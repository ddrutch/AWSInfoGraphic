"""
Pure image processing tools for external operations.

These tools provide raw image processing capabilities without embedded business logic.
All decision-making should happen in AI agent reasoning.
"""

import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io

logger = logging.getLogger(__name__)


class ImageProcessingTools:
    """
    Pure tools for image processing operations.
    
    Provides raw image processing capabilities without embedded business logic.
    All decision-making should happen in AI agent reasoning.
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize image processing tools.
        
        Args:
            temp_dir: Temporary directory for processing
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def resize_image(
        self,
        image_path: str,
        width: int,
        height: int,
        resample_method: str = "LANCZOS"
    ) -> Dict[str, Any]:
        """
        Resize image to specified dimensions.
        Pure resize operation without decision-making logic.
        
        Args:
            image_path: Path to source image
            width: Target width in pixels
            height: Target height in pixels
            resample_method: Resampling method (LANCZOS, BICUBIC, etc.)
            
        Returns:
            Resize operation results
        """
        try:
            # Map string to PIL constant
            resample_map = {
                "LANCZOS": Image.Resampling.LANCZOS,
                "BICUBIC": Image.Resampling.BICUBIC,
                "BILINEAR": Image.Resampling.BILINEAR,
                "NEAREST": Image.Resampling.NEAREST
            }
            
            resample = resample_map.get(resample_method, Image.Resampling.LANCZOS)
            
            with Image.open(image_path) as img:
                original_size = img.size
                resized_img = img.resize((width, height), resample)
                
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = os.path.join(self.temp_dir, f"{base_name}_resized_{width}x{height}.png")
                
                resized_img.save(output_path, format="PNG")
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "original_size": original_size,
                    "new_size": (width, height),
                    "resample_method": resample_method,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Image resize failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def convert_image_format(
        self,
        image_path: str,
        target_format: str,
        quality: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert image to different format.
        Pure format conversion without decision-making logic.
        
        Args:
            image_path: Path to source image
            target_format: Target format (PNG, JPEG, WEBP, etc.)
            quality: Quality setting for lossy formats
            
        Returns:
            Format conversion results
        """
        try:
            with Image.open(image_path) as img:
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                ext = target_format.lower()
                if ext == "jpeg":
                    ext = "jpg"
                output_path = os.path.join(self.temp_dir, f"{base_name}_converted.{ext}")
                
                # Prepare save parameters
                save_kwargs = {"format": target_format.upper()}
                
                # Handle format-specific requirements
                if target_format.upper() in ["JPEG", "JPG"]:
                    # Convert RGBA to RGB for JPEG
                    if img.mode in ("RGBA", "LA", "P"):
                        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                        img = rgb_img
                    
                    if quality is not None:
                        save_kwargs["quality"] = quality
                        save_kwargs["optimize"] = True
                
                elif target_format.upper() == "PNG":
                    if quality is not None:
                        # For PNG, quality affects compression level
                        compress_level = max(0, min(9, 9 - (quality // 10)))
                        save_kwargs["compress_level"] = compress_level
                    save_kwargs["optimize"] = True
                
                img.save(output_path, **save_kwargs)
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "original_format": img.format,
                    "target_format": target_format.upper(),
                    "file_size": os.path.getsize(output_path),
                    "quality": quality,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "image_path": image_path,
                "target_format": target_format,
                "timestamp": datetime.now().isoformat()
            }
    
    def apply_image_filter(
        self,
        image_path: str,
        filter_type: str,
        **filter_params
    ) -> Dict[str, Any]:
        """
        Apply image filter.
        Pure filter application without decision-making logic.
        
        Args:
            image_path: Path to source image
            filter_type: Type of filter (blur, sharpen, enhance_contrast, etc.)
            **filter_params: Filter-specific parameters
            
        Returns:
            Filter application results
        """
        try:
            with Image.open(image_path) as img:
                filtered_img = img.copy()
                
                if filter_type == "blur":
                    radius = filter_params.get("radius", 1.0)
                    filtered_img = filtered_img.filter(ImageFilter.GaussianBlur(radius=radius))
                
                elif filter_type == "sharpen":
                    filtered_img = filtered_img.filter(ImageFilter.SHARPEN)
                
                elif filter_type == "enhance_contrast":
                    factor = filter_params.get("factor", 1.1)
                    enhancer = ImageEnhance.Contrast(filtered_img)
                    filtered_img = enhancer.enhance(factor)
                
                elif filter_type == "enhance_brightness":
                    factor = filter_params.get("factor", 1.1)
                    enhancer = ImageEnhance.Brightness(filtered_img)
                    filtered_img = enhancer.enhance(factor)
                
                elif filter_type == "enhance_color":
                    factor = filter_params.get("factor", 1.1)
                    enhancer = ImageEnhance.Color(filtered_img)
                    filtered_img = enhancer.enhance(factor)
                
                elif filter_type == "enhance_sharpness":
                    factor = filter_params.get("factor", 1.1)
                    enhancer = ImageEnhance.Sharpness(filtered_img)
                    filtered_img = enhancer.enhance(factor)
                
                else:
                    return {
                        "success": False,
                        "error": f"Unknown filter type: {filter_type}",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = os.path.join(self.temp_dir, f"{base_name}_{filter_type}.png")
                
                filtered_img.save(output_path, format="PNG")
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "filter_type": filter_type,
                    "filter_params": filter_params,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Filter application failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "image_path": image_path,
                "filter_type": filter_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def crop_image(
        self,
        image_path: str,
        left: int,
        top: int,
        right: int,
        bottom: int
    ) -> Dict[str, Any]:
        """
        Crop image to specified coordinates.
        Pure crop operation without decision-making logic.
        
        Args:
            image_path: Path to source image
            left: Left coordinate
            top: Top coordinate
            right: Right coordinate
            bottom: Bottom coordinate
            
        Returns:
            Crop operation results
        """
        try:
            with Image.open(image_path) as img:
                original_size = img.size
                cropped_img = img.crop((left, top, right, bottom))
                
                # Generate output path
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = os.path.join(self.temp_dir, f"{base_name}_cropped.png")
                
                cropped_img.save(output_path, format="PNG")
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "original_size": original_size,
                    "crop_box": (left, top, right, bottom),
                    "cropped_size": cropped_img.size,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Image crop failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "image_path": image_path,
                "crop_box": (left, top, right, bottom),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_image_info(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        Get basic image information.
        Pure information extraction without decision-making logic.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image information
        """
        try:
            with Image.open(image_path) as img:
                return {
                    "success": True,
                    "file_path": image_path,
                    "size": img.size,
                    "width": img.size[0],
                    "height": img.size[1],
                    "mode": img.mode,
                    "format": img.format,
                    "has_transparency": img.mode in ("RGBA", "LA") or "transparency" in img.info,
                    "file_size": os.path.getsize(image_path),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get image info: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "file_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def create_blank_canvas(
        self,
        width: int,
        height: int,
        background_color: str = "white",
        mode: str = "RGB"
    ) -> Dict[str, Any]:
        """
        Create a blank canvas image.
        Pure canvas creation without decision-making logic.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            background_color: Background color
            mode: Image mode (RGB, RGBA, etc.)
            
        Returns:
            Canvas creation results
        """
        try:
            # Create new image
            canvas = Image.new(mode, (width, height), background_color)
            
            # Generate output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.temp_dir, f"canvas_{width}x{height}_{timestamp}.png")
            
            canvas.save(output_path, format="PNG")
            
            return {
                "success": True,
                "output_path": output_path,
                "size": (width, height),
                "background_color": background_color,
                "mode": mode,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Canvas creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "size": (width, height),
                "timestamp": datetime.now().isoformat()
            }


# Convenience functions for direct usage
def resize_image(image_path: str, width: int, height: int, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for image resizing.
    
    Args:
        image_path: Path to source image
        width: Target width
        height: Target height
        **kwargs: Additional resize parameters
        
    Returns:
        Resize results
    """
    tools = ImageProcessingTools()
    return tools.resize_image(image_path, width, height, **kwargs)


def convert_image_format(image_path: str, target_format: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for format conversion.
    
    Args:
        image_path: Path to source image
        target_format: Target format
        **kwargs: Additional conversion parameters
        
    Returns:
        Conversion results
    """
    tools = ImageProcessingTools()
    return tools.convert_image_format(image_path, target_format, **kwargs)


def get_image_info(image_path: str) -> Dict[str, Any]:
    """
    Convenience function for getting image information.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image information
    """
    tools = ImageProcessingTools()
    return tools.get_image_info(image_path)