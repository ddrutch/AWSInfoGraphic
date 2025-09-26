"""
Image composition tools for AWS infographic generator.

This module provides utilities for creating final infographic images using PIL/Pillow,
including canvas creation, element rendering, text rendering, and multi-format export.
"""

import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import json

from utils.types import (
    ImageFormat, FinalInfographic, AgentResponse, LayoutSpec
)
from utils.constants import (
    PLATFORM_SPECS, IMAGE_PROCESSING, SUPPORTED_IMAGE_FORMATS,
    DEFAULT_IMAGE_QUALITY, TEMP_FILE_PREFIX
)
from .s3_tools import S3Tools, S3UploadError

logger = logging.getLogger(__name__)


class CompositionError(Exception):
    """Base exception for image composition operations."""
    pass


class CanvasCreationError(CompositionError):
    """Exception raised when canvas creation fails."""
    pass


class ElementRenderingError(CompositionError):
    """Exception raised when element rendering fails."""
    pass


class ExportError(CompositionError):
    """Exception raised when image export fails."""
    pass


class CompositionTools:
    """
    Tools for creating final infographic images through composition.
    
    Provides methods for:
    - Canvas creation and background setup
    - Element rendering (text, images, shapes)
    - Multi-format export (PNG, JPEG, PDF)
    - S3 upload integration
    """
    
    def __init__(self, s3_tools: Optional[S3Tools] = None):
        """
        Initialize CompositionTools.
        
        Args:
            s3_tools: Optional S3Tools instance for uploads
        """
        self.s3_tools = s3_tools or S3Tools()
        self._temp_files = []  # Track temporary files for cleanup
        
        logger.info("Initialized CompositionTools")
    
    def create_canvas(
        self,
        layout_spec: LayoutSpec,
        background_color: Optional[str] = None,
        background_image: Optional[str] = None
    ) -> Image.Image:
        """
        Create canvas with background for infographic composition.
        
        Args:
            layout_spec: Layout specification with canvas size and styling
            background_color: Optional background color (hex)
            background_image: Optional background image path
            
        Returns:
            PIL Image object representing the canvas
            
        Raises:
            CanvasCreationError: If canvas creation fails
        """
        try:
            width, height = layout_spec.canvas_size
            logger.info(f"Creating canvas: {width}x{height}")
            
            # Determine background color
            if background_color is None:
                background_color = layout_spec.color_scheme.background
            
            # Create base canvas
            canvas = Image.new('RGB', (width, height), background_color)
            
            # Add background image if provided
            if background_image and os.path.exists(background_image):
                try:
                    bg_img = Image.open(background_image)
                    bg_img = bg_img.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # Blend with background color for subtle effect
                    canvas = Image.blend(canvas, bg_img, 0.3)
                    
                except Exception as e:
                    logger.warning(f"Failed to apply background image: {e}")
            
            # Apply any background effects from layout
            canvas = self._apply_background_effects(canvas, layout_spec)
            
            logger.info("Canvas created successfully")
            return canvas
            
        except Exception as e:
            raise CanvasCreationError(f"Failed to create canvas: {str(e)}")
    
    def _apply_background_effects(
        self, 
        canvas: Image.Image, 
        layout_spec: LayoutSpec
    ) -> Image.Image:
        """
        Apply background effects like gradients or textures.
        
        Args:
            canvas: Base canvas image
            layout_spec: Layout specification
            
        Returns:
            Canvas with applied effects
        """
        try:
            # Check for background elements in layout
            for element in layout_spec.elements:
                if element.element_type == ElementType.BACKGROUND:
                    canvas = self._render_background_element(canvas, element, layout_spec.canvas_size)
            
            return canvas
            
        except Exception as e:
            logger.warning(f"Failed to apply background effects: {e}")
            return canvas
    
    def _render_background_element(
        self, 
        canvas: Image.Image, 
        element: LayoutElement, 
        canvas_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Render a background element (gradient, pattern, etc.).
        
        Args:
            canvas: Canvas to render on
            element: Background element to render
            canvas_size: Canvas dimensions
            
        Returns:
            Canvas with rendered background element
        """
        try:
            draw = ImageDraw.Draw(canvas)
            width, height = canvas_size
            
            # Convert normalized coordinates to pixels
            x = int(element.position[0] * width)
            y = int(element.position[1] * height)
            w = int(element.size[0] * width)
            h = int(element.size[1] * height)
            
            # Get styling
            styling = element.styling
            bg_type = styling.get("background_type", "solid")
            
            if bg_type == "gradient":
                # Create simple gradient effect
                gradient_color = styling.get("gradient_color", "#E0E0E0")
                for i in range(h):
                    alpha = int(255 * (1 - i / h))
                    color = self._hex_to_rgb(gradient_color) + (alpha,)
                    draw.rectangle([x, y + i, x + w, y + i + 1], fill=color)
            
            elif bg_type == "pattern":
                # Create simple pattern
                pattern_color = styling.get("pattern_color", "#F0F0F0")
                pattern_size = styling.get("pattern_size", 20)
                
                for px in range(x, x + w, pattern_size):
                    for py in range(y, y + h, pattern_size):
                        if (px // pattern_size + py // pattern_size) % 2 == 0:
                            draw.rectangle([px, py, px + pattern_size, py + pattern_size], 
                                         fill=pattern_color)
            
            return canvas
            
        except Exception as e:
            logger.warning(f"Failed to render background element: {e}")
            return canvas
    
    def render_text_elements(
        self, 
        canvas: Image.Image, 
        text_specs: List[Dict[str, Any]]
    ) -> Image.Image:
        """
        Render text elements onto the canvas.
        
        Args:
            canvas: Canvas to render text on
            text_specs: List of text rendering specifications
            
        Returns:
            Canvas with rendered text
            
        Raises:
            ElementRenderingError: If text rendering fails
        """
        try:
            draw = ImageDraw.Draw(canvas)
            
            # Sort by z_index for proper layering
            sorted_specs = sorted(text_specs, key=lambda x: x.get("z_index", 0))
            
            for spec in sorted_specs:
                try:
                    self._render_single_text(draw, spec)
                except Exception as e:
                    logger.warning(f"Failed to render text element: {e}")
                    continue
            
            logger.info(f"Rendered {len(text_specs)} text elements")
            return canvas
            
        except Exception as e:
            raise ElementRenderingError(f"Text rendering failed: {str(e)}")
    
    def _render_single_text(self, draw: ImageDraw.Draw, spec: Dict[str, Any]) -> None:
        """
        Render a single text element.
        
        Args:
            draw: ImageDraw object
            spec: Text rendering specification
        """
        text = spec["text"]
        position = spec["position"]
        font = spec["font"]
        color = spec["color"]
        alignment = spec.get("alignment", "left")
        
        # Handle multi-line text
        if "\n" in text or len(text) > 50:
            lines = self._wrap_text(text, font, spec.get("size", (300, 100))[0])
            line_height = font.getbbox("A")[3] * spec.get("line_spacing", 1.2)
            
            for i, line in enumerate(lines):
                line_y = position[1] + i * line_height
                line_position = self._calculate_text_position(
                    (position[0], line_y), line, font, alignment, spec.get("size", (300, 100))[0]
                )
                draw.text(line_position, line, font=font, fill=color)
        else:
            # Single line text
            text_position = self._calculate_text_position(
                position, text, font, alignment, spec.get("size", (300, 100))[0]
            )
            draw.text(text_position, text, font=font, fill=color)
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """
        Wrap text to fit within specified width.
        
        Args:
            text: Text to wrap
            font: Font to use for measurement
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def _calculate_text_position(
        self, 
        base_position: Tuple[int, int], 
        text: str, 
        font: ImageFont.ImageFont, 
        alignment: str, 
        max_width: int
    ) -> Tuple[int, int]:
        """
        Calculate text position based on alignment.
        
        Args:
            base_position: Base position (x, y)
            text: Text to position
            font: Font for measurement
            alignment: Text alignment (left, center, right)
            max_width: Maximum available width
            
        Returns:
            Calculated position tuple
        """
        x, y = base_position
        
        if alignment == "center":
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            x = x + (max_width - text_width) // 2
        elif alignment == "right":
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            x = x + max_width - text_width
        
        return (x, y)
    
    def render_image_elements(
        self, 
        canvas: Image.Image, 
        image_specs: List[Dict[str, Any]]
    ) -> Image.Image:
        """
        Render image elements onto the canvas.
        
        Args:
            canvas: Canvas to render images on
            image_specs: List of image rendering specifications
            
        Returns:
            Canvas with rendered images
            
        Raises:
            ElementRenderingError: If image rendering fails
        """
        try:
            # Sort by z_index for proper layering
            sorted_specs = sorted(image_specs, key=lambda x: x.get("z_index", 0))
            
            for spec in sorted_specs:
                try:
                    canvas = self._render_single_image(canvas, spec)
                except Exception as e:
                    logger.warning(f"Failed to render image element: {e}")
                    continue
            
            logger.info(f"Rendered {len(image_specs)} image elements")
            return canvas
            
        except Exception as e:
            raise ElementRenderingError(f"Image rendering failed: {str(e)}")
    
    def _render_single_image(self, canvas: Image.Image, spec: Dict[str, Any]) -> Image.Image:
        """
        Render a single image element.
        
        Args:
            canvas: Canvas to render on
            spec: Image rendering specification
            
        Returns:
            Canvas with rendered image
        """
        image_path = spec.get("image_path")
        position = spec["position"]
        size = spec["size"]
        
        if not image_path or not os.path.exists(image_path):
            # Create placeholder if image not available
            return self._render_image_placeholder(canvas, spec)
        
        try:
            # Load and resize image
            img = Image.open(image_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Apply any image effects
            img = self._apply_image_effects(img, spec.get("styling", {}))
            
            # Paste onto canvas
            if img.mode == 'RGBA':
                canvas.paste(img, position, img)
            else:
                canvas.paste(img, position)
            
            return canvas
            
        except Exception as e:
            logger.warning(f"Failed to render image, using placeholder: {e}")
            return self._render_image_placeholder(canvas, spec)
    
    def _render_image_placeholder(self, canvas: Image.Image, spec: Dict[str, Any]) -> Image.Image:
        """
        Render a placeholder for missing images.
        
        Args:
            canvas: Canvas to render on
            spec: Image specification
            
        Returns:
            Canvas with placeholder
        """
        try:
            draw = ImageDraw.Draw(canvas)
            position = spec["position"]
            size = spec["size"]
            
            # Draw placeholder rectangle
            x, y = position
            w, h = size
            
            # Light gray background
            draw.rectangle([x, y, x + w, y + h], fill="#F0F0F0", outline="#CCCCCC", width=2)
            
            # Add placeholder text
            try:
                font = ImageFont.load_default()
                placeholder_text = "Image"
                
                # Center the text
                bbox = font.getbbox(placeholder_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                text_x = x + (w - text_width) // 2
                text_y = y + (h - text_height) // 2
                
                draw.text((text_x, text_y), placeholder_text, font=font, fill="#999999")
                
            except Exception:
                pass  # Skip text if font loading fails
            
            return canvas
            
        except Exception as e:
            logger.warning(f"Failed to render placeholder: {e}")
            return canvas
    
    def _apply_image_effects(self, img: Image.Image, styling: Dict[str, Any]) -> Image.Image:
        """
        Apply visual effects to an image.
        
        Args:
            img: Image to apply effects to
            styling: Styling specifications
            
        Returns:
            Image with applied effects
        """
        try:
            # Border radius (rounded corners)
            border_radius = styling.get("border_radius", 0)
            if border_radius > 0:
                img = self._apply_rounded_corners(img, border_radius)
            
            # Opacity/transparency
            opacity = styling.get("opacity", 1.0)
            if opacity < 1.0:
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Apply opacity
                alpha = img.split()[-1]
                alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
                img.putalpha(alpha)
            
            # Blur effect
            blur_radius = styling.get("blur", 0)
            if blur_radius > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            
            # Brightness adjustment
            brightness = styling.get("brightness", 1.0)
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            
            # Contrast adjustment
            contrast = styling.get("contrast", 1.0)
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
            
            return img
            
        except Exception as e:
            logger.warning(f"Failed to apply image effects: {e}")
            return img
    
    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """
        Apply rounded corners to an image.
        
        Args:
            img: Image to modify
            radius: Corner radius in pixels
            
        Returns:
            Image with rounded corners
        """
        try:
            # Create mask for rounded corners
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius, fill=255)
            
            # Apply mask
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            img.putalpha(mask)
            return img
            
        except Exception as e:
            logger.warning(f"Failed to apply rounded corners: {e}")
            return img
    
    def render_shape_elements(
        self, 
        canvas: Image.Image, 
        shape_specs: List[Dict[str, Any]]
    ) -> Image.Image:
        """
        Render shape elements (rectangles, circles, lines) onto the canvas.
        
        Args:
            canvas: Canvas to render shapes on
            shape_specs: List of shape rendering specifications
            
        Returns:
            Canvas with rendered shapes
        """
        try:
            draw = ImageDraw.Draw(canvas)
            
            # Sort by z_index for proper layering
            sorted_specs = sorted(shape_specs, key=lambda x: x.get("z_index", 0))
            
            for spec in sorted_specs:
                try:
                    self._render_single_shape(draw, spec)
                except Exception as e:
                    logger.warning(f"Failed to render shape element: {e}")
                    continue
            
            logger.info(f"Rendered {len(shape_specs)} shape elements")
            return canvas
            
        except Exception as e:
            raise ElementRenderingError(f"Shape rendering failed: {str(e)}")
    
    def _render_single_shape(self, draw: ImageDraw.Draw, spec: Dict[str, Any]) -> None:
        """
        Render a single shape element.
        
        Args:
            draw: ImageDraw object
            spec: Shape rendering specification
        """
        shape_type = spec.get("shape_type", "rectangle")
        position = spec["position"]
        size = spec["size"]
        styling = spec.get("styling", {})
        
        x, y = position
        w, h = size
        
        fill_color = styling.get("fill_color", "transparent")
        outline_color = styling.get("outline_color", "#000000")
        outline_width = styling.get("outline_width", 1)
        
        if shape_type == "rectangle":
            draw.rectangle([x, y, x + w, y + h], 
                         fill=fill_color if fill_color != "transparent" else None,
                         outline=outline_color, 
                         width=outline_width)
        
        elif shape_type == "circle":
            # Use the smaller dimension for circle radius
            radius = min(w, h) // 2
            center_x = x + w // 2
            center_y = y + h // 2
            
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius],
                        fill=fill_color if fill_color != "transparent" else None,
                        outline=outline_color,
                        width=outline_width)
        
        elif shape_type == "line":
            end_x = x + w
            end_y = y + h
            draw.line([x, y, end_x, end_y], fill=outline_color, width=outline_width)
        
        elif shape_type == "rounded_rectangle":
            radius = styling.get("border_radius", 10)
            draw.rounded_rectangle([x, y, x + w, y + h], 
                                 radius=radius,
                                 fill=fill_color if fill_color != "transparent" else None,
                                 outline=outline_color,
                                 width=outline_width)
    
    def export_image(
        self, 
        canvas: Image.Image, 
        output_path: str, 
        format: str = "PNG", 
        quality: int = 95,
        optimize: bool = True
    ) -> str:
        """
        Export canvas to image file.
        
        Args:
            canvas: Canvas to export
            output_path: Output file path
            format: Image format (PNG, JPEG, PDF)
            quality: Image quality (1-100, for JPEG)
            optimize: Whether to optimize the image
            
        Returns:
            Path to exported file
            
        Raises:
            ExportError: If export fails
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Validate format
            if format.upper() not in SUPPORTED_IMAGE_FORMATS:
                raise ValueError(f"Unsupported format: {format}")
            
            # Prepare save arguments
            save_kwargs = {"optimize": optimize}
            
            if format.upper() in ["JPEG", "JPG"]:
                # Convert RGBA to RGB for JPEG
                if canvas.mode == 'RGBA':
                    # Create white background
                    rgb_canvas = Image.new('RGB', canvas.size, 'white')
                    rgb_canvas.paste(canvas, mask=canvas.split()[-1] if canvas.mode == 'RGBA' else None)
                    canvas = rgb_canvas
                
                save_kwargs["quality"] = quality
                save_kwargs["format"] = "JPEG"
            
            elif format.upper() == "PNG":
                save_kwargs["format"] = "PNG"
                if canvas.mode != 'RGBA':
                    canvas = canvas.convert('RGBA')
            
            elif format.upper() == "PDF":
                save_kwargs["format"] = "PDF"
                if canvas.mode == 'RGBA':
                    # Convert to RGB for PDF
                    rgb_canvas = Image.new('RGB', canvas.size, 'white')
                    rgb_canvas.paste(canvas, mask=canvas.split()[-1])
                    canvas = rgb_canvas
            
            # Save the image
            canvas.save(output_path, **save_kwargs)
            
            # Verify file was created
            if not os.path.exists(output_path):
                raise ExportError("File was not created")
            
            file_size = os.path.getsize(output_path)
            logger.info(f"Exported {format} image: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            raise ExportError(f"Failed to export image: {str(e)}")
    
    def create_multi_format_exports(
        self, 
        canvas: Image.Image, 
        base_filename: str, 
        formats: List[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export canvas in multiple formats.
        
        Args:
            canvas: Canvas to export
            base_filename: Base filename (without extension)
            formats: List of formats to export (defaults to PNG, JPEG)
            output_dir: Output directory (defaults to temp directory)
            
        Returns:
            Dictionary mapping format to file path
            
        Raises:
            ExportError: If any export fails
        """
        try:
            if formats is None:
                formats = ["PNG", "JPEG"]
            
            if output_dir is None:
                output_dir = tempfile.gettempdir()
            
            exported_files = {}
            
            for format in formats:
                try:
                    # Generate filename with appropriate extension
                    ext = "jpg" if format.upper() == "JPEG" else format.lower()
                    filename = f"{base_filename}.{ext}"
                    output_path = os.path.join(output_dir, filename)
                    
                    # Export in this format
                    exported_path = self.export_image(canvas, output_path, format)
                    exported_files[format.upper()] = exported_path
                    
                    # Track temp file for cleanup
                    self._temp_files.append(exported_path)
                    
                except Exception as e:
                    logger.warning(f"Failed to export {format}: {e}")
                    continue
            
            if not exported_files:
                raise ExportError("No formats were successfully exported")
            
            logger.info(f"Exported {len(exported_files)} formats: {list(exported_files.keys())}")
            return exported_files
            
        except Exception as e:
            raise ExportError(f"Multi-format export failed: {str(e)}")
    
    def upload_to_s3(
        self, 
        image_path: str, 
        s3_key: Optional[str] = None,
        public_read: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[str, str]:
        """
        Upload image to S3 and return URLs.
        
        Args:
            image_path: Local path to image file
            s3_key: Optional S3 key (auto-generated if not provided)
            public_read: Whether to make object publicly readable
            metadata: Optional metadata to store with object
            
        Returns:
            Tuple of (s3_key, public_url)
            
        Raises:
            S3UploadError: If upload fails
        """
        try:
            # Generate S3 key if not provided
            if s3_key is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.basename(image_path)
                s3_key = f"infographics/{timestamp}_{filename}"
            
            # Add generation metadata
            upload_metadata = {
                "generated_at": datetime.now().isoformat(),
                "generator": "aws-infographic-generator",
                "version": "1.0"
            }
            if metadata:
                upload_metadata.update(metadata)
            
            # Upload to S3
            uploaded_key = self.s3_tools.upload_file(
                file_path=image_path,
                s3_key=s3_key,
                public_read=public_read,
                metadata=upload_metadata
            )
            
            # Generate public URL
            if public_read:
                public_url = f"https://{self.s3_tools.bucket_name}.s3.{self.s3_tools.region}.amazonaws.com/{uploaded_key}"
            else:
                public_url = self.s3_tools.generate_presigned_url(uploaded_key, expiration=86400)
            
            logger.info(f"Uploaded to S3: {uploaded_key}")
            return uploaded_key, public_url
            
        except Exception as e:
            raise S3UploadError(f"S3 upload failed: {str(e)}")
    
    def create_platform_variants(
        self, 
        canvas: Image.Image, 
        platforms: List[str] = None
    ) -> Dict[str, Image.Image]:
        """
        Create platform-specific variants of the infographic.
        
        Args:
            canvas: Base canvas
            platforms: List of platforms to create variants for
            
        Returns:
            Dictionary mapping platform to resized canvas
        """
        try:
            if platforms is None:
                platforms = ["whatsapp", "twitter", "discord", "general"]
            
            variants = {}
            
            for platform in platforms:
                try:
                    platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["general"])
                    target_size = platform_spec["dimensions"]
                    
                    # Resize canvas for platform
                    variant = canvas.resize(target_size, Image.Resampling.LANCZOS)
                    variants[platform] = variant
                    
                except Exception as e:
                    logger.warning(f"Failed to create {platform} variant: {e}")
                    continue
            
            logger.info(f"Created {len(variants)} platform variants")
            return variants
            
        except Exception as e:
            logger.warning(f"Platform variant creation failed: {e}")
            return {"general": canvas}
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000")
            
        Returns:
            RGB tuple
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files created during composition."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        
        self._temp_files.clear()
        logger.info("Cleaned up temporary files")
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.cleanup_temp_files()


