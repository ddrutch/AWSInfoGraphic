"""
Text formatting tools for AWS infographic generator.

This module provides utilities for text styling, typography decisions, font management,
text measurement, and platform-specific text optimization using Amazon Bedrock.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

from .bedrock_tools import BedrockTools, BedrockInvocationError
from utils.types import PlatformType, FormattedText, AgentResponse
from utils.constants import (
    PLATFORM_SPECS, DEFAULT_FONTS, DEFAULT_COLOR_SCHEMES, 
    VALIDATION_RULES, PROCESSING_TIMEOUTS
)

logger = logging.getLogger(__name__)


class TextFormattingError(Exception):
    """Base exception for text formatting operations."""
    pass


class FontManager:
    """Manages font loading and caching for text rendering."""
    
    def __init__(self):
        """Initialize font manager with default fonts."""
        self._font_cache = {}
        self._default_font_paths = self._get_system_fonts()
        
    def _get_system_fonts(self) -> Dict[str, str]:
        """Get available system fonts."""
        system_fonts = {
            "Arial": "arial.ttf",
            "Helvetica": "helvetica.ttf", 
            "Times": "times.ttf",
            "Courier": "courier.ttf",
            "Verdana": "verdana.ttf",
            "Georgia": "georgia.ttf",
            "Trebuchet": "trebuchet.ttf",
            "Impact": "impact.ttf"
        }
        
        # Try to find actual font paths on system
        font_paths = {}
        for font_name, font_file in system_fonts.items():
            try:
                # Try common font directories
                possible_paths = [
                    f"/System/Library/Fonts/{font_file}",  # macOS
                    f"/usr/share/fonts/truetype/dejavu/{font_file}",  # Linux
                    f"C:/Windows/Fonts/{font_file}",  # Windows
                    f"/usr/share/fonts/{font_file}",  # Generic Linux
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        font_paths[font_name] = path
                        break
                else:
                    # Use PIL default if system font not found
                    font_paths[font_name] = None
                    
            except Exception as e:
                logger.warning(f"Could not locate font {font_name}: {e}")
                font_paths[font_name] = None
                
        return font_paths
    
    def get_font(self, family: str, size: int, weight: str = "normal") -> ImageFont.ImageFont:
        """
        Get font object for rendering.
        
        Args:
            family: Font family name
            size: Font size in pixels
            weight: Font weight (normal, bold)
            
        Returns:
            PIL ImageFont object
        """
        cache_key = f"{family}_{size}_{weight}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        try:
            font_path = self._default_font_paths.get(family)
            
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, size)
            else:
                # Fallback to PIL default font
                try:
                    font = ImageFont.load_default()
                except Exception:
                    # Create a basic font if all else fails
                    font = ImageFont.load_default()
            
            self._font_cache[cache_key] = font
            return font
            
        except Exception as e:
            logger.warning(f"Failed to load font {family}, using default: {e}")
            # Return default font as fallback
            default_font = ImageFont.load_default()
            self._font_cache[cache_key] = default_font
            return default_font
    
    def measure_text(self, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
        """
        Measure text dimensions.
        
        Args:
            text: Text to measure
            font: Font to use for measurement
            
        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            # Create temporary image for measurement
            temp_img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            return (width, height)
            
        except Exception as e:
            logger.error(f"Text measurement failed: {e}")
            # Return estimated dimensions as fallback
            return (len(text) * 8, 16)
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available font families."""
        return list(self._default_font_paths.keys())


class TextTools:
    """
    Text formatting utilities for infographic generation.
    
    Provides methods for intelligent text styling, typography decisions,
    and platform-specific text optimization.
    """
    
    def __init__(self, bedrock_tools: Optional[BedrockTools] = None):
        """
        Initialize TextTools with Bedrock integration.
        
        Args:
            bedrock_tools: Optional BedrockTools instance
        """
        self.bedrock_tools = bedrock_tools or BedrockTools()
        self.font_manager = FontManager()
        
    def analyze_text_requirements(self, content: str, platform: str = "general") -> Dict[str, Any]:
        """
        Analyze text content to determine optimal formatting requirements.
        
        Args:
            content: Text content to analyze
            platform: Target platform for optimization
            
        Returns:
            Dictionary containing text formatting requirements
            
        Raises:
            TextFormattingError: If analysis fails
        """
        try:
            platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["general"])
            
            prompt = f"""Analyze this text content for infographic formatting on {platform}:

