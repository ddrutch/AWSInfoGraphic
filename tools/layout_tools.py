"""
Layout calculation and design tools for AWS Infographic Generator.

This module provides utilities for calculating optimal layouts, positioning elements,
and creating platform-specific design specifications using AWS services.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
import json
import boto3
from botocore.exceptions import ClientError

from utils.types import (
    LayoutSpec, PlatformType, AgentResponse
)
from utils.constants import (
    PLATFORM_SPECS, DEFAULT_COLOR_SCHEMES, DEFAULT_FONTS, 
    LAYOUT_MARGINS, ELEMENT_SPACING, BEDROCK_MODEL_ID, AWS_REGION
)

logger = logging.getLogger(__name__)


class LayoutCalculationError(Exception):
    """Exception raised when layout calculation fails."""
    pass


class LayoutTools:
    """
    Tools for layout calculation and design optimization.
    
    Provides methods for:
    - Element positioning and sizing calculations
    - Platform-specific layout optimizations
    - Color scheme generation and validation
    - Visual hierarchy calculations
    - Grid system implementation
    """
    
    def __init__(self, region: Optional[str] = None):
        """
        Initialize LayoutTools.
        
        Args:
            region: AWS region for Bedrock integration
        """
        self.region = region or AWS_REGION
        
        # Initialize Bedrock client for intelligent layout decisions
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.region)
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock client: {str(e)}")
            self.bedrock_client = None
        
        logger.info("Initialized LayoutTools")
    
    def calculate_optimal_layout(
        self,
        content_elements: List[Dict[str, Any]],
        platform: str = "general",
        canvas_size: Optional[Tuple[int, int]] = None
    ) -> LayoutSpecification:
        """
        Calculate optimal layout for given content elements.
        
        Args:
            content_elements: List of content elements to layout
            platform: Target platform for optimization
            canvas_size: Optional custom canvas size
            
        Returns:
            Complete layout specification
        """
        try:
            logger.info(f"Calculating optimal layout for platform: {platform}")
            
            # Get platform specifications
            platform_spec = PLATFORM_SPECS.get(platform.lower(), PLATFORM_SPECS["general"])
            
            # Determine canvas size
            if canvas_size is None:
                canvas_size = platform_spec["dimensions"]
            
            # Calculate grid system
            grid_system = self._calculate_grid_system(canvas_size, len(content_elements))
            
            # Position elements using grid
            layout_elements = self._position_elements_on_grid(
                content_elements, grid_system, platform_spec
            )
            
            # Generate color scheme
            color_scheme = self._generate_color_scheme(platform)
            
            # Create layout specification
            layout_spec = LayoutSpecification(
                canvas_size=canvas_size,
                elements=layout_elements,
                color_scheme=color_scheme,
                platform_optimizations=self._get_platform_optimizations(platform),
                margins=platform_spec.get("margins", LAYOUT_MARGINS)
            )
            
            # Validate layout
            self._validate_layout(layout_spec)
            
            logger.info(f"Successfully calculated layout with {len(layout_elements)} elements")
            return layout_spec
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal layout: {str(e)}")
            raise LayoutCalculationError(f"Layout calculation failed: {str(e)}")
    
    def _calculate_grid_system(
        self, 
        canvas_size: Tuple[int, int], 
        element_count: int
    ) -> Dict[str, Any]:
        """
        Calculate grid system for layout.
        
        Args:
            canvas_size: Canvas dimensions
            element_count: Number of elements to layout
            
        Returns:
            Grid system specification
        """
        width, height = canvas_size
        
        # Calculate optimal grid dimensions based on element count
        if element_count <= 2:
            cols, rows = 1, 2
        elif element_count <= 4:
            cols, rows = 2, 2
        elif element_count <= 6:
            cols, rows = 2, 3
        elif element_count <= 9:
            cols, rows = 3, 3
        else:
            cols, rows = 4, math.ceil(element_count / 4)
        
        # Calculate cell dimensions
        cell_width = width / cols
        cell_height = height / rows
        
        return {
            "columns": cols,
            "rows": rows,
            "cell_width": cell_width,
            "cell_height": cell_height,
            "total_cells": cols * rows,
            "gutter": min(cell_width, cell_height) * 0.05  # 5% gutter
        }
    
    def _position_elements_on_grid(
        self,
        content_elements: List[Dict[str, Any]],
        grid_system: Dict[str, Any],
        platform_spec: Dict[str, Any]
    ) -> List[LayoutElement]:
        """
        Position elements on the calculated grid.
        
        Args:
            content_elements: Content elements to position
            grid_system: Grid system specification
            platform_spec: Platform-specific specifications
            
        Returns:
            List of positioned layout elements
        """
        layout_elements = []
        
        # Sort elements by priority (title first, then images, then text)
        sorted_elements = self._sort_elements_by_priority(content_elements)
        
        cols = grid_system["columns"]
        rows = grid_system["rows"]
        cell_width = grid_system["cell_width"]
        cell_height = grid_system["cell_height"]
        gutter = grid_system["gutter"]
        
        for i, element in enumerate(sorted_elements):
            if i >= cols * rows:
                break  # Skip elements that don't fit
            
            # Calculate grid position
            col = i % cols
            row = i // cols
            
            # Calculate normalized position (0-1)
            x = (col * cell_width + gutter) / platform_spec["dimensions"][0]
            y = (row * cell_height + gutter) / platform_spec["dimensions"][1]
            
            # Calculate normalized size
            element_width = (cell_width - 2 * gutter) / platform_spec["dimensions"][0]
            element_height = (cell_height - 2 * gutter) / platform_spec["dimensions"][1]
            
            # Adjust size based on element type
            if element.get("type") == "title":
                element_height *= 0.6  # Titles are typically shorter
            elif element.get("type") == "image":
                # Images might need different aspect ratios
                aspect_ratio = element.get("aspect_ratio", 1.0)
                if aspect_ratio != 1.0:
                    element_height = element_width / aspect_ratio
            
            # Create layout element
            layout_element = LayoutElement(
                element_type=self._map_element_type(element.get("type", "text")),
                position=(x, y),
                size=(element_width, element_height),
                content=element.get("content", ""),
                styling=self._generate_element_styling(element, platform_spec),
                z_index=self._calculate_z_index(element.get("type", "text"))
            )
            
            layout_elements.append(layout_element)
        
        return layout_elements
    
    def _sort_elements_by_priority(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort elements by layout priority.
        
        Args:
            elements: List of content elements
            
        Returns:
            Sorted list of elements
        """
        priority_order = {
            "title": 0,
            "subtitle": 1,
            "image": 2,
            "text": 3,
            "bullet_point": 4,
            "caption": 5
        }
        
        return sorted(
            elements,
            key=lambda x: priority_order.get(x.get("type", "text"), 999)
        )
    
    def _map_element_type(self, content_type: str) -> ElementType:
        """
        Map content type to ElementType enum.
        
        Args:
            content_type: Content type string
            
        Returns:
            ElementType enum value
        """
        type_mapping = {
            "title": ElementType.TEXT,
            "subtitle": ElementType.TEXT,
            "text": ElementType.TEXT,
            "bullet_point": ElementType.TEXT,
            "caption": ElementType.TEXT,
            "image": ElementType.IMAGE,
            "background": ElementType.BACKGROUND,
            "shape": ElementType.SHAPE
        }
        
        return type_mapping.get(content_type, ElementType.TEXT)
    
    def _generate_element_styling(
        self, 
        element: Dict[str, Any], 
        platform_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate styling for a layout element.
        
        Args:
            element: Element data
            platform_spec: Platform specifications
            
        Returns:
            Styling dictionary
        """
        element_type = element.get("type", "text")
        
        # Base styling
        styling = {
            "font_family": "Arial",
            "font_weight": "normal",
            "text_align": "left",
            "color": "#333333",
            "background_color": "transparent",
            "border": "none",
            "padding": 10
        }
        
        # Type-specific styling
        if element_type == "title":
            styling.update({
                "font_size": platform_spec.get("title_size", 32),
                "font_weight": "bold",
                "text_align": "center",
                "color": "#2E86AB"
            })
        elif element_type == "subtitle":
            styling.update({
                "font_size": platform_spec.get("subtitle_size", 24),
                "font_weight": "semibold",
                "text_align": "center",
                "color": "#A23B72"
            })
        elif element_type == "text":
            styling.update({
                "font_size": platform_spec.get("body_size", 16),
                "text_align": "left"
            })
        elif element_type == "bullet_point":
            styling.update({
                "font_size": platform_spec.get("body_size", 16),
                "text_align": "left",
                "list_style": "bullet"
            })
        elif element_type == "image":
            styling.update({
                "object_fit": "cover",
                "border_radius": 8
            })
        
        return styling
    
    def _calculate_z_index(self, element_type: str) -> int:
        """
        Calculate z-index for element layering.
        
        Args:
            element_type: Type of element
            
        Returns:
            Z-index value
        """
        z_index_map = {
            "background": 0,
            "shape": 1,
            "image": 2,
            "text": 3,
            "title": 4,
            "subtitle": 4
        }
        
        return z_index_map.get(element_type, 2)
    
    def _generate_color_scheme(self, platform: str) -> ColorScheme:
        """
        Generate appropriate color scheme for platform.
        
        Args:
            platform: Target platform
            
        Returns:
            ColorScheme object
        """
        # Use Bedrock for intelligent color scheme generation if available
        if self.bedrock_client:
            try:
                intelligent_scheme = self._generate_intelligent_color_scheme(platform)
                if intelligent_scheme:
                    return intelligent_scheme
            except Exception as e:
                logger.warning(f"Failed to generate intelligent color scheme: {str(e)}")
        
        # Fallback to default schemes
        scheme_name = "professional"  # Default
        
        # Platform-specific scheme selection
        if platform.lower() == "whatsapp":
            scheme_name = "modern"
        elif platform.lower() == "twitter":
            scheme_name = "corporate"
        elif platform.lower() == "discord":
            scheme_name = "modern"
        
        scheme_data = DEFAULT_COLOR_SCHEMES.get(scheme_name, DEFAULT_COLOR_SCHEMES["professional"])
        
        return ColorScheme(
            primary=scheme_data["primary"],
            secondary=scheme_data["secondary"],
            accent=scheme_data["accent"],
            background=scheme_data["background"],
            text=scheme_data["text"]
        )
    
    def _generate_intelligent_color_scheme(self, platform: str) -> Optional[ColorScheme]:
        """
        Generate color scheme using AWS Bedrock intelligence.
        
        Args:
            platform: Target platform
            
        Returns:
            ColorScheme object or None if generation fails
        """
        try:
            prompt = f"""Generate an optimal color scheme for an infographic targeting {platform}.
            
            Consider:
            - Platform-specific design trends and user preferences
            - Accessibility and readability requirements
            - Professional appearance and brand safety
            - Color psychology for effective communication
            
            Provide a JSON response with these hex color codes:
            - primary: Main brand/accent color
            - secondary: Supporting color
            - accent: Highlight color for important elements
            - background: Background color
            - text: Primary text color
            
            Ensure high contrast ratios for accessibility."""
            
            response = self.bedrock_client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                }),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', [{}])[0].get('text', '')
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                color_data = json.loads(json_match.group())
                
                return ColorScheme(
                    primary=color_data.get("primary", "#2E86AB"),
                    secondary=color_data.get("secondary", "#A23B72"),
                    accent=color_data.get("accent", "#F18F01"),
                    background=color_data.get("background", "#FFFFFF"),
                    text=color_data.get("text", "#333333")
                )
            
        except Exception as e:
            logger.warning(f"Intelligent color scheme generation failed: {str(e)}")
        
        return None
    
    def _get_platform_optimizations(self, platform: str) -> Dict[str, Any]:
        """
        Get platform-specific optimizations.
        
        Args:
            platform: Target platform
            
        Returns:
            Platform optimization settings
        """
        platform_spec = PLATFORM_SPECS.get(platform.lower(), PLATFORM_SPECS["general"])
        
        return {
            "aspect_ratio": platform_spec.get("aspect_ratio", 16/9),
            "max_elements": platform_spec.get("max_elements", 10),
            "preferred_layout": platform_spec.get("preferred_layout", "landscape"),
            "text_size_range": {
                "min": platform_spec.get("min_text_size", 8),
                "max": platform_spec.get("max_text_size", 24)
            },
            "margins": platform_spec.get("margins", LAYOUT_MARGINS),
            "spacing": ELEMENT_SPACING
        }
    
    def _validate_layout(self, layout_spec: LayoutSpecification) -> None:
        """
        Validate layout specification.
        
        Args:
            layout_spec: Layout specification to validate
            
        Raises:
            LayoutCalculationError: If validation fails
        """
        try:
            # Validate using utility function
            # Basic validation - layout_spec should have dimensions and sections
            if not hasattr(layout_spec, 'dimensions') or not hasattr(layout_spec, 'sections'):
                raise ValueError("Invalid layout specification structure")
            
            # Additional custom validations
            if len(layout_spec.elements) == 0:
                raise ValueError("Layout must contain at least one element")
            
            # Check for overlapping elements
            self._check_element_overlaps(layout_spec.elements)
            
        except Exception as e:
            raise LayoutCalculationError(f"Layout validation failed: {str(e)}")
    
    def _check_element_overlaps(self, elements: List[LayoutElement]) -> None:
        """
        Check for overlapping elements in layout.
        
        Args:
            elements: List of layout elements
            
        Raises:
            ValueError: If significant overlaps are detected
        """
        for i, elem1 in enumerate(elements):
            for j, elem2 in enumerate(elements[i+1:], i+1):
                if self._elements_overlap(elem1, elem2):
                    logger.warning(f"Elements {i} and {j} overlap significantly")
    
    def _elements_overlap(self, elem1: LayoutElement, elem2: LayoutElement) -> bool:
        """
        Check if two elements overlap significantly.
        
        Args:
            elem1: First element
            elem2: Second element
            
        Returns:
            True if elements overlap significantly
        """
        x1, y1 = elem1.position
        w1, h1 = elem1.size
        
        x2, y2 = elem2.position
        w2, h2 = elem2.size
        
        # Calculate overlap area
        overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = overlap_x * overlap_y
        
        # Calculate element areas
        area1 = w1 * h1
        area2 = w2 * h2
        
        # Check if overlap is more than 20% of either element
        return overlap_area > 0.2 * min(area1, area2)
    
    def adjust_layout_for_content(
        self,
        layout_spec: LayoutSpecification,
        content_analysis: Dict[str, Any]
    ) -> LayoutSpecification:
        """
        Adjust layout based on content analysis.
        
        Args:
            layout_spec: Base layout specification
            content_analysis: Content analysis results
            
        Returns:
            Adjusted layout specification
        """
        try:
            logger.info("Adjusting layout based on content analysis")
            
            # Create a copy of the layout
            adjusted_elements = []
            
            for element in layout_spec.elements:
                adjusted_element = LayoutElement(
                    element_type=element.element_type,
                    position=element.position,
                    size=element.size,
                    content=element.content,
                    styling=element.styling.copy(),
                    z_index=element.z_index
                )
                
                # Adjust based on content characteristics
                if content_analysis.get("complexity_level") == "high":
                    # Reduce font sizes for complex content
                    if "font_size" in adjusted_element.styling:
                        adjusted_element.styling["font_size"] *= 0.9
                
                if content_analysis.get("tone") == "formal":
                    # Use more conservative styling
                    adjusted_element.styling["color"] = "#2D3436"
                elif content_analysis.get("tone") == "creative":
                    # Use more vibrant colors
                    adjusted_element.styling["color"] = "#6C5CE7"
                
                adjusted_elements.append(adjusted_element)
            
            # Create adjusted layout specification
            adjusted_layout = LayoutSpecification(
                canvas_size=layout_spec.canvas_size,
                elements=adjusted_elements,
                color_scheme=layout_spec.color_scheme,
                platform_optimizations=layout_spec.platform_optimizations,
                margins=layout_spec.margins
            )
            
            logger.info("Successfully adjusted layout for content")
            return adjusted_layout
            
        except Exception as e:
            logger.error(f"Failed to adjust layout: {str(e)}")
            return layout_spec  # Return original on failure
    
    def calculate_responsive_breakpoints(
        self,
        base_layout: LayoutSpecification
    ) -> Dict[str, LayoutSpecification]:
        """
        Calculate responsive layout breakpoints for different screen sizes.
        
        Args:
            base_layout: Base layout specification
            
        Returns:
            Dictionary of breakpoint layouts
        """
        breakpoints = {}
        
        # Define breakpoint sizes
        breakpoint_sizes = {
            "mobile": (480, 640),
            "tablet": (768, 1024),
            "desktop": (1200, 800)
        }
        
        for breakpoint, size in breakpoint_sizes.items():
            try:
                # Scale elements for different sizes
                scaled_elements = []
                scale_x = size[0] / base_layout.canvas_size[0]
                scale_y = size[1] / base_layout.canvas_size[1]
                
                for element in base_layout.elements:
                    scaled_element = LayoutElement(
                        element_type=element.element_type,
                        position=element.position,  # Keep normalized positions
                        size=element.size,  # Keep normalized sizes
                        content=element.content,
                        styling=self._scale_element_styling(element.styling, min(scale_x, scale_y)),
                        z_index=element.z_index
                    )
                    scaled_elements.append(scaled_element)
                
                breakpoints[breakpoint] = LayoutSpecification(
                    canvas_size=size,
                    elements=scaled_elements,
                    color_scheme=base_layout.color_scheme,
                    platform_optimizations=base_layout.platform_optimizations,
                    margins=base_layout.margins
                )
                
            except Exception as e:
                logger.warning(f"Failed to create {breakpoint} breakpoint: {str(e)}")
        
        return breakpoints
    
    def _scale_element_styling(self, styling: Dict[str, Any], scale_factor: float) -> Dict[str, Any]:
        """
        Scale element styling for responsive design.
        
        Args:
            styling: Original styling
            scale_factor: Scaling factor
            
        Returns:
            Scaled styling dictionary
        """
        scaled_styling = styling.copy()
        
        # Scale font sizes
        if "font_size" in scaled_styling:
            scaled_styling["font_size"] = max(8, int(scaled_styling["font_size"] * scale_factor))
        
        # Scale padding
        if "padding" in scaled_styling:
            scaled_styling["padding"] = max(5, int(scaled_styling["padding"] * scale_factor))
        
        return scaled_styling


def create_layout_tools(region: Optional[str] = None) -> LayoutTools:
    """
    Factory function to create LayoutTools instance.
    
    Args:
        region: Optional AWS region
        
    Returns:
        Configured LayoutTools instance
    """
    return LayoutTools(region=region)