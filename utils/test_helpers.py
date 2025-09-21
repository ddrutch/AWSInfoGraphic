"""
Test helper utilities for AWS Infographic Generator.

This module provides utilities and patterns that support testing
without actually implementing test cases. It includes mock factories,
test data generators, and validation helpers.
"""

import json
import tempfile
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from unittest.mock import Mock, MagicMock
from PIL import Image, ImageDraw

from .types import ContentAnalysis, ImageAsset, LayoutSpecification, AgentResponse
from .constants import PLATFORM_SPECS, IMAGE_GENERATION_LIMITS


class MockDataFactory:
    """Factory for creating mock data objects for testing purposes."""
    
    @staticmethod
    def create_mock_content_analysis(
        topic: str = "Sample Topic",
        key_points: Optional[List[str]] = None,
        summary: str = "Sample summary"
    ) -> ContentAnalysis:
        """Create a mock ContentAnalysis object."""
        return ContentAnalysis(
            main_topic=topic,
            key_points=key_points or ["Point 1", "Point 2", "Point 3"],
            hierarchy={"sections": [], "flow_direction": "top-to-bottom"},
            summary=summary,
            suggested_title=f"Title: {topic}",
            content_structure={"metadata": {"mock": True}}
        )
    
    @staticmethod
    def create_mock_image_asset(
        asset_type: str = "generated",
        dimensions: tuple = (512, 512)
    ) -> ImageAsset:
        """Create a mock ImageAsset object."""
        return ImageAsset(
            url="https://example.com/mock-image.png",
            local_path="/tmp/mock-image.png",
            description="Mock image for testing",
            dimensions=dimensions,
            asset_type=asset_type,
            metadata={"mock": True}
        )
    
    @staticmethod
    def create_mock_layout_specification(
        platform: str = "general"
    ) -> LayoutSpecification:
        """Create a mock LayoutSpecification object."""
        spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["general"])
        
        return LayoutSpecification(
            canvas_size=spec["dimensions"],
            elements=[],
            color_scheme={"primary": "#007bff", "secondary": "#6c757d"},
            platform_optimizations={"platform": platform, "mock": True}
        )
    
    @staticmethod
    def create_mock_agent_response(
        success: bool = True,
        data: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Create a mock AgentResponse object."""
        return AgentResponse(
            success=success,
            data=data or {"mock": True},
            metadata={"timestamp": datetime.now().isoformat(), "mock": True},
            error_message=None if success else "Mock error message"
        )


class MockAWSServices:
    """Mock AWS service responses for testing purposes."""
    
    @staticmethod
    def create_mock_bedrock_response(content: str = "Mock Bedrock response") -> str:
        """Create a mock Bedrock model response."""
        return content
    
    @staticmethod
    def create_mock_bedrock_json_response(data: Dict[str, Any]) -> str:
        """Create a mock Bedrock JSON response."""
        return json.dumps(data)
    
    @staticmethod
    def create_mock_s3_upload_response(bucket: str = "mock-bucket", key: str = "mock-key") -> Dict[str, Any]:
        """Create a mock S3 upload response."""
        return {
            "ETag": '"mock-etag"',
            "Location": f"https://{bucket}.s3.amazonaws.com/{key}",
            "Bucket": bucket,
            "Key": key
        }
    
    @staticmethod
    def create_mock_nova_canvas_response(image_data: bytes = b"mock-image-data") -> Dict[str, Any]:
        """Create a mock Nova Canvas response."""
        return {
            "images": [
                {
                    "image": image_data,
                    "seed": 12345,
                    "finishReason": "SUCCESS"
                }
            ]
        }


class TestDataGenerator:
    """Generates test data for various scenarios."""
    
    @staticmethod
    def generate_sample_text(length: str = "medium") -> str:
        """Generate sample text of different lengths."""
        short_text = "AI is transforming business operations."
        
        medium_text = """
        Artificial Intelligence is revolutionizing how businesses operate in the modern world.
        Companies are adopting AI technologies to improve efficiency and productivity.
        Machine learning algorithms analyze vast amounts of data to identify patterns.
        The future of work will involve human-AI collaboration across industries.
        """
        
        long_text = """
        Artificial Intelligence represents one of the most significant technological advances of our time.
        Organizations across various industries are implementing AI solutions to streamline operations,
        enhance customer experiences, and drive innovation. Machine learning algorithms can process
        and analyze enormous datasets, uncovering insights that would be impossible for humans to detect.
        
        The integration of AI into business processes has led to improved decision-making capabilities,
        automated routine tasks, and the development of new products and services. From healthcare
        diagnostics to financial fraud detection, AI applications are becoming increasingly sophisticated
        and reliable.
        
        However, the adoption of AI also presents challenges including ethical considerations,
        job displacement concerns, and the need for new skills and training. Organizations must
        carefully balance the benefits of AI implementation with responsible deployment practices
        that consider societal impact and human welfare.
        
        Looking forward, the future of AI promises even more advanced capabilities including
        general artificial intelligence, improved natural language processing, and enhanced
        computer vision systems. The key to successful AI adoption lies in understanding both
        the technology's potential and its limitations.
        """
        
        if length == "short":
            return short_text.strip()
        elif length == "long":
            return long_text.strip()
        else:
            return medium_text.strip()
    
    @staticmethod
    def generate_platform_test_cases() -> List[Dict[str, Any]]:
        """Generate test cases for different platforms."""
        test_cases = []
        
        for platform, specs in PLATFORM_SPECS.items():
            test_cases.append({
                "platform": platform,
                "dimensions": specs["dimensions"],
                "format": specs["format"],
                "expected_aspect_ratio": specs["dimensions"][0] / specs["dimensions"][1]
            })
        
        return test_cases
    
    @staticmethod
    def generate_error_scenarios() -> List[Dict[str, Any]]:
        """Generate error scenarios for testing error handling."""
        return [
            {
                "scenario": "network_timeout",
                "error_type": "TimeoutError",
                "should_retry": True,
                "expected_fallback": True
            },
            {
                "scenario": "aws_rate_limit",
                "error_type": "RateLimitError",
                "should_retry": True,
                "expected_fallback": False
            },
            {
                "scenario": "invalid_input",
                "error_type": "ValidationError",
                "should_retry": False,
                "expected_fallback": True
            },
            {
                "scenario": "service_unavailable",
                "error_type": "AWSServiceError",
                "should_retry": True,
                "expected_fallback": True
            }
        ]


class MockImageGenerator:
    """Generates mock images for testing purposes."""
    
    @staticmethod
    def create_test_image(
        width: int = 512,
        height: int = 512,
        color: str = "#f0f0f0",
        text: str = "Test Image"
    ) -> Image.Image:
        """Create a test image with specified parameters."""
        image = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(image)
        
        # Add text to image
        text_width = len(text) * 10  # Rough estimate
        text_height = 20
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill="black")
        
        return image
    
    @staticmethod
    def save_test_image(
        image: Image.Image,
        filename: Optional[str] = None
    ) -> str:
        """Save test image to temporary file."""
        if filename is None:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                filename = f.name
        
        image.save(filename, "PNG")
        return filename
    
    @staticmethod
    def create_test_image_file(
        width: int = 512,
        height: int = 512,
        filename: Optional[str] = None
    ) -> str:
        """Create and save a test image file."""
        image = MockImageGenerator.create_test_image(width, height)
        return MockImageGenerator.save_test_image(image, filename)


class ValidationHelpers:
    """Helper functions for validating outputs and behavior."""
    
    @staticmethod
    def validate_content_analysis(analysis: AnalyzedContent) -> Dict[str, bool]:
        """Validate ContentAnalysis object structure and content."""
        validations = {
            "has_main_topic": bool(analysis.main_topic and len(analysis.main_topic.strip()) > 0),
            "has_key_points": bool(analysis.key_points and len(analysis.key_points) > 0),
            "has_summary": bool(analysis.summary and len(analysis.summary.strip()) > 0),
            "has_title": bool(analysis.suggested_title and len(analysis.suggested_title.strip()) > 0),
            "has_hierarchy": bool(analysis.hierarchy and isinstance(analysis.hierarchy, dict)),
            "key_points_reasonable_length": all(
                len(point) <= 100 for point in analysis.key_points
            ) if analysis.key_points else False,
            "title_reasonable_length": len(analysis.suggested_title) <= 60 if analysis.suggested_title else False
        }
        
        return validations
    
    @staticmethod
    def validate_image_asset(asset: ImageAsset) -> Dict[str, bool]:
        """Validate ImageAsset object structure and content."""
        validations = {
            "has_description": bool(asset.description and len(asset.description.strip()) > 0),
            "has_dimensions": bool(asset.dimensions and len(asset.dimensions) == 2),
            "valid_dimensions": all(d > 0 for d in asset.dimensions) if asset.dimensions else False,
            "has_asset_type": bool(asset.asset_type and asset.asset_type in ["stock", "generated", "placeholder"]),
            "has_url_or_path": bool(asset.url or asset.local_path)
        }
        
        return validations
    
    @staticmethod
    def validate_agent_response(response: AgentResponse) -> Dict[str, bool]:
        """Validate AgentResponse object structure and content."""
        validations = {
            "has_success_flag": hasattr(response, 'success'),
            "has_data": bool(response.data is not None),
            "has_metadata": bool(response.metadata is not None),
            "error_message_when_failed": (
                bool(response.error_message) if not response.success else True
            ),
            "data_when_successful": (
                bool(response.data) if response.success else True
            )
        }
        
        return validations
    
    @staticmethod
    def validate_platform_compliance(
        output_specs: Dict[str, Any],
        platform: str
    ) -> Dict[str, bool]:
        """Validate output compliance with platform specifications."""
        if platform not in PLATFORM_SPECS:
            return {"valid_platform": False}
        
        expected_specs = PLATFORM_SPECS[platform]
        
        validations = {
            "valid_platform": True,
            "correct_dimensions": (
                output_specs.get("dimensions") == expected_specs["dimensions"]
            ),
            "correct_format": (
                output_specs.get("format") == expected_specs["format"]
            ),
            "within_size_limits": True  # Would check file size in real implementation
        }
        
        return validations


class PerformanceBenchmarks:
    """Performance benchmarks and timing utilities."""
    
    @staticmethod
    def get_performance_expectations() -> Dict[str, Dict[str, float]]:
        """Get expected performance benchmarks for different operations."""
        return {
            "content_analysis": {
                "max_duration": 10.0,  # seconds
                "typical_duration": 3.0,
                "timeout": 30.0
            },
            "image_generation": {
                "max_duration": 30.0,
                "typical_duration": 15.0,
                "timeout": 60.0
            },
            "layout_design": {
                "max_duration": 5.0,
                "typical_duration": 2.0,
                "timeout": 15.0
            },
            "text_formatting": {
                "max_duration": 3.0,
                "typical_duration": 1.0,
                "timeout": 10.0
            },
            "image_composition": {
                "max_duration": 15.0,
                "typical_duration": 8.0,
                "timeout": 45.0
            },
            "end_to_end": {
                "max_duration": 120.0,
                "typical_duration": 60.0,
                "timeout": 300.0
            }
        }
    
    @staticmethod
    def validate_performance(
        operation: str,
        duration: float
    ) -> Dict[str, Any]:
        """Validate operation performance against benchmarks."""
        benchmarks = PerformanceBenchmarks.get_performance_expectations()
        
        if operation not in benchmarks:
            return {"error": f"No benchmarks for operation: {operation}"}
        
        expected = benchmarks[operation]
        
        return {
            "operation": operation,
            "duration": duration,
            "within_typical": duration <= expected["typical_duration"],
            "within_max": duration <= expected["max_duration"],
            "within_timeout": duration <= expected["timeout"],
            "performance_ratio": duration / expected["typical_duration"],
            "status": (
                "excellent" if duration <= expected["typical_duration"]
                else "good" if duration <= expected["max_duration"]
                else "slow" if duration <= expected["timeout"]
                else "timeout"
            )
        }


class ConfigurationHelpers:
    """Helpers for managing test configurations."""
    
    @staticmethod
    def create_test_config() -> Dict[str, Any]:
        """Create a test configuration with safe defaults."""
        return {
            "aws": {
                "region": "us-east-1",
                "bedrock_model": "anthropic.claude-3-sonnet-20240229-v1:0",
                "s3_bucket": "test-infographic-bucket",
                "nova_canvas_model": "amazon.nova-canvas-v1:0"
            },
            "generation": {
                "max_retries": 2,
                "timeout": 30,
                "fallback_enabled": True
            },
            "platforms": PLATFORM_SPECS,
            "limits": IMAGE_GENERATION_LIMITS,
            "testing": {
                "mock_aws_services": True,
                "use_local_images": True,
                "skip_external_calls": True
            }
        }
    
    @staticmethod
    def create_mock_environment() -> Dict[str, str]:
        """Create mock environment variables for testing."""
        return {
            "AWS_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "test-access-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret-key",
            "S3_BUCKET_NAME": "test-bucket",
            "BEDROCK_MODEL_ID": "test-model",
            "NOVA_CANVAS_MODEL_ID": "test-canvas-model",
            "LOG_LEVEL": "DEBUG",
            "TESTING": "true"
        }


def cleanup_test_files(file_paths: List[str]):
    """Clean up temporary test files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove test file {file_path}: {e}")


def setup_test_environment() -> Dict[str, Any]:
    """Set up a complete test environment with mocks and helpers."""
    return {
        "mock_factory": MockDataFactory(),
        "aws_mocks": MockAWSServices(),
        "data_generator": TestDataGenerator(),
        "image_generator": MockImageGenerator(),
        "validators": ValidationHelpers(),
        "benchmarks": PerformanceBenchmarks(),
        "config": ConfigurationHelpers.create_test_config(),
        "env": ConfigurationHelpers.create_mock_environment()
    }