"{content}"

Platform constraints:
- Canvas size: {platform_spec['dimensions']}
- Max text size: {platform_spec['max_text_size']}px
- Min text size: {platform_spec['min_text_size']}px
- Max elements: {platform_spec['max_elements']}

Return JSON with:
- text_hierarchy: Array of text levels with "type" (title/subtitle/body/caption), "content", "priority" (1-5)
- font_recommendations: Object with "title_font", "body_font", "accent_font"
- size_recommendations: Object with sizes for each text type
- color_strategy: "high_contrast", "monochromatic", "accent_based"
- readability_score: 1-10 (10 = most readable)
- text_density: "low", "medium", "high"
- suggested_line_spacing: multiplier (1.0-2.0)

Focus on readability and visual hierarchy for {platform}."""

            system_prompt = """You are a typography expert specializing in infographic design. 
Analyze text content and provide formatting recommendations that maximize readability and visual impact."""
            
            response = self.bedrock_tools.invoke_model(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            try:
                requirements = json.loads(response)
                
                # Validate and enhance requirements
                requirements = self._validate_text_requirements(requirements, platform_spec)
                
                # Add computed metrics
                requirements.update({
                    "content_length": len(content),
                    "word_count": len(content.split()),
                    "estimated_reading_time": max(1, len(content.split()) // 200),
                    "platform": platform,
                    "analysis_timestamp": datetime.now().isoformat()
                })
                
                return requirements
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse text requirements, using fallback: {e}")
                return self._fallback_text_requirements(content, platform_spec)
                
        except Exception as e:
            raise TextFormattingError(f"Text requirements analysis failed: {str(e)}")
    
    def _validate_text_requirements(self, requirements: Dict[str, Any], platform_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean text requirements."""
        # Ensure required fields exist
        if "text_hierarchy" not in requirements:
            requirements["text_hierarchy"] = []
        
        if "size_recommendations" not in requirements:
            requirements["size_recommendations"] = {
                "title": platform_spec["title_size"],
                "subtitle": platform_spec["subtitle_size"],
                "body": platform_spec["body_size"]
            }
        
        # Validate size constraints
        for text_type, size in requirements["size_recommendations"].items():
            if size > platform_spec["max_text_size"]:
                requirements["size_recommendations"][text_type] = platform_spec["max_text_size"]
            elif size < platform_spec["min_text_size"]:
                requirements["size_recommendations"][text_type] = platform_spec["min_text_size"]
        
        return requirements
    
    def _fallback_text_requirements(self, content: str, platform_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback text requirements analysis."""
        word_count = len(content.split())
        
        # Simple hierarchy detection
        sentences = re.split(r'[.!?]+', content)
        hierarchy = []
        
        if sentences:
            # First sentence as title
            hierarchy.append({
                "type": "title",
                "content": sentences[0].strip()[:60],
                "priority": 5
            })
            
            # Remaining sentences as body
            for i, sentence in enumerate(sentences[1:3]):  # Max 2 body sentences
                if sentence.strip():
                    hierarchy.append({
                        "type": "body",
                        "content": sentence.strip(),
                        "priority": 3 - i
                    })
        
        return {
            "text_hierarchy": hierarchy,
            "font_recommendations": {
                "title_font": "Arial",
                "body_font": "Arial",
                "accent_font": "Arial"
            },
            "size_recommendations": {
                "title": platform_spec["title_size"],
                "subtitle": platform_spec["subtitle_size"],
                "body": platform_spec["body_size"]
            },
            "color_strategy": "high_contrast",
            "readability_score": 7,
            "text_density": "medium" if word_count > 50 else "low",
            "suggested_line_spacing": 1.2
        }
    
    def create_text_styles(self, requirements: Dict[str, Any], color_scheme: ColorScheme) -> Dict[str, FontStyle]:
        """
        Create text styles based on requirements and color scheme.
        
        Args:
            requirements: Text formatting requirements
            color_scheme: Color scheme to use
            
        Returns:
            Dictionary mapping text types to FontStyle objects
        """
        try:
            font_recs = requirements.get("font_recommendations", {})
            size_recs = requirements.get("size_recommendations", {})
            
            styles = {}
            
            # Title style
            styles["title"] = FontStyle(
                family=font_recs.get("title_font", "Arial"),
                size=size_recs.get("title", 32),
                weight="bold",
                color=color_scheme.text
            )
            
            # Subtitle style
            styles["subtitle"] = FontStyle(
                family=font_recs.get("body_font", "Arial"),
                size=size_recs.get("subtitle", 24),
                weight="normal",
                color=color_scheme.text
            )
            
            # Body style
            styles["body"] = FontStyle(
                family=font_recs.get("body_font", "Arial"),
                size=size_recs.get("body", 16),
                weight="normal",
                color=color_scheme.text
            )
            
            # Caption style
            styles["caption"] = FontStyle(
                family=font_recs.get("body_font", "Arial"),
                size=max(10, size_recs.get("body", 16) - 4),
                weight="normal",
                color=color_scheme.secondary
            )
            
            # Accent style (for highlights)
            styles["accent"] = FontStyle(
                family=font_recs.get("accent_font", "Arial"),
                size=size_recs.get("body", 16),
                weight="bold",
                color=color_scheme.accent
            )
            
            return styles
            
        except Exception as e:
            logger.error(f"Text style creation failed: {e}")
            # Return default styles
            return self._get_default_text_styles(color_scheme)
    
    def _get_default_text_styles(self, color_scheme: ColorScheme) -> Dict[str, FontStyle]:
        """Get default text styles as fallback."""
        return {
            "title": FontStyle(family="Arial", size=32, weight="bold", color=color_scheme.text),
            "subtitle": FontStyle(family="Arial", size=24, weight="normal", color=color_scheme.text),
            "body": FontStyle(family="Arial", size=16, weight="normal", color=color_scheme.text),
            "caption": FontStyle(family="Arial", size=12, weight="normal", color=color_scheme.secondary),
            "accent": FontStyle(family="Arial", size=16, weight="bold", color=color_scheme.accent)
        }
    
    def calculate_text_positioning(
        self, 
        text_elements: List[Dict[str, Any]], 
        canvas_size: Tuple[int, int],
        margins: Dict[str, int],
        platform: str = "general"
    ) -> List[LayoutElement]:
        """
        Calculate optimal positioning for text elements.
        
        Args:
            text_elements: List of text elements with content and styling
            canvas_size: Canvas dimensions (width, height)
            margins: Margin specifications
            platform: Target platform
            
        Returns:
            List of positioned LayoutElement objects
        """
        try:
            width, height = canvas_size
            platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["general"])
            
            positioned_elements = []
            current_y = margins["top"]
            
            for i, element in enumerate(text_elements):
                text_type = element.get("type", "body")
                content = element.get("content", "")
                style = element.get("style", {})
                
                # Get font for measurement
                font_family = style.get("family", "Arial")
                font_size = style.get("size", 16)
                font_weight = style.get("weight", "normal")
                
                font = self.font_manager.get_font(font_family, font_size, font_weight)
                text_width, text_height = self.font_manager.measure_text(content, font)
                
                # Calculate position
                x_position = margins["left"]
                y_position = current_y
                
                # Center text horizontally if it's a title
                if text_type == "title":
                    available_width = width - margins["left"] - margins["right"]
                    if text_width < available_width:
                        x_position = margins["left"] + (available_width - text_width) // 2
                
                # Normalize coordinates (0-1)
                normalized_x = x_position / width
                normalized_y = y_position / height
                normalized_width = min(text_width / width, (width - margins["left"] - margins["right"]) / width)
                normalized_height = text_height / height
                
                # Create layout element
                layout_element = LayoutElement(
                    element_type=ElementType.TEXT,
                    position=(normalized_x, normalized_y),
                    size=(normalized_width, normalized_height),
                    content={
                        "text": content,
                        "font_family": font_family,
                        "font_size": font_size,
                        "font_weight": font_weight,
                        "color": style.get("color", "#000000"),
                        "text_type": text_type
                    },
                    styling={
                        "alignment": "center" if text_type == "title" else "left",
                        "line_spacing": element.get("line_spacing", 1.2),
                        "text_decoration": element.get("decoration", "none")
                    },
                    z_index=10 + i  # Text elements on top
                )
                
                positioned_elements.append(layout_element)
                
                # Update Y position for next element
                spacing = self._get_element_spacing(text_type, platform_spec)
                current_y += text_height + spacing
                
                # Check if we're running out of space
                if current_y > height - margins["bottom"] - 50:
                    logger.warning("Text elements may exceed canvas bounds")
                    break
            
            return positioned_elements
            
        except Exception as e:
            raise TextFormattingError(f"Text positioning calculation failed: {str(e)}")
    
    def _get_element_spacing(self, text_type: str, platform_spec: Dict[str, Any]) -> int:
        """Get spacing after text element based on type."""
        spacing_map = {
            "title": 30,
            "subtitle": 20,
            "body": 15,
            "caption": 10
        }
        
        base_spacing = spacing_map.get(text_type, 15)
        
        # Adjust for platform
        if platform_spec["dimensions"][0] < 1200:  # Smaller platforms
            base_spacing = int(base_spacing * 0.8)
        
        return base_spacing
    
    def optimize_text_for_platform(
        self, 
        text_elements: List[Dict[str, Any]], 
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Optimize text elements for specific platform requirements.
        
        Args:
            text_elements: List of text elements to optimize
            platform: Target platform
            
        Returns:
            List of optimized text elements
        """
        try:
            platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["general"])
            optimized_elements = []
            
            for element in text_elements:
                optimized_element = element.copy()
                
                # Adjust text size for platform
                if "style" in optimized_element and "size" in optimized_element["style"]:
                    current_size = optimized_element["style"]["size"]
                    
                    # Clamp to platform limits
                    min_size = platform_spec["min_text_size"]
                    max_size = platform_spec["max_text_size"]
                    
                    optimized_size = max(min_size, min(max_size, current_size))
                    optimized_element["style"]["size"] = optimized_size
                
                # Truncate text if too long for platform
                content = optimized_element.get("content", "")
                text_type = optimized_element.get("type", "body")
                
                max_lengths = {
                    "title": 60 if platform in ["whatsapp", "twitter"] else 80,
                    "subtitle": 80 if platform in ["whatsapp", "twitter"] else 100,
                    "body": 120 if platform in ["whatsapp", "twitter"] else 150,
                    "caption": 60
                }
                
                max_length = max_lengths.get(text_type, 100)
                if len(content) > max_length:
                    optimized_element["content"] = content[:max_length-3] + "..."
                
                # Platform-specific adjustments
                if platform == "whatsapp":
                    # WhatsApp prefers larger, bolder text
                    if "style" in optimized_element:
                        if text_type == "title":
                            optimized_element["style"]["weight"] = "bold"
                        elif text_type == "body":
                            optimized_element["style"]["size"] = max(
                                optimized_element["style"].get("size", 16), 
                                18
                            )
                
                elif platform == "twitter":
                    # Twitter prefers concise, punchy text
                    if text_type == "body" and len(optimized_element["content"]) > 100:
                        optimized_element["content"] = optimized_element["content"][:97] + "..."
                
                elif platform == "discord":
                    # Discord can handle more detailed text
                    pass  # No specific adjustments needed
                
                optimized_elements.append(optimized_element)
            
            # Limit total number of elements for platform
            max_elements = platform_spec.get("max_elements", 10)
            if len(optimized_elements) > max_elements:
                # Keep most important elements (titles and high priority items first)
                optimized_elements.sort(key=lambda x: (
                    x.get("type") == "title",
                    x.get("priority", 0)
                ), reverse=True)
                optimized_elements = optimized_elements[:max_elements]
            
            return optimized_elements
            
        except Exception as e:
            raise TextFormattingError(f"Platform optimization failed: {str(e)}")
    
    def prepare_text_for_rendering(
        self, 
        layout_elements: List[LayoutElement], 
        canvas_size: Tuple[int, int]
    ) -> List[Dict[str, Any]]:
        """
        Prepare text elements for final image composition.
        
        Args:
            layout_elements: List of positioned text elements
            canvas_size: Canvas dimensions
            
        Returns:
            List of render-ready text specifications
        """
        try:
            render_specs = []
            
            for element in layout_elements:
                if element.element_type != ElementType.TEXT:
                    continue
                
                content = element.content
                if not content or "text" not in content:
                    continue
                
                # Convert normalized coordinates to pixels
                width, height = canvas_size
                pixel_x = int(element.position[0] * width)
                pixel_y = int(element.position[1] * height)
                pixel_width = int(element.size[0] * width)
                pixel_height = int(element.size[1] * height)
                
                # Get font object
                font = self.font_manager.get_font(
                    content.get("font_family", "Arial"),
                    content.get("font_size", 16),
                    content.get("font_weight", "normal")
                )
                
                render_spec = {
                    "text": content["text"],
                    "position": (pixel_x, pixel_y),
                    "size": (pixel_width, pixel_height),
                    "font": font,
                    "color": content.get("color", "#000000"),
                    "alignment": element.styling.get("alignment", "left"),
                    "line_spacing": element.styling.get("line_spacing", 1.2),
                    "z_index": element.z_index,
                    "text_type": content.get("text_type", "body")
                }
                
                render_specs.append(render_spec)
            
            # Sort by z_index for proper layering
            render_specs.sort(key=lambda x: x["z_index"])
            
            return render_specs
            
        except Exception as e:
            raise TextFormattingError(f"Text rendering preparation failed: {str(e)}")
    
    def validate_text_readability(
        self, 
        text_elements: List[Dict[str, Any]], 
        color_scheme: ColorScheme,
        canvas_size: Tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Validate text readability and suggest improvements.
        
        Args:
            text_elements: List of text elements to validate
            color_scheme: Color scheme being used
            canvas_size: Canvas dimensions
            
        Returns:
            Dictionary containing readability analysis and suggestions
        """
        try:
            issues = []
            suggestions = []
            readability_score = 10
            
            for element in text_elements:
                content = element.get("content", "")
                style = element.get("style", {})
                text_type = element.get("type", "body")
                
                # Check text length
                if len(content) > 150 and text_type != "body":
                    issues.append(f"{text_type} text is too long ({len(content)} chars)")
                    suggestions.append(f"Shorten {text_type} to under 100 characters")
                    readability_score -= 1
                
                # Check font size
                font_size = style.get("size", 16)
                if font_size < 12:
                    issues.append(f"{text_type} font size too small ({font_size}px)")
                    suggestions.append(f"Increase {text_type} font size to at least 12px")
                    readability_score -= 2
                
                # Check contrast (simplified)
                text_color = style.get("color", color_scheme.text)
                if text_color == color_scheme.background:
                    issues.append(f"{text_type} has poor contrast")
                    suggestions.append(f"Use contrasting color for {text_type}")
                    readability_score -= 3
            
            # Check overall text density
            total_chars = sum(len(elem.get("content", "")) for elem in text_elements)
            canvas_area = canvas_size[0] * canvas_size[1]
            char_density = total_chars / (canvas_area / 10000)  # chars per 100x100 area
            
            if char_density > 50:
                issues.append("Text density too high")
                suggestions.append("Reduce text content or increase canvas size")
                readability_score -= 2
            
            return {
                "readability_score": max(0, readability_score),
                "issues": issues,
                "suggestions": suggestions,
                "text_density": char_density,
                "total_characters": total_chars,
                "validation_passed": len(issues) == 0
            }
            
        except Exception as e:
            logger.error(f"Readability validation failed: {e}")
            return {
                "readability_score": 5,
                "issues": ["Validation failed"],
                "suggestions": ["Review text formatting manually"],
                "validation_passed": False
            }


def create_text_tools() -> TextTools:
    """
    Factory function to create TextTools instance.
    
    Returns:
        Configured TextTools instance
    """
    return TextTools()


def analyze_text_for_infographic(content: str, platform: str = "general") -> Dict[str, Any]:
    """
    Convenience function to analyze text requirements for infographic.
    
    Args:
        content: Text content to analyze
        platform: Target platform
        
    Returns:
        Text formatting requirements
    """
    text_tools = create_text_tools()
    return text_tools.analyze_text_requirements(content, platform)


def create_platform_optimized_text(
    text_elements: List[Dict[str, Any]], 
    platform: str
) -> List[Dict[str, Any]]:
    """
    Convenience function to optimize text for platform.
    
    Args:
        text_elements: Text elements to optimize
        platform: Target platform
        
    Returns:
        Optimized text elements
    """
    text_tools = create_text_tools()
    return text_tools.optimize_text_for_platform(text_elements, platform)