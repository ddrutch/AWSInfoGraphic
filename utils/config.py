"""
Configuration management for AWS Infographic Generator.

This module provides centralized configuration management with support
for different environments including testing, development, and production.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .constants import PLATFORM_SPECS, IMAGE_GENERATION_LIMITS


@dataclass
class AWSConfig:
    """AWS service configuration."""
    region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    nova_canvas_model_id: str = "amazon.nova-canvas-v1:0"
    s3_bucket_name: str = ""
    s3_region: Optional[str] = None
    
    def __post_init__(self):
        # Use same region for S3 if not specified
        if self.s3_region is None:
            self.s3_region = self.region


@dataclass
class GenerationConfig:
    """Infographic generation configuration."""
    max_retries: int = 3
    timeout_seconds: int = 60
    fallback_enabled: bool = True
    circuit_breaker_enabled: bool = True
    parallel_processing: bool = False
    cache_enabled: bool = True
    
    # Content analysis settings
    max_key_points: int = 8
    max_text_length: int = 10000
    min_text_length: int = 50
    
    # Image generation settings
    default_image_size: tuple = (512, 512)
    max_image_size: tuple = (2048, 2048)
    image_quality: int = 85
    
    # Layout settings
    default_platform: str = "general"
    auto_platform_optimization: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    structured_logging: bool = True
    log_to_console: bool = True


@dataclass
class TestingConfig:
    """Testing configuration."""
    mock_aws_services: bool = False
    use_local_images: bool = False
    skip_external_calls: bool = False
    test_data_dir: str = "tests/data"
    mock_response_delay: float = 0.1
    enable_performance_tracking: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    validate_inputs: bool = True
    sanitize_outputs: bool = True
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = None
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ["png", "jpg", "jpeg", "gif", "webp"]


class ConfigurationManager:
    """Manages application configuration from multiple sources."""
    
    def __init__(self, config_file: Optional[str] = None, environment: str = "development"):
        self.environment = environment
        self.config_file = config_file
        
        # Initialize default configurations
        self.aws_config = AWSConfig()
        self.generation_config = GenerationConfig()
        self.logging_config = LoggingConfig()
        self.testing_config = TestingConfig()
        self.security_config = SecurityConfig()
        
        # Load configuration from various sources
        self._load_from_environment()
        if config_file:
            self._load_from_file(config_file)
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # AWS Configuration
        if os.getenv("AWS_REGION"):
            self.aws_config.region = os.getenv("AWS_REGION")
        if os.getenv("BEDROCK_MODEL_ID"):
            self.aws_config.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID")
        if os.getenv("NOVA_CANVAS_MODEL_ID"):
            self.aws_config.nova_canvas_model_id = os.getenv("NOVA_CANVAS_MODEL_ID")
        if os.getenv("S3_BUCKET_NAME"):
            self.aws_config.s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        if os.getenv("S3_REGION"):
            self.aws_config.s3_region = os.getenv("S3_REGION")
        
        # Generation Configuration
        if os.getenv("MAX_RETRIES"):
            self.generation_config.max_retries = int(os.getenv("MAX_RETRIES"))
        if os.getenv("TIMEOUT_SECONDS"):
            self.generation_config.timeout_seconds = int(os.getenv("TIMEOUT_SECONDS"))
        if os.getenv("FALLBACK_ENABLED"):
            self.generation_config.fallback_enabled = os.getenv("FALLBACK_ENABLED").lower() == "true"
        if os.getenv("PARALLEL_PROCESSING"):
            self.generation_config.parallel_processing = os.getenv("PARALLEL_PROCESSING").lower() == "true"
        
        # Logging Configuration
        if os.getenv("LOG_LEVEL"):
            self.logging_config.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.logging_config.file_path = os.getenv("LOG_FILE")
        if os.getenv("STRUCTURED_LOGGING"):
            self.logging_config.structured_logging = os.getenv("STRUCTURED_LOGGING").lower() == "true"
        
        # Testing Configuration
        if os.getenv("TESTING"):
            testing_mode = os.getenv("TESTING").lower() == "true"
            self.testing_config.mock_aws_services = testing_mode
            self.testing_config.skip_external_calls = testing_mode
        if os.getenv("MOCK_AWS_SERVICES"):
            self.testing_config.mock_aws_services = os.getenv("MOCK_AWS_SERVICES").lower() == "true"
        if os.getenv("USE_LOCAL_IMAGES"):
            self.testing_config.use_local_images = os.getenv("USE_LOCAL_IMAGES").lower() == "true"
    
    def _load_from_file(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update configurations from file
                if "aws" in config_data:
                    self._update_config_from_dict(self.aws_config, config_data["aws"])
                if "generation" in config_data:
                    self._update_config_from_dict(self.generation_config, config_data["generation"])
                if "logging" in config_data:
                    self._update_config_from_dict(self.logging_config, config_data["logging"])
                if "testing" in config_data:
                    self._update_config_from_dict(self.testing_config, config_data["testing"])
                if "security" in config_data:
                    self._update_config_from_dict(self.security_config, config_data["security"])
        
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _update_config_from_dict(self, config_obj, config_dict: Dict[str, Any]):
        """Update configuration object from dictionary."""
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        if self.environment == "testing":
            # Testing environment overrides
            self.testing_config.mock_aws_services = True
            self.testing_config.skip_external_calls = True
            self.testing_config.use_local_images = True
            self.generation_config.timeout_seconds = 10
            self.generation_config.max_retries = 1
            self.logging_config.level = "DEBUG"
            
        elif self.environment == "development":
            # Development environment overrides
            self.logging_config.level = "DEBUG"
            self.logging_config.log_to_console = True
            self.generation_config.cache_enabled = True
            
        elif self.environment == "production":
            # Production environment overrides
            self.logging_config.level = "INFO"
            self.logging_config.file_path = "/var/log/infographic-generator.log"
            self.security_config.validate_inputs = True
            self.security_config.rate_limit_enabled = True
            self.generation_config.circuit_breaker_enabled = True
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return {
            "environment": self.environment,
            "aws": asdict(self.aws_config),
            "generation": asdict(self.generation_config),
            "logging": asdict(self.logging_config),
            "testing": asdict(self.testing_config),
            "security": asdict(self.security_config),
            "platforms": PLATFORM_SPECS,
            "limits": IMAGE_GENERATION_LIMITS
        }
    
    def get_aws_config(self) -> AWSConfig:
        """Get AWS configuration."""
        return self.aws_config
    
    def get_generation_config(self) -> GenerationConfig:
        """Get generation configuration."""
        return self.generation_config
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self.logging_config
    
    def get_testing_config(self) -> TestingConfig:
        """Get testing configuration."""
        return self.testing_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.security_config
    
    def is_testing_mode(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing" or self.testing_config.mock_aws_services
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    def is_production_mode(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration and return validation results."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate AWS configuration
        if not self.aws_config.s3_bucket_name and not self.is_testing_mode():
            validation_results["errors"].append("S3 bucket name is required for non-testing environments")
            validation_results["valid"] = False
        
        # Validate generation configuration
        if self.generation_config.max_retries < 0:
            validation_results["errors"].append("Max retries cannot be negative")
            validation_results["valid"] = False
        
        if self.generation_config.timeout_seconds <= 0:
            validation_results["errors"].append("Timeout must be positive")
            validation_results["valid"] = False
        
        # Validate security configuration
        if self.security_config.max_file_size <= 0:
            validation_results["errors"].append("Max file size must be positive")
            validation_results["valid"] = False
        
        # Warnings
        if self.is_production_mode() and self.logging_config.level == "DEBUG":
            validation_results["warnings"].append("Debug logging enabled in production")
        
        if not self.security_config.validate_inputs and self.is_production_mode():
            validation_results["warnings"].append("Input validation disabled in production")
        
        return validation_results
    
    def save_config(self, file_path: str):
        """Save current configuration to file."""
        config_data = self.get_all_config()
        
        # Remove non-serializable items
        config_data.pop("platforms", None)
        config_data.pop("limits", None)
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def reload_config(self):
        """Reload configuration from sources."""
        self._load_from_environment()
        if self.config_file:
            self._load_from_file(self.config_file)
        self._apply_environment_overrides()


# Global configuration manager instance
_global_config_manager = None


def get_config_manager(
    config_file: Optional[str] = None,
    environment: Optional[str] = None
) -> ConfigurationManager:
    """Get or create global configuration manager instance."""
    global _global_config_manager
    
    if _global_config_manager is None:
        # Determine environment
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")
        
        # Determine config file
        if config_file is None:
            config_file = os.getenv("CONFIG_FILE")
        
        _global_config_manager = ConfigurationManager(config_file, environment)
    
    return _global_config_manager


def get_aws_config() -> AWSConfig:
    """Get AWS configuration."""
    return get_config_manager().get_aws_config()


def get_generation_config() -> GenerationConfig:
    """Get generation configuration."""
    return get_config_manager().get_generation_config()


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return get_config_manager().get_logging_config()


def get_testing_config() -> TestingConfig:
    """Get testing configuration."""
    return get_config_manager().get_testing_config()


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return get_config_manager().get_security_config()


def is_testing_mode() -> bool:
    """Check if running in testing mode."""
    return get_config_manager().is_testing_mode()


def is_development_mode() -> bool:
    """Check if running in development mode."""
    return get_config_manager().is_development_mode()


def is_production_mode() -> bool:
    """Check if running in production mode."""
    return get_config_manager().is_production_mode()


# Configuration validation decorator
def require_valid_config(func):
    """Decorator to ensure valid configuration before function execution."""
    def wrapper(*args, **kwargs):
        config_manager = get_config_manager()
        validation = config_manager.validate_config()
        
        if not validation["valid"]:
            raise ValueError(f"Invalid configuration: {validation['errors']}")
        
        return func(*args, **kwargs)
    
    return wrapper


# Environment-specific configuration helpers
def create_testing_config() -> ConfigurationManager:
    """Create configuration optimized for testing."""
    return ConfigurationManager(environment="testing")


def create_development_config(config_file: Optional[str] = None) -> ConfigurationManager:
    """Create configuration optimized for development."""
    return ConfigurationManager(config_file=config_file, environment="development")


def create_production_config(config_file: str) -> ConfigurationManager:
    """Create configuration optimized for production."""
    return ConfigurationManager(config_file=config_file, environment="production")