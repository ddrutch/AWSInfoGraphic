"""
Pure image validation tools for basic file operations.

These tools provide raw image validation without embedded business logic.
All decision-making should happen in AI agent reasoning.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageValidationTools:
    """
    Pure tools for image file validation operations.
    
    Provides raw validation data without embedded business logic or decision-making.
    """
    
    def __init__(self):
        """Initialize image validation tools."""
        pass
    
    def validate_image_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Validate image file format and basic properties.
        Returns raw validation data for AI interpretation.
        
        Args:
            file_path: Path to image file to validate
            
        Returns:
            Raw validation results
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File does not exist",
                    "file_path": file_path,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get basic file info
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Try to validate with PIL
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    return {
                        "success": True,
                        "is_valid_image": True,
                        "file_path": file_path,
                        "file_size": file_size,
                        "file_extension": file_extension,
                        "dimensions": img.size,
                        "width": img.size[0],
                        "height": img.size[1],
                        "format": img.format,
                        "mode": img.mode,
                        "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as img_error:
                return {
                    "success": True,
                    "is_valid_image": False,
                    "file_path": file_path,
                    "file_size": file_size,
                    "file_extension": file_extension,
                    "validation_error": str(img_error),
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def check_image_dimensions(
        self,
        file_path: str,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check image dimensions against constraints.
        Returns raw dimension data for AI interpretation.
        
        Args:
            file_path: Path to image file
            min_width: Minimum width constraint
            min_height: Minimum height constraint
            max_width: Maximum width constraint
            max_height: Maximum height constraint
            
        Returns:
            Raw dimension check results
        """
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                width, height = img.size
                
                constraints_met = []
                constraints_failed = []
                
                if min_width is not None:
                    if width >= min_width:
                        constraints_met.append(f"width >= {min_width}")
                    else:
                        constraints_failed.append(f"width {width} < minimum {min_width}")
                
                if min_height is not None:
                    if height >= min_height:
                        constraints_met.append(f"height >= {min_height}")
                    else:
                        constraints_failed.append(f"height {height} < minimum {min_height}")
                
                if max_width is not None:
                    if width <= max_width:
                        constraints_met.append(f"width <= {max_width}")
                    else:
                        constraints_failed.append(f"width {width} > maximum {max_width}")
                
                if max_height is not None:
                    if height <= max_height:
                        constraints_met.append(f"height <= {max_height}")
                    else:
                        constraints_failed.append(f"height {height} > maximum {max_height}")
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "width": width,
                    "height": height,
                    "aspect_ratio": width / height,
                    "constraints_met": constraints_met,
                    "constraints_failed": constraints_failed,
                    "all_constraints_met": len(constraints_failed) == 0,
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Dimension check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def check_file_size(
        self,
        file_path: str,
        max_size_bytes: Optional[int] = None,
        min_size_bytes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check file size against constraints.
        Returns raw file size data for AI interpretation.
        
        Args:
            file_path: Path to file
            max_size_bytes: Maximum file size in bytes
            min_size_bytes: Minimum file size in bytes
            
        Returns:
            Raw file size check results
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File does not exist",
                    "file_path": file_path,
                    "timestamp": datetime.now().isoformat()
                }
            
            file_size = os.path.getsize(file_path)
            
            constraints_met = []
            constraints_failed = []
            
            if max_size_bytes is not None:
                if file_size <= max_size_bytes:
                    constraints_met.append(f"size <= {max_size_bytes} bytes")
                else:
                    constraints_failed.append(f"size {file_size} > maximum {max_size_bytes} bytes")
            
            if min_size_bytes is not None:
                if file_size >= min_size_bytes:
                    constraints_met.append(f"size >= {min_size_bytes} bytes")
                else:
                    constraints_failed.append(f"size {file_size} < minimum {min_size_bytes} bytes")
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size_bytes": file_size,
                "file_size_kb": file_size / 1024,
                "file_size_mb": file_size / (1024 * 1024),
                "constraints_met": constraints_met,
                "constraints_failed": constraints_failed,
                "all_constraints_met": len(constraints_failed) == 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"File size check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_image_format_info(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Get detailed image format information.
        Returns raw format data for AI interpretation.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Raw image format information
        """
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                # Get basic format info
                format_info = {
                    "success": True,
                    "file_path": file_path,
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add format-specific info
                if hasattr(img, 'info') and img.info:
                    format_info["metadata"] = dict(img.info)
                
                # Add color information
                if hasattr(img, 'getcolors'):
                    try:
                        colors = img.getcolors(maxcolors=256*256*256)
                        if colors:
                            format_info["unique_colors"] = len(colors)
                            format_info["is_grayscale"] = len(set(color[1] if isinstance(color[1], int) else color[1][0] for color in colors[:10])) == 1
                    except:
                        pass  # Skip color analysis if it fails
                
                return format_info
            
        except Exception as e:
            logger.error(f"Format info extraction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_multiple_images(
        self,
        file_paths: List[str]
    ) -> Dict[str, Any]:
        """
        Validate multiple image files.
        Returns raw validation data for all files.
        
        Args:
            file_paths: List of image file paths
            
        Returns:
            Raw validation results for all files
        """
        results = {
            "success": True,
            "total_files": len(file_paths),
            "valid_images": 0,
            "invalid_images": 0,
            "file_results": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for file_path in file_paths:
            try:
                validation_result = self.validate_image_file(file_path)
                results["file_results"][file_path] = validation_result
                
                if validation_result.get("success") and validation_result.get("is_valid_image"):
                    results["valid_images"] += 1
                else:
                    results["invalid_images"] += 1
                    
            except Exception as e:
                results["file_results"][file_path] = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                results["invalid_images"] += 1
        
        return results


# Convenience functions for direct usage
def validate_image(file_path: str) -> Dict[str, Any]:
    """
    Convenience function for image validation.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Validation results
    """
    tools = ImageValidationTools()
    return tools.validate_image_file(file_path)


def check_image_constraints(
    file_path: str,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    max_size_mb: Optional[float] = None
) -> Dict[str, Any]:
    """
    Convenience function for checking image constraints.
    
    Args:
        file_path: Path to image file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        max_size_mb: Maximum file size in MB
        
    Returns:
        Constraint check results
    """
    tools = ImageValidationTools()
    
    results = {}
    
    # Check dimensions
    if max_width or max_height:
        dim_result = tools.check_image_dimensions(
            file_path, 
            max_width=max_width, 
            max_height=max_height
        )
        results["dimensions"] = dim_result
    
    # Check file size
    if max_size_mb:
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        size_result = tools.check_file_size(file_path, max_size_bytes=max_size_bytes)
        results["file_size"] = size_result
    
    return results