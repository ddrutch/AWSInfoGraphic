"""
Monitoring and logging utilities for AWS Infographic Generator.

This module provides comprehensive monitoring, logging, and alerting
capabilities for tracking system health and performance.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict, deque
import threading
from dataclasses import dataclass, asdict
from enum import Enum

from .error_handling import ErrorCategory, ErrorSeverity, InfographicError


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]


@dataclass
class SystemAlert:
    """System alert data structure."""
    level: AlertLevel
    message: str
    component: str
    timestamp: datetime
    context: Dict[str, Any]
    resolved: bool = False


class PerformanceMonitor:
    """Monitors system performance metrics."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics = defaultdict(lambda: deque(maxlen=window_size))
        self.alerts = deque(maxlen=100)
        self._lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            "response_time": {"warning": 5.0, "error": 10.0, "critical": 30.0},
            "error_rate": {"warning": 0.05, "error": 0.1, "critical": 0.2},
            "memory_usage": {"warning": 0.7, "error": 0.85, "critical": 0.95},
            "cpu_usage": {"warning": 0.8, "error": 0.9, "critical": 0.95}
        }
        
        logger = logging.getLogger(__name__)
        logger.info("Performance monitor initialized")
    
    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None
    ):
        """Record a performance metric."""
        with self._lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            
            self.metrics[name].append(metric)
            
            # Check thresholds and generate alerts
            self._check_thresholds(name, value)
    
    def _check_thresholds(self, metric_name: str, value: float):
        """Check if metric value exceeds thresholds."""
        if metric_name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_name]
        
        if value >= thresholds["critical"]:
            self._create_alert(AlertLevel.CRITICAL, f"{metric_name} critical: {value}", metric_name)
        elif value >= thresholds["error"]:
            self._create_alert(AlertLevel.ERROR, f"{metric_name} error: {value}", metric_name)
        elif value >= thresholds["warning"]:
            self._create_alert(AlertLevel.WARNING, f"{metric_name} warning: {value}", metric_name)
    
    def _create_alert(self, level: AlertLevel, message: str, component: str, context: Optional[Dict[str, Any]] = None):
        """Create a system alert."""
        alert = SystemAlert(
            level=level,
            message=message,
            component=component,
            timestamp=datetime.now(),
            context=context or {}
        )
        
        self.alerts.append(alert)
        
        # Log alert
        logger = logging.getLogger(__name__)
        if level == AlertLevel.CRITICAL:
            logger.critical(f"ALERT: {message}")
        elif level == AlertLevel.ERROR:
            logger.error(f"ALERT: {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"ALERT: {message}")
        else:
            logger.info(f"ALERT: {message}")
    
    def get_metric_stats(self, metric_name: str, time_window: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics for a specific metric."""
        with self._lock:
            if metric_name not in self.metrics:
                return {"error": f"Metric {metric_name} not found"}
            
            metrics = list(self.metrics[metric_name])
            
            # Filter by time window if specified
            if time_window:
                cutoff_time = datetime.now() - timedelta(seconds=time_window)
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            if not metrics:
                return {"error": "No metrics in specified time window"}
            
            values = [m.value for m in metrics]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1],
                "unit": metrics[-1].unit,
                "time_range": {
                    "start": metrics[0].timestamp.isoformat(),
                    "end": metrics[-1].timestamp.isoformat()
                }
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        with self._lock:
            result = {}
            for name in self.metrics:
                result[name] = self.get_metric_stats(name, time_window=300)  # Last 5 minutes
            return result
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts."""
        with self._lock:
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            return [asdict(alert) for alert in active_alerts]
    
    def resolve_alert(self, alert_index: int) -> bool:
        """Mark an alert as resolved."""
        with self._lock:
            if 0 <= alert_index < len(self.alerts):
                self.alerts[alert_index].resolved = True
                return True
            return False


class AgentPerformanceTracker:
    """Tracks performance metrics for individual agents."""
    
    def __init__(self, agent_name: str, monitor: PerformanceMonitor):
        self.agent_name = agent_name
        self.monitor = monitor
        self.operation_counts = defaultdict(int)
        self.operation_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self._lock = threading.Lock()
    
    def track_operation(self, operation_name: str):
        """Context manager to track operation performance."""
        return OperationTracker(self, operation_name)
    
    def record_operation(self, operation_name: str, duration: float, success: bool):
        """Record an operation's performance."""
        with self._lock:
            self.operation_counts[operation_name] += 1
            self.operation_times[operation_name].append(duration)
            
            if not success:
                self.error_counts[operation_name] += 1
        
        # Record metrics
        self.monitor.record_metric(
            f"{self.agent_name}_{operation_name}_duration",
            duration,
            "seconds",
            {"agent": self.agent_name, "operation": operation_name}
        )
        
        # Calculate error rate
        total_ops = self.operation_counts[operation_name]
        error_rate = self.error_counts[operation_name] / total_ops if total_ops > 0 else 0
        
        self.monitor.record_metric(
            f"{self.agent_name}_{operation_name}_error_rate",
            error_rate,
            "ratio",
            {"agent": self.agent_name, "operation": operation_name}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent."""
        with self._lock:
            stats = {
                "agent_name": self.agent_name,
                "operations": {}
            }
            
            for operation in self.operation_counts:
                times = self.operation_times[operation]
                total_ops = self.operation_counts[operation]
                errors = self.error_counts[operation]
                
                stats["operations"][operation] = {
                    "total_count": total_ops,
                    "error_count": errors,
                    "success_rate": (total_ops - errors) / total_ops if total_ops > 0 else 0,
                    "avg_duration": sum(times) / len(times) if times else 0,
                    "min_duration": min(times) if times else 0,
                    "max_duration": max(times) if times else 0
                }
            
            return stats


class OperationTracker:
    """Context manager for tracking individual operations."""
    
    def __init__(self, agent_tracker: AgentPerformanceTracker, operation_name: str):
        self.agent_tracker = agent_tracker
        self.operation_name = operation_name
        self.start_time = None
        self.success = True
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.success = exc_type is None
        
        self.agent_tracker.record_operation(
            self.operation_name,
            duration,
            self.success
        )
    
    def mark_error(self):
        """Mark the operation as failed."""
        self.success = False


class SystemHealthMonitor:
    """Monitors overall system health."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.agent_trackers = {}
        self.system_start_time = datetime.now()
        self._lock = threading.Lock()
        
        logger = logging.getLogger(__name__)
        logger.info("System health monitor initialized")
    
    def get_agent_tracker(self, agent_name: str) -> AgentPerformanceTracker:
        """Get or create an agent performance tracker."""
        with self._lock:
            if agent_name not in self.agent_trackers:
                self.agent_trackers[agent_name] = AgentPerformanceTracker(
                    agent_name, self.performance_monitor
                )
            return self.agent_trackers[agent_name]
    
    def record_system_metric(self, name: str, value: float, unit: str = "", tags: Optional[Dict[str, str]] = None):
        """Record a system-level metric."""
        self.performance_monitor.record_metric(name, value, unit, tags)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health report."""
        uptime = (datetime.now() - self.system_start_time).total_seconds()
        
        health_report = {
            "system_info": {
                "uptime_seconds": uptime,
                "start_time": self.system_start_time.isoformat(),
                "current_time": datetime.now().isoformat()
            },
            "performance_metrics": self.performance_monitor.get_all_metrics(),
            "active_alerts": self.performance_monitor.get_active_alerts(),
            "agent_performance": {}
        }
        
        # Add agent performance stats
        with self._lock:
            for agent_name, tracker in self.agent_trackers.items():
                health_report["agent_performance"][agent_name] = tracker.get_stats()
        
        return health_report
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform system health check and return status."""
        health_report = self.get_system_health()
        
        # Determine overall health status
        active_alerts = health_report["active_alerts"]
        critical_alerts = [a for a in active_alerts if a["level"] == AlertLevel.CRITICAL.value]
        error_alerts = [a for a in active_alerts if a["level"] == AlertLevel.ERROR.value]
        
        if critical_alerts:
            status = "critical"
        elif error_alerts:
            status = "degraded"
        elif len(active_alerts) > 0:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "summary": {
                "total_alerts": len(active_alerts),
                "critical_alerts": len(critical_alerts),
                "error_alerts": len(error_alerts),
                "uptime_hours": health_report["system_info"]["uptime_seconds"] / 3600
            },
            "details": health_report
        }


# Global system health monitor
_global_health_monitor = None


def get_health_monitor() -> SystemHealthMonitor:
    """Get or create global health monitor instance."""
    global _global_health_monitor
    if _global_health_monitor is None:
        _global_health_monitor = SystemHealthMonitor()
    return _global_health_monitor


def track_agent_operation(agent_name: str, operation_name: str):
    """Decorator to track agent operation performance."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = get_health_monitor()
            tracker = monitor.get_agent_tracker(agent_name)
            
            with tracker.track_operation(operation_name) as op_tracker:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    op_tracker.mark_error()
                    raise
        
        return wrapper
    return decorator


def log_structured_event(
    event_type: str,
    message: str,
    level: str = "info",
    **context
):
    """Log a structured event with context."""
    logger = logging.getLogger(__name__)
    
    event_data = {
        "event_type": event_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "context": context
    }
    
    log_message = f"[{event_type}] {message}"
    
    if level == "debug":
        logger.debug(log_message, extra={"event_data": event_data})
    elif level == "info":
        logger.info(log_message, extra={"event_data": event_data})
    elif level == "warning":
        logger.warning(log_message, extra={"event_data": event_data})
    elif level == "error":
        logger.error(log_message, extra={"event_data": event_data})
    elif level == "critical":
        logger.critical(log_message, extra={"event_data": event_data})


class StructuredLogger:
    """Structured logging utility for consistent log formatting."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = logging.getLogger(component_name)
    
    def log_operation_start(self, operation: str, **context):
        """Log the start of an operation."""
        log_structured_event(
            "operation_start",
            f"Starting {operation}",
            level="info",
            component=self.component_name,
            operation=operation,
            **context
        )
    
    def log_operation_success(self, operation: str, duration: float, **context):
        """Log successful operation completion."""
        log_structured_event(
            "operation_success",
            f"Completed {operation} in {duration:.2f}s",
            level="info",
            component=self.component_name,
            operation=operation,
            duration=duration,
            **context
        )
    
    def log_operation_error(self, operation: str, error: Exception, duration: Optional[float] = None, **context):
        """Log operation error."""
        log_structured_event(
            "operation_error",
            f"Failed {operation}: {str(error)}",
            level="error",
            component=self.component_name,
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            duration=duration,
            **context
        )
    
    def log_performance_warning(self, metric: str, value: float, threshold: float, **context):
        """Log performance warning."""
        log_structured_event(
            "performance_warning",
            f"{metric} ({value}) exceeded threshold ({threshold})",
            level="warning",
            component=self.component_name,
            metric=metric,
            value=value,
            threshold=threshold,
            **context
        )
    
    def log_resource_usage(self, resource_type: str, usage: float, **context):
        """Log resource usage."""
        log_structured_event(
            "resource_usage",
            f"{resource_type} usage: {usage}",
            level="info",
            component=self.component_name,
            resource_type=resource_type,
            usage=usage,
            **context
        )


def create_structured_logger(component_name: str) -> StructuredLogger:
    """Create a structured logger for a component."""
    return StructuredLogger(component_name)