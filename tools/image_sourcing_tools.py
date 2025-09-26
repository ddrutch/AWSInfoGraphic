"""Minimal image sourcing tools used by ImageSourcer agent.

This provides a placeholder implementation that can be used in demo mode
or when Nova Canvas access is not available. Implements an async API and
returns objects compatible with the ImageAsset dataclass described in docs.
"""

import asyncio
import logging
from typing import Dict, Any, List, Tuple, Optional

try:
    from strands import tool
except Exception:
    def tool(fn=None, **kwargs):
        if fn is None:
            def _wrap(f):
                return f
            return _wrap
        return fn

logger = logging.getLogger(__name__)


@tool
async def create_placeholder_image(dimensions: Tuple[int, int], text: str = "Image") -> Dict[str, Any]:
    """Create a placeholder image asset (no real image generation).

    Returns a dict with the minimal fields used by downstream agents.
    """
    width, height = dimensions
    # Simulate async work
    await asyncio.sleep(0.01)
    return {
        "url": None,
        "local_path": None,
        "description": text,
        "dimensions": (width, height),
        "asset_type": "placeholder",
        "file_size": 0,
        "format": "PNG",
        "metadata": {},
        "generation_prompt": None,
        "cache_key": None
    }


@tool
async def source_images(topic: str, count: int = 3, style: str = "professional") -> List[Dict[str, Any]]:
    """Return a list of placeholder image assets for the given topic."""
    tasks = [create_placeholder_image((1024, 1024), f"{topic} - {i+1}") for i in range(count)]
    return await asyncio.gather(*tasks)
"""Image sourcing tools for the ImageSourcer agent."""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


@tool
def generate_image_with_nova(
    prompt: str, 
    width: int = 1024, 
    height: int = 1024,
    style: str = "photographic",
    negative_prompt: str = "",
    cfg_scale: float = 8.0
) -> Dict[str, Any]:
    """Generate an image using Amazon Nova Canvas.
    
    Args:
        prompt: Text description for image generation
        width: Image width in pixels
        height: Image height in pixels
        style: Image style (photographic, digital-art, etc.)
        negative_prompt: Elements to avoid in generation
        cfg_scale: Configuration scale for generation control
        
    Returns:
        Dictionary containing image generation results
    """
    try:
        logger.info(f"Generating image with Nova Canvas: {prompt[:50]}...")
        
        # Import Nova Canvas tools for actual generation
        from tools.nova_canvas_tools import NovaCanvasTools
        
        nova_tools = NovaCanvasTools()
        
        # Generate image using Nova Canvas
        result = nova_tools.generate_image(
            prompt=prompt,
            width=width,
            height=height,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale
        )
        
        return {
            "success": True,
            "image_data": result.get("image_data"),
            "image_url": result.get("image_url", ""),
            "image_id": result.get("image_id", ""),
            "status": "completed",
            "generation_params": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "style": style,
                "cfg_scale": cfg_scale
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Nova Canvas generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "status": "failed",
            "timestamp": datetime.now().isoformat()
        }


@tool
def create_image_prompt(content_summary: str, platform: str, content_type: str = "general") -> str:
    """Create optimized image generation prompt based on content.
    
    Args:
        content_summary: Summary of the content to visualize
        platform: Target platform for the infographic
        content_type: Type of content (business, educational, etc.)
        
    Returns:
        Optimized prompt string for image generation
    """
    try:
        # Platform-specific style adjustments
        platform_styles = {
            "whatsapp": "mobile-friendly, high contrast, simple composition",
            "twitter": "attention-grabbing, bold colors, clear focal point",
            "linkedin": "professional, business-appropriate, clean design",
            "instagram": "visually striking, aesthetic, social media optimized",
            "discord": "modern, tech-friendly, gaming culture appropriate",
            "reddit": "authentic, discussion-friendly, not overly promotional",
            "general": "versatile, professional, widely appealing"
        }
        
        style_guidance = platform_styles.get(platform.lower(), platform_styles["general"])
        
        # Content type specific elements
        content_elements = {
            "business": "charts, graphs, professional imagery, corporate aesthetics",
            "educational": "clear diagrams, learning-focused visuals, instructional elements",
            "technology": "modern tech imagery, digital elements, innovation themes",
            "health": "medical imagery, wellness themes, clean and trustworthy visuals",
            "finance": "financial symbols, growth imagery, professional and secure aesthetics",
            "general": "versatile imagery that supports the main message"
        }
        
        content_guidance = content_elements.get(content_type.lower(), content_elements["general"])
        
        # Construct optimized prompt
        optimized_prompt = f"""Create a professional infographic image for {platform} platform.

Content focus: {content_summary}

Style requirements: {style_guidance}
Visual elements: {content_guidance}

Requirements:
- High quality, professional appearance
- Clear visual hierarchy and composition
- Suitable for infographic integration
- Platform-optimized dimensions and style
- Avoid text overlays (text will be added separately)
- Focus on supporting visual elements and imagery
- Clean, modern aesthetic"""
        
        logger.info(f"Created optimized prompt for {platform} platform")
        return optimized_prompt
        
    except Exception as e:
        logger.error(f"Prompt creation failed: {str(e)}")
        return f"Create a professional image for {platform} based on: {content_summary}"


