"""
Comprehensive error handling utilities for AWS Infographic Generator.

This module provides centralized error handling, retry logic, circuit breaker patterns,
and fallback mechanisms for all AWS agents and tools.
"""

import asyncio
import functools
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type, Union
from enum import Enum
import traceback
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for categorization and handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for specific handling strategies."""
    NETWORK = "network"
    AWS_SERVICE = "aws_service"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    PROCESSING = "processing"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class ErrorHandlingConfig:
    """Configuration for error handling behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        circuit_breaker_enabled: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
        fallback_enabled: bool = True,
        logging_enabled: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.circuit_breaker_enabled = circuit_breaker_enabled
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.fallback_enabled = fallback_enabled
        self.logging_enabled = logging_enabled


class InfographicError(Exception):
    """Base exception for infographic generation errors."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.retry_strategy = retry_strategy
        self.context = context or {}
        self.original_error = original_error
        self.timestamp = datetime.now()


class AWSServiceError(InfographicError):
    """AWS service-specific errors."""
    
    def __init__(self, message: str, service_name: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AWS_SERVICE,
            **kwargs
        )
        self.service_name = service_name


class NetworkError(InfographicError):
    """Network-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            **kwargs
        )


class RateLimitError(InfographicError):
    """Rate limiting errors."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RATE_LIMIT,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            **kwargs
        )
        self.retry_after = retry_after


class ValidationError(InfographicError):
    """Input validation errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            retry_strategy=RetryStrategy.NO_RETRY,
            **kwargs
        )


