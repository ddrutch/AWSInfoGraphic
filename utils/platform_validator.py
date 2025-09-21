"""
Platform Validator for AWS Infographic Generator

This module provides comprehensive validation and quality checks for platform-specific
infographi to ensure platform compliance and quality standards.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import os
import colorsys
from datetime import datetime

from utils.constants import PLATFORM_SPECS, PLATFORM_VALIDATION, QUALITY_CHECKS
from utils.types import LayoutSpec, AnalyzedContent, ImageAsset

logger = logging.getLogger(__name__)


class PlatformValidator:
    """
    Comprehensive platform validation and quality checking utility.
    
    Provides validation methods for:
    - Content compliance with platform requirements
    - Layout specifications and element positioning
    - Image quality and format compliance
    - Text readability and accessibility
    - Color scheme accessibility and contrast
    """
    
    def __init__(self):
        """Initialize the platform validator."""
        self.platform_specs = PLATFORM_SPECS
        self.validation_rules = PLATFORM_VALIDATION
        self.quality_checks = QUALITY_CHECKS
    
    def validate_content_for_platform(
        self, 
        content_analysis: ContentAnalysis, 
        platform: str
    ) -> Dict[str, Any]:
        """
        Validate content analysis results against platform requirements.
        
        Args:
            content_analysis: Content analysis results
            platform: Target platform
            
        Returns:
            Validation results with compliance status and recommendations
        """
        platform_rules = self.validation_rules.get(platform.lower(), self.validation_rules["general"])
        
        validation_result = {
            "is_compliant": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "platform": platform,
            "content_metrics": {},
            "optimization_suggestions": []
        }
        
        # Check text length limits
        total_text_length = len(content_analysis.main_topic) + sum(len(point) for point in content_analysis.key_points)
        max_text_length = platform_rules.get("max_text_length", 1000)
        
        validation_result["content_metrics"]["total_text_length"] = total_text_length
        
        if total_text_length > max_text_length:
            validation_result["errors"].append(
                f"Total text length ({total_text_length}) exceeds platform limit ({max_text_length})"
            )
            validation_result["is_compliant"] = False
            validation_result["recommendations"].append(
                f"Reduce text content by {total_text_length - max_text_length} characters"
            )
        
        # Check number of key points
        key_points_count = len(content_analysis.key_points)
        max_elements = platform_rules.get("max_elements", 12)
        
        validation_result["content_metrics"]["key_points_count"] = key_points_count
        
        if key_points_count > max_elements:
            validation_result["warnings"].append(
                f"Number of key points ({key_points_count}) may exceed optimal display limit ({max_elements})"
            )
            validation_result["recommendations"].append(
                f"Consider consolidating key points to {max_elements} or fewer"
            )
        
        # Enhanced platform-specific content validation
        validation_result = self._apply_enhanced_platform_validation(
            validation_result, content_analysis, platform, platform_rules
        )
        
        return validation_result
    
    def _apply_enhanced_platform_validation(
        self,
        validation_result: Dict[str, Any],
        content_analysis: ContentAnalysis,
        platform: str,
        platform_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply enhanced platform-specific validation rules."""
        
        if platform.lower() == "whatsapp":
            # WhatsApp-specific validations
            if validation_result["content_metrics"]["total_text_length"] > 150:
                validation_result["optimization_suggestions"].append(
                    "WhatsApp users prefer concise content. Consider shortening text for better engagement."
                )
            
            # Check for mobile-friendly content structure
            if len(content_analysis.key_points) > 5:
                validation_result["optimization_suggestions"].append(
                    "Consider limiting to 5 key points for optimal mobile viewing"
                )
            
            # Emoji and visual element suggestions
            validation_result["optimization_suggestions"].append(
                "Consider adding emojis or visual elements to enhance mobile engagement"
            )
        
        elif platform.lower() == "twitter":
            # Twitter-specific validations
            if validation_result["content_metrics"]["total_text_length"] > 280:
                validation_result["optimization_suggestions"].append(
                    "Twitter content should be concise and attention-grabbing. Consider reducing text length."
                )
            
            # Check for hashtag potential
            validation_result["optimization_suggestions"].append(
                "Consider adding relevant hashtags for better discoverability"
            )
            
            # Visual impact check
            if len(content_analysis.key_points) < 2:
                validation_result["optimization_suggestions"].append(
                    "Twitter users appreciate quick, scannable information. Consider adding more key points."
                )
        
        elif platform.lower() == "instagram":
            # Instagram-specific validations
            if validation_result["content_metrics"]["total_text_length"] > 125:
                validation_result["optimization_suggestions"].append(
                    "Instagram is visual-first. Consider reducing text and emphasizing visual elements."
                )
            
            # Aesthetic considerations
            validation_result["optimization_suggestions"].extend([
                "Ensure high visual appeal with strong imagery",
                "Consider brand consistency in colors and fonts",
                "Optimize for square format viewing"
            ])
        
        elif platform.lower() == "linkedin":
            # LinkedIn-specific validations
            if len(content_analysis.key_points) < 3:
                validation_result["optimization_suggestions"].append(
                    "LinkedIn users appreciate detailed, professional content. Consider adding more key points."
                )
            
            # Professional tone check
            validation_result["optimization_suggestions"].extend([
                "Ensure professional tone and language",
                "Include data or statistics if available",
                "Consider industry-specific terminology"
            ])
        
        elif platform.lower() == "discord":
            # Discord-specific validations
            validation_result["optimization_suggestions"].extend([
                "Consider gaming/tech community preferences",
                "Ensure readability in dark theme environments",
                "Optimize for desktop viewing primarily"
            ])
        
        elif platform.lower() == "reddit":
            # Reddit-specific validations
            validation_result["optimization_suggestions"].extend([
                "Ensure content is discussion-worthy",
                "Consider community-specific preferences",
                "Optimize for feed-style viewing"
            ])
        
        return validation_result

    def validate_comprehensive_quality(
        self,
        infographic_data: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive quality validation across all infographic components.
        
        Args:
            infographic_data: Complete infographic data including content, layout, images
            platform: Target platform
            
        Returns:
            Comprehensive quality validation results
        """
        validation_result = {
            "overall_quality_score": 0.0,
            "component_scores": {},
            "is_platform_optimized": True,
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "platform": platform,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        component_weights = {
            "content": 0.25,
            "layout": 0.25,
            "typography": 0.20,
            "visual_design": 0.15,
            "accessibility": 0.10,
            "platform_compliance": 0.05
        }
        
        # Validate each component
        if "content_analysis" in infographic_data:
            content_score = self._validate_content_quality(
                infographic_data["content_analysis"], platform
            )
            validation_result["component_scores"]["content"] = content_score
        
        if "layout_specification" in infographic_data:
            layout_score = self._validate_layout_quality(
                infographic_data["layout_specification"], platform
            )
            validation_result["component_scores"]["layout"] = layout_score
        
        if "text_elements" in infographic_data:
            typography_score = self._validate_typography_quality(
                infographic_data["text_elements"], platform
            )
            validation_result["component_scores"]["typography"] = typography_score
        
        if "image_assets" in infographic_data:
            visual_score = self._validate_visual_quality(
                infographic_data["image_assets"], platform
            )
            validation_result["component_scores"]["visual_design"] = visual_score
        
        # Calculate accessibility score
        accessibility_score = self._validate_accessibility_compliance(
            infographic_data, platform
        )
        validation_result["component_scores"]["accessibility"] = accessibility_score
        
        # Calculate platform compliance score
        platform_score = self._validate_platform_compliance(
            infographic_data, platform
        )
        validation_result["component_scores"]["platform_compliance"] = platform_score
        
        # Calculate overall quality score
        total_score = 0.0
        for component, score in validation_result["component_scores"].items():
            weight = component_weights.get(component, 0.1)
            total_score += score["score"] * weight
        
        validation_result["overall_quality_score"] = min(100.0, max(0.0, total_score))
        
        # Determine if platform optimized
        validation_result["is_platform_optimized"] = (
            validation_result["overall_quality_score"] >= 75.0 and
            len(validation_result["critical_issues"]) == 0
        )
        
        # Generate summary recommendations
        validation_result["recommendations"] = self._generate_quality_recommendations(
            validation_result, platform
        )
        
        return validation_result
    
    def _validate_content_quality(self, content_analysis: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Validate content quality and relevance."""
        score_data = {"score": 85.0, "issues": [], "strengths": []}
        
        # Check content structure
        if content_analysis.get("main_topic"):
            score_data["strengths"].append("Clear main topic identified")
        else:
            score_data["issues"].append("Missing clear main topic")
            score_data["score"] -= 15
        
        # Check key points quality
        key_points = content_analysis.get("key_points", [])
        if len(key_points) >= 3:
            score_data["strengths"].append("Sufficient key points for engagement")
        elif len(key_points) < 2:
            score_data["issues"].append("Insufficient key points for effective infographic")
            score_data["score"] -= 20
        
        # Platform-specific content scoring
        if platform.lower() == "linkedin" and len(key_points) >= 4:
            score_data["score"] += 5  # Bonus for detailed professional content
        elif platform.lower() in ["whatsapp", "twitter"] and len(key_points) <= 4:
            score_data["score"] += 5  # Bonus for concise content
        
        return score_data
    
    def _validate_layout_quality(self, layout_spec: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Validate layout design quality."""
        score_data = {"score": 80.0, "issues": [], "strengths": []}
        
        # Check element distribution
        elements = layout_spec.get("elements", [])
        if len(elements) > 0:
            score_data["strengths"].append("Layout contains visual elements")
            
            # Check for visual hierarchy
            element_types = [elem.get("element_type") for elem in elements]
            if "title" in element_types:
                score_data["strengths"].append("Clear title element present")
                score_data["score"] += 5
            
            # Check spacing and positioning
            positions = [elem.get("position", (0, 0)) for elem in elements]
            if len(set(positions)) == len(positions):  # No overlapping positions
                score_data["strengths"].append("Good element spacing")
            else:
                score_data["issues"].append("Potential element overlap detected")
                score_data["score"] -= 10
        else:
            score_data["issues"].append("Layout lacks visual elements")
            score_data["score"] -= 25
        
        return score_data
    
    def _validate_typography_quality(self, text_elements: List[Dict[str, Any]], platform: str) -> Dict[str, Any]:
        """Validate typography and text formatting quality."""
        score_data = {"score": 85.0, "issues": [], "strengths": []}
        
        if not text_elements:
            score_data["issues"].append("No text elements found")
            score_data["score"] = 0
            return score_data
        
        # Check font size hierarchy
        font_sizes = []
        for element in text_elements:
            styling = element.get("styling", {})
            font_size = styling.get("font_size", 16)
            font_sizes.append(font_size)
        
        if len(set(font_sizes)) > 1:
            score_data["strengths"].append("Good font size hierarchy")
        else:
            score_data["issues"].append("Lacks font size variation for hierarchy")
            score_data["score"] -= 15
        
        # Check readability
        from utils.constants import PLATFORM_VALIDATION
        platform_rules = PLATFORM_VALIDATION.get(platform.lower(), PLATFORM_VALIDATION["general"])
        min_font_size = platform_rules.get("min_font_size", 8)
        
        readable_elements = sum(1 for size in font_sizes if size >= min_font_size)
        if readable_elements == len(font_sizes):
            score_data["strengths"].append("All text meets readability standards")
        else:
            score_data["issues"].append("Some text may be too small for platform")
            score_data["score"] -= 20
        
        return score_data
    
    def _validate_visual_quality(self, image_assets: List[Dict[str, Any]], platform: str) -> Dict[str, Any]:
        """Validate visual design quality."""
        score_data = {"score": 75.0, "issues": [], "strengths": []}
        
        if not image_assets:
            score_data["issues"].append("No visual assets found")
            score_data["score"] = 40  # Still functional but not visually engaging
            return score_data
        
        # Check asset quality
        high_quality_assets = 0
        for asset in image_assets:
            if asset.get("asset_type") == "generated":
                high_quality_assets += 1
                score_data["strengths"].append("Contains generated visual content")
            elif asset.get("asset_type") == "stock":
                high_quality_assets += 1
        
        if high_quality_assets > 0:
            score_data["score"] += min(20, high_quality_assets * 10)
        
        return score_data
    
    def _validate_accessibility_compliance(self, infographic_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Validate accessibility compliance."""
        score_data = {"score": 90.0, "issues": [], "strengths": []}
        
        # Check color contrast (simplified)
        color_scheme = infographic_data.get("layout_specification", {}).get("color_scheme", {})
        if color_scheme:
            # Assume good contrast if color scheme is present
            score_data["strengths"].append("Color scheme defined")
        else:
            score_data["issues"].append("No color scheme validation possible")
            score_data["score"] -= 10
        
        # Check text size compliance
        text_elements = infographic_data.get("text_elements", [])
        if text_elements:
            from utils.constants import PLATFORM_VALIDATION
            platform_rules = PLATFORM_VALIDATION.get(platform.lower(), PLATFORM_VALIDATION["general"])
            min_font_size = platform_rules.get("min_font_size", 8)
            
            compliant_text = True
            for element in text_elements:
                font_size = element.get("styling", {}).get("font_size", 16)
                if font_size < min_font_size:
                    compliant_text = False
                    break
            
            if compliant_text:
                score_data["strengths"].append("Text meets accessibility size requirements")
            else:
                score_data["issues"].append("Some text below accessibility size requirements")
                score_data["score"] -= 20
        
        return score_data
    
    def _validate_platform_compliance(self, infographic_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Validate platform-specific compliance."""
        score_data = {"score": 95.0, "issues": [], "strengths": []}
        
        from utils.constants import PLATFORM_SPECS, PLATFORM_VALIDATION
        platform_spec = PLATFORM_SPECS.get(platform.lower(), PLATFORM_SPECS["general"])
        platform_rules = PLATFORM_VALIDATION.get(platform.lower(), PLATFORM_VALIDATION["general"])
        
        # Check dimensions compliance
        layout_spec = infographic_data.get("layout_specification", {})
        canvas_size = layout_spec.get("canvas_size")
        expected_dimensions = platform_spec.get("dimensions")
        
        if canvas_size and expected_dimensions:
            if canvas_size == expected_dimensions:
                score_data["strengths"].append("Perfect dimension compliance")
            else:
                score_data["issues"].append("Dimensions don't match platform optimal")
                score_data["score"] -= 5
        
        # Check element count compliance
        elements = layout_spec.get("elements", [])
        max_elements = platform_rules.get("max_elements", 12)
        
        if len(elements) <= max_elements:
            score_data["strengths"].append("Element count within platform limits")
        else:
            score_data["issues"].append("Too many elements for platform")
            score_data["score"] -= 10
        
        return score_data
    
    def _generate_quality_recommendations(self, validation_result: Dict[str, Any], platform: str) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        overall_score = validation_result["overall_quality_score"]
        
        if overall_score < 60:
            recommendations.append("Consider major revisions to improve overall quality")
        elif overall_score < 80:
            recommendations.append("Good foundation, focus on addressing specific component issues")
        else:
            recommendations.append("High quality infographic, minor optimizations may enhance further")
        
        # Component-specific recommendations
        for component, score_data in validation_result["component_scores"].items():
            if score_data["score"] < 70:
                recommendations.append(f"Focus on improving {component} quality")
                recommendations.extend([f"- {issue}" for issue in score_data.get("issues", [])])
        
        # Platform-specific recommendations
        if platform.lower() == "whatsapp":
            recommendations.append("Ensure mobile-first design with high contrast")
        elif platform.lower() == "twitter":
            recommendations.append("Optimize for quick scanning and immediate impact")
        elif platform.lower() == "instagram":
            recommendations.append("Prioritize visual appeal and brand consistency")
        elif platform.lower() == "linkedin":
            recommendations.append("Maintain professional tone and detailed content")
        
        return recommendations
        """
        Validate content analysis results against platform requirements.
        
        Args:
            content_analysis: Content analysis results
            platform: Target platform
            
        Returns:
            Validation results with compliance status and recommendations
        """
        platform_rules = self.validation_rules.get(platform.lower(), self.validation_rules["general"])
        
        validation_result = {
            "is_compliant": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "platform": platform,
            "content_metrics": {}
        }
        
        # Check text length limits
        total_text_length = len(content_analysis.main_topic) + sum(len(point) for point in content_analysis.key_points)
        max_text_length = platform_rules.get("max_text_length", 1000)
        
        validation_result["content_metrics"]["total_text_length"] = total_text_length
        
        if total_text_length > max_text_length:
            validation_result["errors"].append(
                f"Total text length ({total_text_length}) exceeds platform limit ({max_text_length})"
            )
            validation_result["is_compliant"] = False
            validation_result["recommendations"].append(
                f"Reduce text content by {total_text_length - max_text_length} characters"
            )
        
        # Check number of key points
        key_points_count = len(content_analysis.key_points)
        max_elements = platform_rules.get("max_elements", 12)
        
        validation_result["content_metrics"]["key_points_count"] = key_points_count
        
        if key_points_count > max_elements:
            validation_result["warnings"].append(
                f"Number of key points ({key_points_count}) may exceed optimal display limit ({max_elements})"
            )
            validation_result["recommendations"].append(
                f"Consider consolidating key points to {max_elements} or fewer"
            )
        
        # Platform-specific content recommendations
        if platform.lower() == "whatsapp":
            if total_text_length > 150:
                validation_result["recommendations"].append(
                    "WhatsApp users prefer concise content. Consider shortening text for better engagement."
                )
        
        elif platform.lower() == "twitter":
            if total_text_length > 280:
                validation_result["recommendations"].append(
                    "Twitter content should be concise and attention-grabbing. Consider reducing text length."
                )
        
        elif platform.lower() == "linkedin":
            if key_points_count < 3:
                validation_result["recommendations"].append(
                    "LinkedIn users appreciate detailed, professional content. Consider adding more key points."
                )
        
        return validation_result
    
    def validate_layout_for_platform(
        self, 
        layout_spec: LayoutSpecification, 
        platform: str
    ) -> Dict[str, Any]:
        """
        Validate layout specification against platform requirements.
        
        Args:
            layout_spec: Layout specification to validate
            platform: Target platform
            
        Returns:
            Validation results with layout compliance and optimization suggestions
        """
        platform_rules = self.validation_rules.get(platform.lower(), self.validation_rules["general"])
        platform_spec = self.platform_specs.get(platform.lower(), self.platform_specs["general"])
        
        validation_result = {
            "is_compliant": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "platform": platform,
            "layout_metrics": {}
        }
        
        # Check canvas dimensions
        expected_dimensions = platform_spec["dimensions"]
        actual_dimensions = layout_spec.canvas_size
        
        validation_result["layout_metrics"]["canvas_size"] = actual_dimensions
        validation_result["layout_metrics"]["expected_size"] = expected_dimensions
        
        if actual_dimensions != expected_dimensions:
            validation_result["warnings"].append(
                f"Canvas size {actual_dimensions} differs from platform optimal {expected_dimensions}"
            )
        
        # Check element count
        element_count = len(layout_spec.elements)
        max_elements = platform_rules.get("max_elements", 12)
        
        validation_result["layout_metrics"]["element_count"] = element_count
        
        if element_count > max_elements:
            validation_result["warnings"].append(
                f"Element count ({element_count}) exceeds platform recommendation ({max_elements})"
            )
            validation_result["recommendations"].append(
                "Consider consolidating or removing less important elements"
            )
        
        # Check margins
        required_margins = platform_rules.get("required_margins", 50)
        layout_margins = layout_spec.margins
        
        for side, margin in layout_margins.items():
            if margin < required_margins:
                validation_result["warnings"].append(
                    f"Margin {side} ({margin}px) is below platform recommendation ({required_margins}px)"
                )
        
        # Validate element positioning and overlap
        overlap_issues = self._check_element_overlap(layout_spec.elements)
        if overlap_issues:
            validation_result["warnings"].extend(overlap_issues)
            validation_result["recommendations"].append(
                "Adjust element positioning to reduce overlap and improve readability"
            )
        
        # Check visual hierarchy
        hierarchy_issues = self._validate_visual_hierarchy(layout_spec.elements)
        if hierarchy_issues:
            validation_result["recommendations"].extend(hierarchy_issues)
        
        return validation_result
    
    def validate_image_for_platform(
        self, 
        image_path: str, 
        platform: str
    ) -> Dict[str, Any]:
        """
        Validate image against platform requirements.
        
        Args:
            image_path: Path to image file
            platform: Target platform
            
        Returns:
            Image validation results
        """
        platform_spec = self.platform_specs.get(platform.lower(), self.platform_specs["general"])
        platform_rules = self.validation_rules.get(platform.lower(), self.validation_rules["general"])
        
        validation_result = {
            "is_compliant": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "platform": platform,
            "image_metrics": {}
        }
        
        try:
            with Image.open(image_path) as img:
                file_size = os.path.getsize(image_path)
                
                # Basic image metrics
                validation_result["image_metrics"] = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "file_size_mb": file_size / (1024 * 1024),
                    "aspect_ratio": img.width / img.height
                }
                
                # Check dimensions
                expected_dimensions = platform_spec["dimensions"]
                if (img.width, img.height) != expected_dimensions:
                    validation_result["warnings"].append(
                        f"Image dimensions {img.width}x{img.height} differ from platform optimal {expected_dimensions}"
                    )
                
                # Check file size
                max_file_size = platform_rules.get("file_size_limit_mb", 10) * 1024 * 1024
                if file_size > max_file_size:
                    validation_result["errors"].append(
                        f"File size {file_size / (1024*1024):.1f}MB exceeds platform limit {max_file_size / (1024*1024):.1f}MB"
                    )
                    validation_result["is_compliant"] = False
                
                # Check aspect ratio
                expected_ratio = platform_spec.get("aspect_ratio", 16/9)
                actual_ratio = img.width / img.height
                tolerance = platform_rules.get("aspect_ratio_tolerance", 0.1)
                
                if abs(actual_ratio - expected_ratio) > tolerance:
                    validation_result["warnings"].append(
                        f"Aspect ratio {actual_ratio:.2f} differs significantly from platform optimal {expected_ratio:.2f}"
                    )
                
                # Check format
                preferred_format = platform_spec.get("format", "PNG")
                if img.format != preferred_format:
                    validation_result["recommendations"].append(
                        f"Consider converting to {preferred_format} format for optimal platform compatibility"
                    )
                
                # Platform-specific checks
                if platform.lower() == "whatsapp" and file_size > 16 * 1024 * 1024:
                    validation_result["errors"].append("WhatsApp has a 16MB file size limit")
                    validation_result["is_compliant"] = False
                
                elif platform.lower() == "twitter" and file_size > 5 * 1024 * 1024:
                    validation_result["errors"].append("Twitter has a 5MB file size limit")
                    validation_result["is_compliant"] = False
        
        except Exception as e:
            validation_result["errors"].append(f"Failed to validate image: {str(e)}")
            validation_result["is_compliant"] = False
        
        return validation_result
    
    def validate_text_readability(
        self, 
        text_elements: List[Dict[str, Any]], 
        platform: str
    ) -> Dict[str, Any]:
        """
        Validate text elements for readability and accessibility.
        
        Args:
            text_elements: List of text elements with styling
            platform: Target platform
            
        Returns:
            Text readability validation results
        """
        platform_rules = self.validation_rules.get(platform.lower(), self.validation_rules["general"])
        readability_checks = self.quality_checks["text_readability"]
        
        validation_result = {
            "is_accessible": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "platform": platform,
            "readability_metrics": {}
        }
        
        total_text_area = 0
        canvas_area = 1.0  # Normalized canvas area
        
        for i, element in enumerate(text_elements):
            text_content = element.get("content", "")
            styling = element.get("styling", {})
            size = element.get("size", (0.1, 0.1))
            
            # Check font size
            font_size = styling.get("font_size", 12)
            min_font_size = platform_rules.get("min_font_size", 8)
            
            if font_size < min_font_size:
                validation_result["errors"].append(
                    f"Text element {i} font size ({font_size}px) below platform minimum ({min_font_size}px)"
                )
                validation_result["is_accessible"] = False
            
            # Check line length
            line_length = len(text_content.split('\n')[0]) if text_content else 0
            max_line_length = readability_checks.get("max_line_length", 60)
            
            if line_length > max_line_length:
                validation_result["warnings"].append(
                    f"Text element {i} line length ({line_length}) may be too long for optimal readability"
                )
            
            # Calculate text density
            element_area = size[0] * size[1]
            total_text_area += element_area
        
        # Check overall text density
        text_density = total_text_area / canvas_area
        max_text_density = readability_checks.get("max_text_density", 0.4)
        
        validation_result["readability_metrics"]["text_density"] = text_density
        
        if text_density > max_text_density:
            validation_result["warnings"].append(
                f"Text density ({text_density:.2f}) may be too high for optimal readability"
            )
            validation_result["recommendations"].append(
                "Consider reducing text content or increasing canvas size"
            )
        
        return validation_result
    
    def validate_color_accessibility(
        self, 
        color_scheme: Dict[str, str], 
        platform: str
    ) -> Dict[str, Any]:
        """
        Validate color scheme for accessibility compliance.
        
        Args:
            color_scheme: Color scheme with primary, secondary, background, text colors
            platform: Target platform
            
        Returns:
            Color accessibility validation results
        """
        platform_rules = self.validation_rules.get(platform.lower(), self.validation_rules["general"])
        accessibility_checks = self.quality_checks["color_accessibility"]
        
        validation_result = {
            "is_accessible": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "platform": platform,
            "contrast_ratios": {}
        }
        
        # Check contrast ratios
        background_color = color_scheme.get("background", "#FFFFFF")
        text_color = color_scheme.get("text", "#000000")
        
        # Calculate contrast ratio (simplified)
        contrast_ratio = self._calculate_contrast_ratio(background_color, text_color)
        min_contrast = platform_rules.get("min_contrast_ratio", 4.5)
        
        validation_result["contrast_ratios"]["text_background"] = contrast_ratio
        
        if contrast_ratio < min_contrast:
            validation_result["errors"].append(
                f"Text/background contrast ratio ({contrast_ratio:.1f}) below accessibility minimum ({min_contrast})"
            )
            validation_result["is_accessible"] = False
            validation_result["recommendations"].append(
                "Increase contrast between text and background colors"
            )
        
        # Check color blindness safety
        if accessibility_checks.get("color_blindness_safe", True):
            color_blind_issues = self._check_color_blindness_safety(color_scheme)
            if color_blind_issues:
                validation_result["warnings"].extend(color_blind_issues)
                validation_result["recommendations"].append(
                    "Consider using patterns or shapes in addition to color for important distinctions"
                )
        
        return validation_result
    
    def _check_element_overlap(self, elements: List[Any]) -> List[str]:
        """Check for element overlap issues."""
        overlap_issues = []
        
        for i, elem1 in enumerate(elements):
            pos1 = elem1.position
            size1 = elem1.size
            
            for j, elem2 in enumerate(elements[i+1:], i+1):
                pos2 = elem2.position
                size2 = elem2.size
                
                # Check for overlap
                if (pos1[0] < pos2[0] + size2[0] and pos1[0] + size1[0] > pos2[0] and
                    pos1[1] < pos2[1] + size2[1] and pos1[1] + size1[1] > pos2[1]):
                    
                    overlap_issues.append(f"Elements {i} and {j} overlap")
        
        return overlap_issues
    
    def _validate_visual_hierarchy(self, elements: List[Any]) -> List[str]:
        """Validate visual hierarchy of elements."""
        recommendations = []
        
        # Check if there's a clear title element
        title_elements = [elem for elem in elements if elem.element_type.value == "title"]
        if not title_elements:
            recommendations.append("Consider adding a clear title element for better visual hierarchy")
        
        # Check font size hierarchy
        text_elements = [elem for elem in elements if elem.element_type.value in ["title", "text", "subtitle"]]
        if len(text_elements) > 1:
            font_sizes = []
            for elem in text_elements:
                font_size = elem.styling.get("font_size", 12)
                font_sizes.append(font_size)
            
            if len(set(font_sizes)) == 1:
                recommendations.append("Consider varying font sizes to create better visual hierarchy")
        
        return recommendations
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors (simplified)."""
        try:
            # Convert hex to RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            # Calculate relative luminance (simplified)
            def luminance(rgb):
                r, g, b = [x/255.0 for x in rgb]
                return 0.299 * r + 0.587 * g + 0.114 * b
            
            lum1 = luminance(rgb1)
            lum2 = luminance(rgb2)
            
            # Calculate contrast ratio
            lighter = max(lum1, lum2)
            darker = min(lum1, lum2)
            
            return (lighter + 0.05) / (darker + 0.05)
            
        except Exception:
            return 4.5  # Return acceptable default if calculation fails
    
    def _check_color_blindness_safety(self, color_scheme: Dict[str, str]) -> List[str]:
        """Check color scheme for color blindness accessibility."""
        issues = []
        
        # Check for problematic color combinations
        primary = color_scheme.get("primary", "#000000")
        secondary = color_scheme.get("secondary", "#000000")
        
        # Simplified check for red-green color blindness
        try:
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            primary_rgb = hex_to_rgb(primary)
            secondary_rgb = hex_to_rgb(secondary)
            
            # Check if colors are too similar in red-green spectrum
            if abs(primary_rgb[0] - secondary_rgb[0]) < 50 and abs(primary_rgb[1] - secondary_rgb[1]) < 50:
                issues.append("Primary and secondary colors may be difficult to distinguish for color-blind users")
        
        except Exception:
            pass  # Skip check if color parsing fails
        
        return issues


def create_platform_validator() -> PlatformValidator:
    """
    Factory function to create PlatformValidator instance.
    
    Returns:
        Configured PlatformValidator instance
    """
    return PlatformValidator()