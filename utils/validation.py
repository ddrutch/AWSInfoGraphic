"""
Validation utilities for AWS Infographic Generator.

This module provides comprehensive validation functions for inputs, outputs,
and system state that support both runtime validation and testing scenarios.
"""

import re
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
import mimetypes

from .types import AnalyzedContent, ImageAsset, LayoutSpec, AgentResponse
from .constants import PLATFORM_SPECS, IMAGE_GENERATION_LIMITS
from .error_handling import ValidationError, InfographicError


class InputValidator:
    """Validates user inputs and system inputs."""
    
    @staticmethod
    def validate_text_input(text: str, min_length: int = 10, max_length: int = 10000) -> Dict[str, Any]:
        """Validate text input for content analysis."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        # Check if text exists
        if not text or not isinstance(text, str):
            validation_result["valid"] = False
            validation_result["errors"].append("Text input is required and must be a string")
            return validation_result
        
        # Clean and check length
        cleaned_text = text.strip()
        text_length = len(cleaned_text)
        
        validation_result["metadata"]["original_length"] = len(text)
        validation_result["metadata"]["cleaned_length"] = text_length
        validation_result["metadata"]["word_count"] = len(cleaned_text.split())
        
        if text_length < min_length:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Text too short. Minimum {min_length} characters required, got {text_length}")
        
        if text_length > max_length:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Text too long. Maximum {max_length} characters allowed, got {text_length}")
        
        # Check for suspicious content
        if re.search(r'<script|javascript:|data:', cleaned_text, re.IGNORECASE):
            validation_result["warnings"].append("Text contains potentially unsafe content")
        
        # Check encoding
        try:
            cleaned_text.encode('utf-8')
        except UnicodeEncodeError:
            validation_result["warnings"].append("Text contains non-UTF-8 characters")
        
        # Check for reasonable content structure
        sentences = re.split(r'[.!?]+', cleaned_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        validation_result["metadata"]["sentence_count"] = len(sentences)
        
        if len(sentences) < 1:
            validation_result["warnings"].append("Text appears to lack sentence structure")
        
        return validation_result
    
    @staticmethod
    def validate_platform_input(platform: str) -> Dict[str, Any]:
        """Validate platform specification."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        if not platform or not isinstance(platform, str):
            validation_result["valid"] = False
            validation_result["errors"].append("Platform must be a non-empty string")
            return validation_result
        
        platform = platform.lower().strip()
        validation_result["metadata"]["normalized_platform"] = platform
        
        if platform not in PLATFORM_SPECS:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Unsupported platform: {platform}")
            validation_result["metadata"]["supported_platforms"] = list(PLATFORM_SPECS.keys())
        else:
            validation_result["metadata"]["platform_specs"] = PLATFORM_SPECS[platform]
        
        return validation_result
    
    @staticmethod
    def validate_image_dimensions(dimensions: Tuple[int, int]) -> Dict[str, Any]:
        """Validate image dimensions."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        if not dimensions or len(dimensions) != 2:
            validation_result["valid"] = False
            validation_result["errors"].append("Dimensions must be a tuple of (width, height)")
            return validation_result
        
        width, height = dimensions
        validation_result["metadata"]["width"] = width
        validation_result["metadata"]["height"] = height
        validation_result["metadata"]["aspect_ratio"] = width / height if height > 0 else 0
        validation_result["metadata"]["total_pixels"] = width * height
        
        # Check if dimensions are positive integers
        if not isinstance(width, int) or not isinstance(height, int):
            validation_result["valid"] = False
            validation_result["errors"].append("Dimensions must be integers")
        
        if width <= 0 or height <= 0:
            validation_result["valid"] = False
            validation_result["errors"].append("Dimensions must be positive")
        
        # Check reasonable limits
        min_dimension = 64
        max_dimension = 4096
        
        if width < min_dimension or height < min_dimension:
            validation_result["warnings"].append(f"Dimensions below recommended minimum of {min_dimension}px")
        
        if width > max_dimension or height > max_dimension:
            validation_result["warnings"].append(f"Dimensions above recommended maximum of {max_dimension}px")
        
        # Check aspect ratio
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio > 10 or aspect_ratio < 0.1:
            validation_result["warnings"].append("Extreme aspect ratio may cause layout issues")
        
        return validation_result
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate file path and extension."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        if not file_path or not isinstance(file_path, str):
            validation_result["valid"] = False
            validation_result["errors"].append("File path must be a non-empty string")
            return validation_result
        
        path = Path(file_path)
        validation_result["metadata"]["absolute_path"] = str(path.resolve())
        validation_result["metadata"]["extension"] = path.suffix.lower()
        validation_result["metadata"]["filename"] = path.name
        validation_result["metadata"]["exists"] = path.exists()
        
        # Check extension
        if allowed_extensions:
            extension = path.suffix.lower().lstrip('.')
            if extension not in allowed_extensions:
                validation_result["valid"] = False
                validation_result["errors"].append(f"File extension '{extension}' not allowed. Allowed: {allowed_extensions}")
        
        # Check if file exists (for reading)
        if path.exists():
            validation_result["metadata"]["size_bytes"] = path.stat().st_size
            validation_result["metadata"]["is_file"] = path.is_file()
            validation_result["metadata"]["is_readable"] = os.access(path, os.R_OK)
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            validation_result["metadata"]["mime_type"] = mime_type
        
        return validation_result


class OutputValidator:
    """Validates system outputs and generated content."""
    
    @staticmethod
    def validate_content_analysis(analysis: AnalyzedContent) -> Dict[str, Any]:
        """Validate ContentAnalysis output."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        # Check required fields
        if not analysis.main_topic:
            validation_result["valid"] = False
            validation_result["errors"].append("Main topic is required")
        elif len(analysis.main_topic.strip()) == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("Main topic cannot be empty")
        
        if not analysis.key_points:
            validation_result["valid"] = False
            validation_result["errors"].append("Key points are required")
        elif not isinstance(analysis.key_points, list):
            validation_result["valid"] = False
            validation_result["errors"].append("Key points must be a list")
        
        if not analysis.summary:
            validation_result["valid"] = False
            validation_result["errors"].append("Summary is required")
        
        if not analysis.suggested_title:
            validation_result["valid"] = False
            validation_result["errors"].append("Suggested title is required")
        
        # Validate content quality
        if analysis.main_topic and len(analysis.main_topic) > 100:
            validation_result["warnings"].append("Main topic is very long")
        
        if analysis.key_points:
            validation_result["metadata"]["key_points_count"] = len(analysis.key_points)
            
            for i, point in enumerate(analysis.key_points):
                if not isinstance(point, str):
                    validation_result["errors"].append(f"Key point {i+1} must be a string")
                elif len(point.strip()) == 0:
                    validation_result["warnings"].append(f"Key point {i+1} is empty")
                elif len(point) > 150:
                    validation_result["warnings"].append(f"Key point {i+1} is very long")
        
        if analysis.suggested_title and len(analysis.suggested_title) > 80:
            validation_result["warnings"].append("Suggested title is very long")
        
        if analysis.summary and len(analysis.summary) > 500:
            validation_result["warnings"].append("Summary is very long")
        
        # Validate hierarchy structure
        if analysis.hierarchy:
            if not isinstance(analysis.hierarchy, dict):
                validation_result["errors"].append("Hierarchy must be a dictionary")
            else:
                validation_result["metadata"]["hierarchy_keys"] = list(analysis.hierarchy.keys())
        
        return validation_result
    
    @staticmethod
    def validate_image_asset(asset: ImageAsset) -> Dict[str, Any]:
        """Validate ImageAsset output."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        # Check required fields
        if not asset.description:
            validation_result["valid"] = False
            validation_result["errors"].append("Image description is required")
        
        if not asset.dimensions or len(asset.dimensions) != 2:
            validation_result["valid"] = False
            validation_result["errors"].append("Image dimensions are required")
        else:
            width, height = asset.dimensions
            validation_result["metadata"]["width"] = width
            validation_result["metadata"]["height"] = height
            validation_result["metadata"]["aspect_ratio"] = width / height if height > 0 else 0
        
        if not asset.asset_type:
            validation_result["valid"] = False
            validation_result["errors"].append("Asset type is required")
        elif asset.asset_type not in ["stock", "generated", "placeholder"]:
            validation_result["valid"] = False
            validation_result["errors"].append("Invalid asset type")
        
        # Check that at least one source is available
        if not asset.url and not asset.local_path:
            validation_result["valid"] = False
            validation_result["errors"].append("Either URL or local path must be provided")
        
        # Validate URL format if provided
        if asset.url:
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(asset.url):
                validation_result["warnings"].append("URL format appears invalid")
        
        # Validate local path if provided
        if asset.local_path:
            path_validation = InputValidator.validate_file_path(
                asset.local_path,
                allowed_extensions=["png", "jpg", "jpeg", "gif", "webp"]
            )
            if not path_validation["valid"]:
                validation_result["warnings"].append("Local path validation failed")
        
        return validation_result
    
    @staticmethod
    def validate_layout_specification(layout: LayoutSpecification) -> Dict[str, Any]:
        """Validate LayoutSpecification output."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        # Check canvas size
        if not layout.canvas_size or len(layout.canvas_size) != 2:
            validation_result["valid"] = False
            validation_result["errors"].append("Canvas size is required")
        else:
            width, height = layout.canvas_size
            validation_result["metadata"]["canvas_width"] = width
            validation_result["metadata"]["canvas_height"] = height
            
            if width <= 0 or height <= 0:
                validation_result["valid"] = False
                validation_result["errors"].append("Canvas dimensions must be positive")
        
        # Check elements
        if layout.elements is None:
            validation_result["valid"] = False
            validation_result["errors"].append("Elements list is required")
        elif not isinstance(layout.elements, list):
            validation_result["valid"] = False
            validation_result["errors"].append("Elements must be a list")
        else:
            validation_result["metadata"]["element_count"] = len(layout.elements)
            
            for i, element in enumerate(layout.elements):
                if not hasattr(element, 'element_type'):
                    validation_result["errors"].append(f"Element {i+1} missing element_type")
                if not hasattr(element, 'position'):
                    validation_result["errors"].append(f"Element {i+1} missing position")
                if not hasattr(element, 'size'):
                    validation_result["errors"].append(f"Element {i+1} missing size")
        
        # Check color scheme
        if layout.color_scheme:
            if not isinstance(layout.color_scheme, dict):
                validation_result["warnings"].append("Color scheme should be a dictionary")
            else:
                validation_result["metadata"]["color_scheme_keys"] = list(layout.color_scheme.keys())
        
        return validation_result
    
    @staticmethod
    def validate_agent_response(response: AgentResponse) -> Dict[str, Any]:
        """Validate AgentResponse output."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        # Check required fields
        if not hasattr(response, 'success'):
            validation_result["valid"] = False
            validation_result["errors"].append("Success field is required")
        
        validation_result["metadata"]["success"] = response.success
        
        # Check consistency
        if response.success:
            if not response.data:
                validation_result["warnings"].append("Successful response should have data")
            if response.error_message:
                validation_result["warnings"].append("Successful response should not have error message")
        else:
            if not response.error_message:
                validation_result["warnings"].append("Failed response should have error message")
        
        # Check data structure
        if response.data is not None:
            validation_result["metadata"]["data_type"] = type(response.data).__name__
            if isinstance(response.data, dict):
                validation_result["metadata"]["data_keys"] = list(response.data.keys())
        
        # Check metadata
        if response.metadata is not None:
            validation_result["metadata"]["has_metadata"] = True
            if isinstance(response.metadata, dict):
                validation_result["metadata"]["metadata_keys"] = list(response.metadata.keys())
        
        return validation_result


class SystemValidator:
    """Validates system state and configuration."""
    
    @staticmethod
    def validate_aws_credentials() -> Dict[str, Any]:
        """Validate AWS credentials and permissions."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        import os
        
        # Check environment variables
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION")
        
        validation_result["metadata"]["has_access_key"] = bool(aws_access_key)
        validation_result["metadata"]["has_secret_key"] = bool(aws_secret_key)
        validation_result["metadata"]["has_region"] = bool(aws_region)
        validation_result["metadata"]["region"] = aws_region
        
        if not aws_access_key:
            validation_result["warnings"].append("AWS_ACCESS_KEY_ID not found in environment")
        
        if not aws_secret_key:
            validation_result["warnings"].append("AWS_SECRET_ACCESS_KEY not found in environment")
        
        if not aws_region:
            validation_result["warnings"].append("AWS_REGION not found in environment")
        
        # Check AWS profile
        aws_profile = os.getenv("AWS_PROFILE")
        if aws_profile:
            validation_result["metadata"]["aws_profile"] = aws_profile
        
        return validation_result
    
    @staticmethod
    def validate_dependencies() -> Dict[str, Any]:
        """Validate required dependencies."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        required_packages = [
            "boto3",
            "botocore", 
            "pillow",
            "pydantic",
            "requests",
            "strands-agents"
        ]
        
        available_packages = []
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                available_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        validation_result["metadata"]["available_packages"] = available_packages
        validation_result["metadata"]["missing_packages"] = missing_packages
        
        if missing_packages:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required packages: {missing_packages}")
        
        return validation_result
    
    @staticmethod
    def validate_system_resources() -> Dict[str, Any]:
        """Validate system resources."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {}
        }
        
        import psutil
        import tempfile
        
        # Check memory
        memory = psutil.virtual_memory()
        validation_result["metadata"]["total_memory_gb"] = memory.total / (1024**3)
        validation_result["metadata"]["available_memory_gb"] = memory.available / (1024**3)
        validation_result["metadata"]["memory_percent"] = memory.percent
        
        if memory.percent > 90:
            validation_result["warnings"].append("High memory usage detected")
        
        # Check disk space
        disk = psutil.disk_usage('/')
        validation_result["metadata"]["total_disk_gb"] = disk.total / (1024**3)
        validation_result["metadata"]["free_disk_gb"] = disk.free / (1024**3)
        validation_result["metadata"]["disk_percent"] = (disk.used / disk.total) * 100
        
        if disk.free < 1024**3:  # Less than 1GB free
            validation_result["warnings"].append("Low disk space available")
        
        # Check temp directory
        temp_dir = tempfile.gettempdir()
        validation_result["metadata"]["temp_directory"] = temp_dir
        validation_result["metadata"]["temp_writable"] = os.access(temp_dir, os.W_OK)
        
        if not os.access(temp_dir, os.W_OK):
            validation_result["valid"] = False
            validation_result["errors"].append("Temporary directory is not writable")
        
        return validation_result