class ProcessingError(InfographicError):
    """Content processing errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            **kwargs
        )


class TimeoutError(InfographicError):
    """Timeout errors."""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.TIMEOUT,
            **kwargs
        )
        self.timeout_duration = timeout_duration


class CircuitBreaker:
    """Circuit breaker implementation for preventing cascade failures."""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function."""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self._call_with_circuit_breaker(func, *args, **kwargs)
        
        return wrapper
    
    def _call_with_circuit_breaker(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker logic."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN")
                else:
                    raise InfographicError(
                        f"Circuit breaker '{self.name}' is OPEN",
                        category=ErrorCategory.RESOURCE,
                        severity=ErrorSeverity.HIGH
                    )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation."""
        with self._lock:
            self.failure_count = 0
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info(f"Circuit breaker '{self.name}' reset to CLOSED")
    
    def _on_failure(self):
        """Handle failed operation."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class RetryHandler:
    """Handles retry logic with various strategies."""
    
    def __init__(self, config: ErrorHandlingConfig):
        self.config = config
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to add retry logic to a function."""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self._execute_with_retry(func, *args, **kwargs)
        
        return wrapper
    
    def _execute_with_retry(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except InfographicError as e:
                last_exception = e
                
                # Don't retry validation errors or no-retry strategies
                if e.retry_strategy == RetryStrategy.NO_RETRY:
                    raise
                
                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt, e.retry_strategy)
                    
                    if self.config.logging_enabled:
                        logger.warning(
                            f"Attempt {attempt + 1}/{self.config.max_retries + 1} failed: {str(e)}. "
                            f"Retrying in {delay:.2f}s"
                        )
                    
                    time.sleep(delay)
                else:
                    if self.config.logging_enabled:
                        logger.error(f"All retry attempts failed. Last error: {str(e)}")
                    raise
                    
            except Exception as e:
                # Wrap unexpected exceptions
                wrapped_error = InfographicError(
                    f"Unexpected error: {str(e)}",
                    category=ErrorCategory.UNKNOWN,
                    original_error=e
                )
                last_exception = wrapped_error
                
                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt, RetryStrategy.EXPONENTIAL_BACKOFF)
                    
                    if self.config.logging_enabled:
                        logger.warning(
                            f"Attempt {attempt + 1}/{self.config.max_retries + 1} failed with unexpected error: {str(e)}. "
                            f"Retrying in {delay:.2f}s"
                        )
                    
                    time.sleep(delay)
                else:
                    if self.config.logging_enabled:
                        logger.error(f"All retry attempts failed. Last error: {str(e)}")
                    raise wrapped_error
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int, strategy: RetryStrategy) -> float:
        """Calculate delay for retry attempt."""
        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
        elif strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        else:
            delay = 0
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter and delay > 0:
            import random
            jitter_amount = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)


class ErrorMetrics:
    """Collects and tracks error metrics."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.errors = deque(maxlen=window_size)
        self.error_counts = defaultdict(int)
        self.category_counts = defaultdict(int)
        self.severity_counts = defaultdict(int)
        self._lock = threading.Lock()
    
    def record_error(self, error: InfographicError):
        """Record an error for metrics tracking."""
        with self._lock:
            error_record = {
                "timestamp": error.timestamp,
                "message": error.message,
                "category": error.category.value,
                "severity": error.severity.value,
                "context": error.context
            }
            
            self.errors.append(error_record)
            self.error_counts[error.message] += 1
            self.category_counts[error.category.value] += 1
            self.severity_counts[error.severity.value] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current error metrics."""
        with self._lock:
            total_errors = len(self.errors)
            
            # Calculate error rate over time windows
            now = datetime.now()
            recent_errors = [
                e for e in self.errors
                if (now - e["timestamp"]).total_seconds() <= 300  # Last 5 minutes
            ]
            
            return {
                "total_errors": total_errors,
                "recent_errors_5min": len(recent_errors),
                "error_rate_5min": len(recent_errors) / 5.0,  # Errors per minute
                "category_distribution": dict(self.category_counts),
                "severity_distribution": dict(self.severity_counts),
                "most_common_errors": dict(list(self.error_counts.items())[:10]),
                "window_size": self.window_size
            }
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        with self._lock:
            self.errors.clear()
            self.error_counts.clear()
            self.category_counts.clear()
            self.severity_counts.clear()


class FallbackManager:
    """Manages fallback strategies for different types of failures."""
    
    def __init__(self):
        self.fallback_strategies = {}
        self.fallback_history = deque(maxlen=100)
    
    def register_fallback(
        self,
        error_category: ErrorCategory,
        fallback_func: Callable,
        priority: int = 0
    ):
        """Register a fallback strategy for an error category."""
        if error_category not in self.fallback_strategies:
            self.fallback_strategies[error_category] = []
        
        self.fallback_strategies[error_category].append({
            "function": fallback_func,
            "priority": priority
        })
        
        # Sort by priority (higher priority first)
        self.fallback_strategies[error_category].sort(
            key=lambda x: x["priority"],
            reverse=True
        )
        
        logger.info(f"Registered fallback for {error_category.value} with priority {priority}")
    
    def execute_fallback(
        self,
        error: InfographicError,
        *args,
        **kwargs
    ) -> Any:
        """Execute appropriate fallback strategy for an error."""
        fallbacks = self.fallback_strategies.get(error.category, [])
        
        if not fallbacks:
            logger.warning(f"No fallback strategy available for {error.category.value}")
            raise error
        
        for fallback in fallbacks:
            try:
                logger.info(f"Attempting fallback for {error.category.value}")
                
                result = fallback["function"](error, *args, **kwargs)
                
                # Record successful fallback
                self.fallback_history.append({
                    "timestamp": datetime.now(),
                    "error_category": error.category.value,
                    "fallback_priority": fallback["priority"],
                    "success": True
                })
                
                logger.info(f"Fallback successful for {error.category.value}")
                return result
                
            except Exception as fallback_error:
                logger.warning(
                    f"Fallback failed for {error.category.value}: {str(fallback_error)}"
                )
                
                # Record failed fallback
                self.fallback_history.append({
                    "timestamp": datetime.now(),
                    "error_category": error.category.value,
                    "fallback_priority": fallback["priority"],
                    "success": False,
                    "error": str(fallback_error)
                })
                
                continue
        
        # All fallbacks failed
        logger.error(f"All fallbacks failed for {error.category.value}")
        raise error
    
    def get_fallback_metrics(self) -> Dict[str, Any]:
        """Get fallback execution metrics."""
        total_attempts = len(self.fallback_history)
        successful_attempts = sum(1 for h in self.fallback_history if h["success"])
        
        category_stats = defaultdict(lambda: {"total": 0, "successful": 0})
        for history in self.fallback_history:
            category = history["error_category"]
            category_stats[category]["total"] += 1
            if history["success"]:
                category_stats[category]["successful"] += 1
        
        return {
            "total_fallback_attempts": total_attempts,
            "successful_fallbacks": successful_attempts,
            "fallback_success_rate": successful_attempts / total_attempts if total_attempts > 0 else 0,
            "category_stats": dict(category_stats),
            "registered_strategies": {
                category.value: len(strategies)
                for category, strategies in self.fallback_strategies.items()
            }
        }


class ErrorHandler:
    """Main error handling coordinator."""
    
    def __init__(self, config: Optional[ErrorHandlingConfig] = None):
        self.config = config or ErrorHandlingConfig()
        self.retry_handler = RetryHandler(self.config)
        self.circuit_breakers = {}
        self.error_metrics = ErrorMetrics()
        self.fallback_manager = FallbackManager()
        
        logger.info("Error handler initialized with comprehensive error handling")
    
    def with_error_handling(
        self,
        circuit_breaker_name: Optional[str] = None,
        fallback_category: Optional[ErrorCategory] = None
    ):
        """Decorator that applies comprehensive error handling."""
        
        def decorator(func: Callable) -> Callable:
            # Apply retry logic
            func = self.retry_handler(func)
            
            # Apply circuit breaker if specified
            if circuit_breaker_name and self.config.circuit_breaker_enabled:
                if circuit_breaker_name not in self.circuit_breakers:
                    self.circuit_breakers[circuit_breaker_name] = CircuitBreaker(
                        name=circuit_breaker_name,
                        failure_threshold=self.config.circuit_breaker_threshold,
                        recovery_timeout=self.config.circuit_breaker_timeout
                    )
                
                func = self.circuit_breakers[circuit_breaker_name](func)
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                    
                except InfographicError as e:
                    # Record error metrics
                    self.error_metrics.record_error(e)
                    
                    # Try fallback if enabled and available
                    if (self.config.fallback_enabled and 
                        fallback_category and 
                        e.category == fallback_category):
                        try:
                            return self.fallback_manager.execute_fallback(e, *args, **kwargs)
                        except Exception:
                            pass  # Fallback failed, re-raise original error
                    
                    raise
                    
                except Exception as e:
                    # Wrap and handle unexpected errors
                    wrapped_error = InfographicError(
                        f"Unexpected error in {func.__name__}: {str(e)}",
                        category=ErrorCategory.UNKNOWN,
                        original_error=e,
                        context={"function": func.__name__, "args": str(args)[:200]}
                    )
                    
                    self.error_metrics.record_error(wrapped_error)
                    raise wrapped_error
            
            return wrapper
        
        return decorator
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers."""
        return {
            name: breaker.get_state()
            for name, breaker in self.circuit_breakers.items()
        }
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive error handling metrics."""
        return {
            "error_metrics": self.error_metrics.get_metrics(),
            "fallback_metrics": self.fallback_manager.get_fallback_metrics(),
            "circuit_breaker_status": self.get_circuit_breaker_status(),
            "config": {
                "max_retries": self.config.max_retries,
                "circuit_breaker_enabled": self.config.circuit_breaker_enabled,
                "fallback_enabled": self.config.fallback_enabled
            }
        }


# Global error handler instance
_global_error_handler = None


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def with_error_handling(
    circuit_breaker_name: Optional[str] = None,
    fallback_category: Optional[ErrorCategory] = None
):
    """Convenience decorator for applying error handling."""
    return get_error_handler().with_error_handling(
        circuit_breaker_name=circuit_breaker_name,
        fallback_category=fallback_category
    )


# Utility functions for common error scenarios
def handle_aws_service_error(service_name: str, original_error: Exception) -> AWSServiceError:
    """Convert AWS service errors to standardized format."""
    error_message = str(original_error)
    
    # Categorize AWS errors
    if "ThrottlingException" in error_message or "TooManyRequestsException" in error_message:
        return RateLimitError(
            f"{service_name} rate limit exceeded: {error_message}",
            context={"service": service_name}
        )
    elif "AccessDeniedException" in error_message or "UnauthorizedOperation" in error_message:
        return AWSServiceError(
            f"{service_name} access denied: {error_message}",
            service_name=service_name,
            category=ErrorCategory.AUTHENTICATION,
            retry_strategy=RetryStrategy.NO_RETRY
        )
    elif "ValidationException" in error_message:
        return ValidationError(
            f"{service_name} validation error: {error_message}",
            context={"service": service_name}
        )
    elif "TimeoutError" in error_message or "timeout" in error_message.lower():
        return TimeoutError(
            f"{service_name} timeout: {error_message}",
            context={"service": service_name}
        )
    else:
        return AWSServiceError(
            f"{service_name} error: {error_message}",
            service_name=service_name,
            original_error=original_error
        )


def handle_network_error(original_error: Exception) -> NetworkError:
    """Convert network errors to standardized format."""
    return NetworkError(
        f"Network error: {str(original_error)}",
        original_error=original_error
    )


def log_error_context(error: InfographicError, additional_context: Optional[Dict[str, Any]] = None):
    """Log error with full context information."""
    context = {
        "error_type": type(error).__name__,
        "category": error.category.value,
        "severity": error.severity.value,
        "retry_strategy": error.retry_strategy.value,
        "timestamp": error.timestamp.isoformat(),
        "original_error": str(error.original_error) if error.original_error else None,
        **error.context
    }
    
    if additional_context:
        context.update(additional_context)
    
    logger.error(f"Error occurred: {error.message}", extra={"error_context": context})
    
    # Also log stack trace for debugging
    if error.original_error:
        logger.debug("Original error traceback:", exc_info=error.original_error)


# Fallback strategies for different agent types
def content_analysis_fallback(error: InfographicError, text: str, *args, **kwargs) -> Dict[str, Any]:
    """Fallback strategy for content analysis failures."""
    logger.info("Executing content analysis fallback")
    
    try:
        # Basic text processing fallback
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # Extract basic key points (first few sentences)
        key_points = sentences[:5] if len(sentences) >= 5 else sentences
        
        # Generate basic title from first sentence or first 50 chars
        title = sentences[0][:50] if sentences else text[:50]
        
        # Basic summary
        summary = f"Key information about {title.lower()}"
        
        fallback_analysis = {
            "main_topic": title,
            "key_points": key_points,
            "summary": summary,
            "suggested_title": title,
            "hierarchy": {"sections": [], "flow_direction": "top-to-bottom"},
            "content_structure": {"fallback": True, "method": "basic_text_processing"}
        }
        
        logger.info("Content analysis fallback completed successfully")
        return {
            "success": True,
            "data": {"structured_analysis": fallback_analysis},
            "fallback": True,
            "fallback_method": "basic_text_processing"
        }
        
    except Exception as fallback_error:
        logger.error(f"Content analysis fallback failed: {str(fallback_error)}")
        raise ProcessingError(f"Content analysis fallback failed: {str(fallback_error)}")


def image_generation_fallback(error: InfographicError, prompt: str, image_id: str, *args, **kwargs) -> Dict[str, Any]:
    """Fallback strategy for image generation failures."""
    logger.info("Executing image generation fallback")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        import os
        
        # Create a simple placeholder image
        width, height = kwargs.get('dimensions', (512, 512))
        
        # Create image with gradient background
        image = Image.new('RGB', (width, height), '#f0f0f0')
        draw = ImageDraw.Draw(image)
        
        # Add gradient effect
        for y in range(height):
            color_value = int(240 - (y / height) * 40)  # Gradient from light to darker
            color = f"#{color_value:02x}{color_value:02x}{color_value:02x}"
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add text
        try:
            font_size = min(width, height) // 15
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()
        
        # Wrap and center text
        text_lines = []
        words = prompt.split()[:10]  # Limit words
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= 30:  # Character limit per line
                current_line.append(word)
            else:
                if current_line:
                    text_lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            text_lines.append(' '.join(current_line))
        
        # Draw text lines
        text_height = len(text_lines) * 30
        start_y = (height - text_height) // 2
        
        for i, line in enumerate(text_lines[:5]):  # Max 5 lines
            text_width = draw.textlength(line, font=font) if hasattr(draw, 'textlength') else len(line) * 10
            x = (width - text_width) // 2
            y = start_y + i * 30
            draw.text((x, y), line, fill='#333333', font=font)
        
        # Add decorative border
        border_color = '#cccccc'
        draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=3)
        
        # Add corner decorations
        corner_size = 20
        draw.rectangle([10, 10, corner_size, corner_size], fill='#4a90e2')
        draw.rectangle([width-corner_size-10, 10, width-10, corner_size], fill='#4a90e2')
        draw.rectangle([10, height-corner_size-10, corner_size, height-10], fill='#4a90e2')
        draw.rectangle([width-corner_size-10, height-corner_size-10, width-10, height-10], fill='#4a90e2')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file.name, "PNG")
            temp_path = tmp_file.name
        
        # Create ImageAsset-like structure
        fallback_image = {
            "url": f"file://{temp_path}",
            "type": "fallback_placeholder",
            "source": "fallback",
            "description": f"Fallback image for: {prompt[:50]}"
        }
        
        logger.info("Image generation fallback completed successfully")
        return {
            "success": True,
            "image_asset": fallback_image,
            "fallback": True,
            "fallback_method": "enhanced_placeholder"
        }
        
    except Exception as fallback_error:
        logger.error(f"Image generation fallback failed: {str(fallback_error)}")
        
        # Ultimate fallback - return a simple data structure
        return {
            "success": True,
            "image_asset": {
                "url": None,
                "type": "fallback_failed",
                "source": "fallback",
                "description": f"Fallback failed for: {prompt[:50]}"
            },
            "fallback": True,
            "fallback_method": "minimal_fallback"
        }


def layout_design_fallback(error: InfographicError, content_elements: List[Dict], platform: str, *args, **kwargs) -> Dict[str, Any]:
    """Fallback strategy for layout design failures."""
    logger.info("Executing layout design fallback")
    
    try:
        # Platform-specific dimensions
        platform_dimensions = {
            "whatsapp": (1080, 1080),
            "twitter": (1200, 675),
            "discord": (1920, 1080),
            "reddit": (1080, 1080),
            "general": (1920, 1080)
        }
        
        canvas_size = platform_dimensions.get(platform.lower(), (1920, 1080))
        
        # Create simple grid layout
        elements = []
        y_position = 50
        
        for i, element in enumerate(content_elements[:10]):  # Limit elements
            element_height = 80 if element.get('type') == 'text' else 200
            
            layout_element = {
                "element_type": element.get('type', 'text'),
                "position": (50, y_position),
                "size": (canvas_size[0] - 100, element_height),
                "content": element.get('content', ''),
                "styling": {
                    "font_size": 24 if element.get('element_type') == 'title' else 16,
                    "color": "#333333",
                    "alignment": "left"
                }
            }
            
            elements.append(layout_element)
            y_position += element_height + 20
            
            # Prevent overflow
            if y_position > canvas_size[1] - 100:
                break
        
        fallback_layout = {
            "canvas_size": canvas_size,
            "elements": elements,
            "color_scheme": {"primary": "#4a90e2", "secondary": "#f0f0f0", "text": "#333333"},
            "platform_optimizations": {"platform": platform}
        }
        
        logger.info("Layout design fallback completed successfully")
        return {
            "success": True,
            "data": {"layout_specification": fallback_layout},
            "fallback": True,
            "fallback_method": "simple_grid_layout"
        }
        
    except Exception as fallback_error:
        logger.error(f"Layout design fallback failed: {str(fallback_error)}")
        raise ProcessingError(f"Layout design fallback failed: {str(fallback_error)}")


def text_formatting_fallback(error: InfographicError, content: str, platform: str, *args, **kwargs) -> Dict[str, Any]:
    """Fallback strategy for text formatting failures."""
    logger.info("Executing text formatting fallback")
    
    try:
        # Basic text formatting
        lines = content.split('\n')
        formatted_elements = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            # Determine element type based on position and content
            if i == 0:
                element_type = "title"
                font_size = 32
            elif line.startswith('•') or line.startswith('-'):
                element_type = "bullet_point"
                font_size = 18
            else:
                element_type = "body_text"
                font_size = 20
            
            formatted_element = {
                "text": line.strip(),
                "type": element_type,
                "font_size": font_size,
                "color": "#333333",
                "font_family": "Arial",
                "alignment": "left",
                "line_height": 1.2
            }
            
            formatted_elements.append(formatted_element)
        
        fallback_formatting = {
            "formatted_elements": formatted_elements,
            "global_styles": {
                "font_family": "Arial",
                "color_scheme": {"primary": "#333333", "accent": "#4a90e2"}
            }
        }
        
        logger.info("Text formatting fallback completed successfully")
        return {
            "success": True,
            "data": fallback_formatting,
            "fallback": True,
            "fallback_method": "basic_text_formatting"
        }
        
    except Exception as fallback_error:
        logger.error(f"Text formatting fallback failed: {str(fallback_error)}")
        raise ProcessingError(f"Text formatting fallback failed: {str(fallback_error)}")


def image_composition_fallback(error: InfographicError, layout_spec: Dict, content_elements: Dict, platform: str, *args, **kwargs) -> Dict[str, Any]:
    """Fallback strategy for image composition failures."""
    logger.info("Executing image composition fallback")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        # Get canvas size from layout or use default
        canvas_size = layout_spec.get('canvas_size', (1920, 1080))
        
        # Create base image
        image = Image.new('RGB', canvas_size, '#ffffff')
        draw = ImageDraw.Draw(image)
        
        # Add background gradient
        for y in range(canvas_size[1]):
            alpha = y / canvas_size[1]
            color_value = int(255 - alpha * 20)  # Subtle gradient
            color = (color_value, color_value, color_value)
            draw.line([(0, y), (canvas_size[0], y)], fill=color)
        
        # Add text elements
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            body_font = ImageFont.truetype("arial.ttf", 20)
        except (OSError, IOError):
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        y_position = 50
        
        # Process text elements
        text_elements = content_elements.get('text_elements', [])
        for element in text_elements:
            text = element.get('text', '')
            element_type = element.get('type', 'body')
            
            if element_type == 'title':
                font = title_font
                color = '#2c3e50'
            else:
                font = body_font
                color = '#34495e'
            
            # Word wrap
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                text_width = draw.textlength(test_line, font=font) if hasattr(draw, 'textlength') else len(test_line) * 10
                
                if text_width <= canvas_size[0] - 100:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text lines
            for line in lines:
                draw.text((50, y_position), line, fill=color, font=font)
                y_position += 40 if element_type == 'title' else 30
            
            y_position += 20  # Space between elements
        
        # Add decorative elements
        # Header bar
        draw.rectangle([0, 0, canvas_size[0], 10], fill='#3498db')
        
        # Footer bar
        draw.rectangle([0, canvas_size[1]-10, canvas_size[0], canvas_size[1]], fill='#3498db')
        
        # Side accent
        draw.rectangle([0, 0, 5, canvas_size[1]], fill='#e74c3c')
        
        # Save image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            image.save(tmp_file.name, "PNG", quality=90)
            temp_path = tmp_file.name
        
        fallback_result = {
            "image_path": temp_path,
            "s3_url": f"file://{temp_path}",
            "metadata": {
                "platform": platform,
                "canvas_size": canvas_size,
                "fallback": True,
                "method": "basic_composition"
            },
            "platform_variants": {platform: f"file://{temp_path}"}
        }
        
        logger.info("Image composition fallback completed successfully")
        return {
            "success": True,
            "data": fallback_result,
            "fallback": True,
            "fallback_method": "basic_image_composition"
        }
        
    except Exception as fallback_error:
        logger.error(f"Image composition fallback failed: {str(fallback_error)}")
        raise ProcessingError(f"Image composition fallback failed: {str(fallback_error)}")


# Register fallback strategies with the global error handler
def register_fallback_strategies():
    """Register all fallback strategies with the global error handler."""
    error_handler = get_error_handler()
    
    # Register fallback strategies
    error_handler.fallback_manager.register_fallback(
        ErrorCategory.PROCESSING, content_analysis_fallback, priority=10
    )
    
    error_handler.fallback_manager.register_fallback(
        ErrorCategory.AWS_SERVICE, image_generation_fallback, priority=10
    )
    
    error_handler.fallback_manager.register_fallback(
        ErrorCategory.PROCESSING, layout_design_fallback, priority=8
    )
    
    error_handler.fallback_manager.register_fallback(
        ErrorCategory.PROCESSING, text_formatting_fallback, priority=8
    )
    
    error_handler.fallback_manager.register_fallback(
        ErrorCategory.PROCESSING, image_composition_fallback, priority=8
    )
    
    logger.info("All fallback strategies registered successfully")


# Initialize fallback strategies when module is imported
register_fallback_strategies()