@tool
def validate_generated_image(image_data: Any, platform: str) -> Dict[str, Any]:
    """Validate that generated image meets platform requirements.
    
    Args:
        image_data: Generated image data or URL
        platform: Target platform specifications
        
    Returns:
        Validation results dictionary
    """
    try:
        from tools.image_validation_tools import ImageValidationTools
        
        validator = ImageValidationTools()
        
        # Platform-specific requirements
        platform_specs = {
            "whatsapp": {"width": 1080, "height": 1080, "aspect_ratio": 1.0},
            "twitter": {"width": 1200, "height": 675, "aspect_ratio": 1.78},
            "linkedin": {"width": 1200, "height": 627, "aspect_ratio": 1.91},
            "instagram": {"width": 1080, "height": 1080, "aspect_ratio": 1.0},
            "discord": {"width": 1920, "height": 1080, "aspect_ratio": 1.78},
            "reddit": {"width": 1200, "height": 630, "aspect_ratio": 1.9},
            "general": {"width": 1920, "height": 1080, "aspect_ratio": 1.78}
        }
        
        specs = platform_specs.get(platform.lower(), platform_specs["general"])
        
        # Validate image against platform requirements
        validation_result = validator.validate_platform_compliance(image_data, specs)
        
        return {
            "valid": validation_result.get("compliant", False),
            "issues": validation_result.get("issues", []),
            "recommendations": validation_result.get("recommendations", []),
            "platform_specs": specs,
            "validation_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        return {
            "valid": False,
            "issues": [f"Validation error: {str(e)}"],
            "recommendations": ["Retry image generation with adjusted parameters"],
            "validation_timestamp": datetime.now().isoformat()
        }


@tool
def get_fallback_image(content_type: str, platform: str) -> Dict[str, Any]:
    """Get a fallback image when generation fails.
    
    Args:
        content_type: Type of content for appropriate fallback
        platform: Target platform for sizing
        
    Returns:
        Fallback image information dictionary
    """
    try:
        # Platform dimensions for fallback generation
        platform_dims = {
            "whatsapp": (1080, 1080),
            "twitter": (1200, 675),
            "linkedin": (1200, 627),
            "instagram": (1080, 1080),
            "discord": (1920, 1080),
            "reddit": (1200, 630),
            "general": (1920, 1080)
        }
        
        width, height = platform_dims.get(platform.lower(), platform_dims["general"])
        
        # Content-specific fallback themes
        fallback_themes = {
            "business": "professional gradient background with subtle geometric patterns",
            "educational": "clean academic background with learning-focused elements",
            "technology": "modern tech background with digital elements",
            "health": "clean medical background with wellness themes",
            "finance": "professional financial background with growth elements",
            "general": "clean professional background suitable for any content"
        }
        
        theme = fallback_themes.get(content_type.lower(), fallback_themes["general"])
        
        # Generate simple fallback using basic generation
        fallback_prompt = f"Create a simple, clean {theme} for {platform} platform, {width}x{height} dimensions, minimal design, professional appearance"
        
        logger.info(f"Providing fallback image for {content_type} content on {platform}")
        
        return {
            "fallback_prompt": fallback_prompt,
            "dimensions": {"width": width, "height": height},
            "theme": theme,
            "platform": platform,
            "content_type": content_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fallback image generation failed: {str(e)}")
        return {
            "fallback_prompt": f"Create a simple background for {platform}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def get_image_sourcing_tools():
    """Return list of image sourcing tools for agent initialization."""
    return [
        generate_image_with_nova,
        create_image_prompt,
        validate_generated_image,
        get_fallback_image
    ]