class ComprehensiveValidator:
    """Comprehensive validation orchestrator."""
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        self.system_validator = SystemValidator()
    
    def validate_infographic_request(
        self,
        text: str,
        platform: str = "general",
        dimensions: Optional[Tuple[int, int]] = None
    ) -> Dict[str, Any]:
        """Validate a complete infographic generation request."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validations": {}
        }
        
        # Validate text input
        text_validation = self.input_validator.validate_text_input(text)
        validation_result["validations"]["text"] = text_validation
        
        if not text_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(text_validation["errors"])
        validation_result["warnings"].extend(text_validation["warnings"])
        
        # Validate platform
        platform_validation = self.input_validator.validate_platform_input(platform)
        validation_result["validations"]["platform"] = platform_validation
        
        if not platform_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(platform_validation["errors"])
        validation_result["warnings"].extend(platform_validation["warnings"])
        
        # Validate dimensions if provided
        if dimensions:
            dimensions_validation = self.input_validator.validate_image_dimensions(dimensions)
            validation_result["validations"]["dimensions"] = dimensions_validation
            
            if not dimensions_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(dimensions_validation["errors"])
            validation_result["warnings"].extend(dimensions_validation["warnings"])
        
        return validation_result
    
    def validate_system_readiness(self) -> Dict[str, Any]:
        """Validate system readiness for infographic generation."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validations": {}
        }
        
        # Validate AWS credentials
        aws_validation = self.system_validator.validate_aws_credentials()
        validation_result["validations"]["aws"] = aws_validation
        validation_result["warnings"].extend(aws_validation["warnings"])
        
        # Validate dependencies
        deps_validation = self.system_validator.validate_dependencies()
        validation_result["validations"]["dependencies"] = deps_validation
        
        if not deps_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(deps_validation["errors"])
        
        # Validate system resources
        resources_validation = self.system_validator.validate_system_resources()
        validation_result["validations"]["resources"] = resources_validation
        
        if not resources_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(resources_validation["errors"])
        validation_result["warnings"].extend(resources_validation["warnings"])
        
        return validation_result
    
    def validate_generation_output(
        self,
        content_analysis: Optional[ContentAnalysis] = None,
        image_assets: Optional[List[ImageAsset]] = None,
        layout: Optional[LayoutSpecification] = None,
        final_response: Optional[AgentResponse] = None
    ) -> Dict[str, Any]:
        """Validate complete generation output."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validations": {}
        }
        
        # Validate content analysis
        if content_analysis:
            content_validation = self.output_validator.validate_content_analysis(content_analysis)
            validation_result["validations"]["content_analysis"] = content_validation
            
            if not content_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(content_validation["errors"])
            validation_result["warnings"].extend(content_validation["warnings"])
        
        # Validate image assets
        if image_assets:
            for i, asset in enumerate(image_assets):
                asset_validation = self.output_validator.validate_image_asset(asset)
                validation_result["validations"][f"image_asset_{i}"] = asset_validation
                
                if not asset_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend([f"Asset {i+1}: {error}" for error in asset_validation["errors"]])
                validation_result["warnings"].extend([f"Asset {i+1}: {warning}" for warning in asset_validation["warnings"]])
        
        # Validate layout
        if layout:
            layout_validation = self.output_validator.validate_layout_specification(layout)
            validation_result["validations"]["layout"] = layout_validation
            
            if not layout_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(layout_validation["errors"])
            validation_result["warnings"].extend(layout_validation["warnings"])
        
        # Validate final response
        if final_response:
            response_validation = self.output_validator.validate_agent_response(final_response)
            validation_result["validations"]["final_response"] = response_validation
            
            if not response_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(response_validation["errors"])
            validation_result["warnings"].extend(response_validation["warnings"])
        
        return validation_result


# Global validator instance
_global_validator = None


def get_validator() -> ComprehensiveValidator:
    """Get or create global validator instance."""
    global _global_validator
    if _global_validator is None:
        _global_validator = ComprehensiveValidator()
    return _global_validator


# Convenience functions
def validate_text_input(text: str) -> Dict[str, Any]:
    """Validate text input."""
    return InputValidator.validate_text_input(text)


def validate_platform_input(platform: str) -> Dict[str, Any]:
    """Validate platform input."""
    return InputValidator.validate_platform_input(platform)


def validate_content_analysis(analysis: AnalyzedContent) -> Dict[str, Any]:
    """Validate content analysis output."""
    return OutputValidator.validate_content_analysis(analysis)


def validate_system_readiness() -> Dict[str, Any]:
    """Validate system readiness."""
    return get_validator().validate_system_readiness()


def validate_infographic_request(text: str, platform: str = "general") -> Dict[str, Any]:
    """Validate infographic generation request."""
    return get_validator().validate_infographic_request(text, platform)