def create_composition_tools(s3_tools: Optional[S3Tools] = None) -> CompositionTools:
    """
    Factory function to create CompositionTools instance.
    
    Args:
        s3_tools: Optional S3Tools instance
        
    Returns:
        Configured CompositionTools instance
    """
    return CompositionTools(s3_tools=s3_tools)


def compose_infographic(
    layout_spec: LayoutSpec,
    text_specs: List[Dict[str, Any]],
    image_specs: List[Dict[str, Any]] = None,
    shape_specs: List[Dict[str, Any]] = None,
    output_path: Optional[str] = None,
    formats: List[str] = None
) -> Dict[str, str]:
    """
    Convenience function to compose complete infographic.
    
    Args:
        layout_spec: Layout specification
        text_specs: Text rendering specifications
        image_specs: Optional image specifications
        shape_specs: Optional shape specifications
        output_path: Optional output path (uses temp if not provided)
        formats: Export formats (defaults to PNG)
        
    Returns:
        Dictionary mapping format to file path
    """
    composition_tools = create_composition_tools()
    
    try:
        # Create canvas
        canvas = composition_tools.create_canvas(layout_spec)
        
        # Render shapes first (background layer)
        if shape_specs:
            canvas = composition_tools.render_shape_elements(canvas, shape_specs)
        
        # Render images
        if image_specs:
            canvas = composition_tools.render_image_elements(canvas, image_specs)
        
        # Render text on top
        canvas = composition_tools.render_text_elements(canvas, text_specs)
        
        # Export
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{TEMP_FILE_PREFIX}infographic_{timestamp}"
        
        if formats is None:
            formats = ["PNG"]
        
        return composition_tools.create_multi_format_exports(
            canvas, 
            os.path.splitext(output_path)[0], 
            formats
        )
        
    finally:
        composition_tools.cleanup_temp_files()