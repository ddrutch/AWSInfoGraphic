"""
Pure Nova Canvas tools for external image generation operations.

These tools provide raw Nova Canvas API access without embedded business logic.
All decision-making should happen in AI agent reasoning.
"""

import json
import logging
import base64
import tempfile
from typing import Any, Dict, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from utils.constants import AWS_REGION

logger = logging.getLogger(__name__)


class NovaCanvasTools:
    """
    Pure tools for Amazon Nova Canvas image generation operations.
    
    Provides raw API access without embedded business logic or decision-making.
    """
    
    def __init__(self, region: Optional[str] = None):
        """
        Initialize Nova Canvas tools.
        
        Args:
            region: AWS region for Bedrock client
        """
        self.region = region or AWS_REGION
        
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock client: {str(e)}")
            self.bedrock_client = None
    
    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        negative_prompt: str = "",
        cfg_scale: float = 8.0,
        seed: int = 0,
        num_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate image using Nova Canvas API.
        Returns raw API response without processing.
        
        Args:
            prompt: Text prompt for image generation
            width: Image width in pixels
            height: Image height in pixels
            negative_prompt: Negative prompt to avoid certain elements
            cfg_scale: Configuration scale for generation
            seed: Random seed for reproducibility
            num_images: Number of images to generate
            
        Returns:
            Raw Nova Canvas API response
        """
        try:
            if not self.bedrock_client:
                return {
                    "success": False,
                    "error": "Bedrock client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare Nova Canvas generation parameters
            generation_params = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    "negativeText": negative_prompt,
                },
                "imageGenerationConfig": {
                    "numberOfImages": num_images,
                    "height": height,
                    "width": width,
                    "cfgScale": cfg_scale,
                    "seed": seed
                }
            }
            
            # Call Nova Canvas API
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-canvas-v1:0",
                body=json.dumps(generation_params),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            return {
                "success": True,
                "response_body": response_body,
                "generation_params": generation_params,
                "timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"Nova Canvas API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "ClientError",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown'),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Nova Canvas generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
    
    def save_generated_image(
        self,
        image_data: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save base64 encoded image data to file.
        Pure file operation without processing logic.
        
        Args:
            image_data: Base64 encoded image data
            output_path: Optional output file path
            
        Returns:
            File save results
        """
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Use provided path or create temporary file
            if output_path:
                file_path = output_path
            else:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    file_path = tmp_file.name
            
            # Write image data to file
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size": len(image_bytes),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_generation_params(
        self,
        width: int,
        height: int,
        cfg_scale: float,
        num_images: int
    ) -> Dict[str, Any]:
        """
        Validate Nova Canvas generation parameters.
        Pure validation without decision-making logic.
        
        Args:
            width: Image width
            height: Image height
            cfg_scale: Configuration scale
            num_images: Number of images
            
        Returns:
            Validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check dimension limits
        if width < 320 or width > 4096:
            validation_results["errors"].append(f"Width {width} outside valid range 320-4096")
            validation_results["is_valid"] = False
        
        if height < 320 or height > 4096:
            validation_results["errors"].append(f"Height {height} outside valid range 320-4096")
            validation_results["is_valid"] = False
        
        # Check aspect ratio
        aspect_ratio = width / height
        if aspect_ratio < 0.25 or aspect_ratio > 4.0:
            validation_results["warnings"].append(f"Aspect ratio {aspect_ratio:.2f} may produce suboptimal results")
        
        # Check cfg_scale
        if cfg_scale < 1.0 or cfg_scale > 20.0:
            validation_results["errors"].append(f"CFG scale {cfg_scale} outside valid range 1.0-20.0")
            validation_results["is_valid"] = False
        
        # Check num_images
        if num_images < 1 or num_images > 5:
            validation_results["errors"].append(f"Number of images {num_images} outside valid range 1-5")
            validation_results["is_valid"] = False
        
        return validation_results


# Convenience function for direct usage
def generate_image_with_nova_canvas(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for Nova Canvas image generation.
    
    Args:
        prompt: Text prompt for generation
        width: Image width
        height: Image height
        **kwargs: Additional generation parameters
        
    Returns:
        Generation results
    """
    tools = NovaCanvasTools()
    return tools.generate_image(prompt, width, height, **kwargs)