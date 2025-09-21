"""
Configuration constants for AWS Infographic Generator
"""
import os
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Amazon Bedrock Configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

# Amazon S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "aws-infographic-generator-assets")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# Amazon Nova Canvas Configuration
NOVA_CANVAS_MODEL_ID = os.getenv("NOVA_CANVAS_MODEL_ID", "amazon.nova-canvas-v1:0")

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Image Generation Settings
DEFAULT_IMAGE_FORMAT = os.getenv("DEFAULT_IMAGE_FORMAT", "PNG")
DEFAULT_IMAGE_QUALITY = int(os.getenv("DEFAULT_IMAGE_QUALITY", "95"))
MAX_IMAGE_SIZE = os.getenv("MAX_IMAGE_SIZE", "1920x1080")

# Image Sourcing Limits
MAX_GENERATIVE_IMAGES = int(os.getenv("MAX_GENERATIVE_IMAGES", "3"))
MAX_WEB_IMAGES = int(os.getenv("MAX_WEB_IMAGES", "5"))

# Platform Specifications
PLATFORM_SPECS: Dict[str, Dict[str, any]] = {
    "whatsapp": {
        "dimensions": tuple(map(int, os.getenv("WHATSAPP_DIMENSIONS", "1080x1080").split("x"))),
        "format": "PNG",
        "aspect_ratio": 1.0,
        "max_text_size": 24,
        "min_text_size": 12,
        "title_size": 32,
        "subtitle_size": 20,
        "body_size": 16,
        "margins": {"top": 60, "bottom": 60, "left": 60, "right": 60},
        "max_elements": 8,
        "preferred_layout": "square",
        "dpi": 72,
        "compression_quality": 85,
        "max_file_size_mb": 16,
        "color_profile": "sRGB",
        "text_contrast_ratio": 4.5,
        "line_height_multiplier": 1.4,
        "character_limit": 150,
        "optimal_viewing_distance": "arm_length",
        "font_weights": ["normal", "bold"],
        "supported_formats": ["PNG", "JPEG"],
        "background_opacity": 1.0,
        "border_radius": 8,
        "shadow_enabled": True,
        "animation_support": False,
    },
    "twitter": {
        "dimensions": tuple(map(int, os.getenv("TWITTER_DIMENSIONS", "1200x675").split("x"))),
        "format": "PNG", 
        "aspect_ratio": 16/9,
        "max_text_size": 20,
        "min_text_size": 10,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 14,
        "margins": {"top": 40, "bottom": 40, "left": 50, "right": 50},
        "max_elements": 6,
        "preferred_layout": "landscape",
        "dpi": 72,
        "compression_quality": 90,
        "max_file_size_mb": 5,
        "color_profile": "sRGB",
        "text_contrast_ratio": 7.0,
        "line_height_multiplier": 1.3,
        "character_limit": 280,
        "optimal_viewing_distance": "desktop",
        "font_weights": ["normal", "bold", "medium"],
        "supported_formats": ["PNG", "JPEG", "GIF"],
        "background_opacity": 1.0,
        "border_radius": 12,
        "shadow_enabled": False,
        "animation_support": True,
    },
    "discord": {
        "dimensions": tuple(map(int, os.getenv("DISCORD_DIMENSIONS", "1920x1080").split("x"))),
        "format": "PNG",
        "aspect_ratio": 16/9,
        "max_text_size": 18,
        "min_text_size": 10,
        "title_size": 36,
        "subtitle_size": 24,
        "body_size": 16,
        "margins": {"top": 50, "bottom": 50, "left": 80, "right": 80},
        "max_elements": 10,
        "preferred_layout": "landscape",
        "dpi": 96,
        "compression_quality": 95,
        "max_file_size_mb": 8,
        "color_profile": "sRGB",
        "text_contrast_ratio": 4.5,
        "line_height_multiplier": 1.5,
        "character_limit": 2000,
        "optimal_viewing_distance": "desktop",
        "font_weights": ["normal", "bold", "light"],
        "supported_formats": ["PNG", "JPEG", "GIF", "WEBP"],
        "background_opacity": 0.95,
        "border_radius": 6,
        "shadow_enabled": True,
        "animation_support": True,
    },
    "instagram": {
        "dimensions": tuple(map(int, os.getenv("INSTAGRAM_DIMENSIONS", "1080x1080").split("x"))),
        "format": "JPEG",
        "aspect_ratio": 1.0,
        "max_text_size": 22,
        "min_text_size": 14,
        "title_size": 30,
        "subtitle_size": 22,
        "body_size": 18,
        "margins": {"top": 80, "bottom": 80, "left": 80, "right": 80},
        "max_elements": 7,
        "preferred_layout": "square",
        "dpi": 72,
        "compression_quality": 95,
        "max_file_size_mb": 30,
        "color_profile": "sRGB",
        "text_contrast_ratio": 4.5,
        "line_height_multiplier": 1.4,
        "character_limit": 125,
        "optimal_viewing_distance": "mobile",
        "font_weights": ["normal", "bold", "medium"],
        "supported_formats": ["JPEG", "PNG"],
        "background_opacity": 1.0,
        "border_radius": 0,
        "shadow_enabled": False,
        "animation_support": False,
    },
    "linkedin": {
        "dimensions": tuple(map(int, os.getenv("LINKEDIN_DIMENSIONS", "1200x627").split("x"))),
        "format": "PNG",
        "aspect_ratio": 1.91,
        "max_text_size": 18,
        "min_text_size": 12,
        "title_size": 32,
        "subtitle_size": 20,
        "body_size": 16,
        "margins": {"top": 60, "bottom": 60, "left": 80, "right": 80},
        "max_elements": 8,
        "preferred_layout": "landscape",
        "dpi": 72,
        "compression_quality": 90,
        "max_file_size_mb": 5,
        "color_profile": "sRGB",
        "text_contrast_ratio": 7.0,
        "line_height_multiplier": 1.4,
        "character_limit": 300,
        "optimal_viewing_distance": "desktop",
        "font_weights": ["normal", "bold", "medium"],
        "supported_formats": ["PNG", "JPEG"],
        "background_opacity": 1.0,
        "border_radius": 4,
        "shadow_enabled": False,
        "animation_support": False,
    },
    "reddit": {
        "dimensions": tuple(map(int, os.getenv("REDDIT_DIMENSIONS", "1200x630").split("x"))),
        "format": "PNG",
        "aspect_ratio": 1.9,
        "max_text_size": 16,
        "min_text_size": 10,
        "title_size": 28,
        "subtitle_size": 18,
        "body_size": 14,
        "margins": {"top": 40, "bottom": 40, "left": 60, "right": 60},
        "max_elements": 9,
        "preferred_layout": "landscape",
        "dpi": 72,
        "compression_quality": 85,
        "max_file_size_mb": 20,
        "color_profile": "sRGB",
        "text_contrast_ratio": 4.5,
        "line_height_multiplier": 1.3,
        "character_limit": 500,
        "optimal_viewing_distance": "desktop",
        "font_weights": ["normal", "bold"],
        "supported_formats": ["PNG", "JPEG", "GIF"],
        "background_opacity": 1.0,
        "border_radius": 8,
        "shadow_enabled": True,
        "animation_support": True,
    },
    "general": {
        "dimensions": tuple(map(int, os.getenv("GENERAL_DIMENSIONS", "1920x1080").split("x"))),
        "format": "PNG",
        "aspect_ratio": 16/9,
        "max_text_size": 16,
        "min_text_size": 8,
        "title_size": 40,
        "subtitle_size": 28,
        "body_size": 18,
        "margins": {"top": 50, "bottom": 50, "left": 50, "right": 50},
        "max_elements": 12,
        "preferred_layout": "landscape",
        "dpi": 96,
        "compression_quality": 95,
        "max_file_size_mb": 10,
        "color_profile": "sRGB",
        "text_contrast_ratio": 4.5,
        "line_height_multiplier": 1.4,
        "character_limit": 1000,
        "optimal_viewing_distance": "desktop",
        "font_weights": ["normal", "bold", "light", "medium"],
        "supported_formats": ["PNG", "JPEG", "PDF"],
        "background_opacity": 1.0,
        "border_radius": 0,
        "shadow_enabled": False,
        "animation_support": False,
    },
}

# Color Schemes
DEFAULT_COLOR_SCHEMES = {
    "professional": {
        "primary": "#2E86AB",
        "secondary": "#A23B72", 
        "accent": "#F18F01",
        "background": "#FFFFFF",
        "text": "#333333",
    },
    "modern": {
        "primary": "#6C5CE7",
        "secondary": "#A29BFE",
        "accent": "#FD79A8",
        "background": "#F8F9FA",
        "text": "#2D3436",
    },
    "corporate": {
        "primary": "#0984E3",
        "secondary": "#74B9FF",
        "accent": "#00B894",
        "background": "#FFFFFF",
        "text": "#2D3436",
    },
}

# Font Configuration
DEFAULT_FONTS = {
    "title": {"family": "Arial", "size": 32, "weight": "bold"},
    "subtitle": {"family": "Arial", "size": 24, "weight": "normal"},
    "body": {"family": "Arial", "size": 16, "weight": "normal"},
    "caption": {"family": "Arial", "size": 12, "weight": "normal"},
}

# Layout Configuration
LAYOUT_MARGINS = {
    "top": 50,
    "bottom": 50,
    "left": 50,
    "right": 50,
}

ELEMENT_SPACING = {
    "title_to_content": 30,
    "content_to_content": 20,
    "image_to_text": 15,
}

# Development Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MOCK_AWS_SERVICES = os.getenv("MOCK_AWS_SERVICES", "false").lower() == "true"

# Agent Configuration
AGENT_TIMEOUT = 60  # seconds
MAX_AGENT_RETRIES = 2

# File Extensions
SUPPORTED_IMAGE_FORMATS = ["PNG", "JPEG", "JPG", "PDF"]
TEMP_FILE_PREFIX = "infographic_temp_"

# Error Messages
ERROR_MESSAGES = {
    "aws_connection": "Failed to connect to AWS services. Please check your credentials.",
    "bedrock_unavailable": "Amazon Bedrock service is currently unavailable.",
    "s3_upload_failed": "Failed to upload image to S3.",
    "image_generation_failed": "Failed to generate infographic image.",
    "invalid_input": "Invalid input provided for infographic generation.",
    "content_analysis_failed": "Failed to analyze content. Please check your input.",
    "layout_generation_failed": "Failed to generate layout specification.",
    "image_sourcing_failed": "Failed to source or generate images.",
    "text_formatting_failed": "Failed to format text elements.",
    "validation_error": "Data validation failed. Please check your input parameters.",
}

# Validation Constants
VALIDATION_RULES = {
    "min_input_length": 10,
    "max_input_length": 10000,
    "min_title_length": 1,
    "max_title_length": 200,
    "max_key_points": 10,
    "min_image_size": 100,
    "max_image_size": 4000,
    "max_elements_per_layout": 15,
    "min_font_size": 8,
    "max_font_size": 72,
}

# Platform-Specific Validation Rules
PLATFORM_VALIDATION = {
    "whatsapp": {
        "max_text_length": 150,
        "min_contrast_ratio": 4.5,
        "max_elements": 8,
        "required_margins": 60,
        "max_font_size": 32,
        "min_font_size": 12,
        "aspect_ratio_tolerance": 0.05,
        "file_size_limit_mb": 16,
    },
    "twitter": {
        "max_text_length": 280,
        "min_contrast_ratio": 7.0,
        "max_elements": 6,
        "required_margins": 40,
        "max_font_size": 28,
        "min_font_size": 10,
        "aspect_ratio_tolerance": 0.1,
        "file_size_limit_mb": 5,
    },
    "discord": {
        "max_text_length": 2000,
        "min_contrast_ratio": 4.5,
        "max_elements": 10,
        "required_margins": 50,
        "max_font_size": 36,
        "min_font_size": 10,
        "aspect_ratio_tolerance": 0.1,
        "file_size_limit_mb": 8,
    },
    "instagram": {
        "max_text_length": 125,
        "min_contrast_ratio": 4.5,
        "max_elements": 7,
        "required_margins": 80,
        "max_font_size": 30,
        "min_font_size": 14,
        "aspect_ratio_tolerance": 0.05,
        "file_size_limit_mb": 30,
    },
    "linkedin": {
        "max_text_length": 300,
        "min_contrast_ratio": 7.0,
        "max_elements": 8,
        "required_margins": 60,
        "max_font_size": 32,
        "min_font_size": 12,
        "aspect_ratio_tolerance": 0.1,
        "file_size_limit_mb": 5,
    },
    "reddit": {
        "max_text_length": 500,
        "min_contrast_ratio": 4.5,
        "max_elements": 9,
        "required_margins": 40,
        "max_font_size": 28,
        "min_font_size": 10,
        "aspect_ratio_tolerance": 0.1,
        "file_size_limit_mb": 20,
    },
    "general": {
        "max_text_length": 1000,
        "min_contrast_ratio": 4.5,
        "max_elements": 12,
        "required_margins": 50,
        "max_font_size": 40,
        "min_font_size": 8,
        "aspect_ratio_tolerance": 0.2,
        "file_size_limit_mb": 10,
    },
}

# Platform-Specific Quality Checks
QUALITY_CHECKS = {
    "text_readability": {
        "min_font_size_ratio": 0.02,  # Relative to image height
        "max_line_length": 60,  # Characters per line
        "min_line_spacing": 1.2,
        "max_text_density": 0.4,  # Text area / total area
    },
    "visual_hierarchy": {
        "title_size_ratio": 2.0,  # Title vs body text
        "subtitle_size_ratio": 1.4,  # Subtitle vs body text
        "min_element_spacing": 20,  # Pixels
        "max_nesting_levels": 3,
    },
    "color_accessibility": {
        "min_contrast_normal": 4.5,
        "min_contrast_large": 3.0,
        "max_colors_per_scheme": 5,
        "color_blindness_safe": True,
    },
    "layout_balance": {
        "max_asymmetry_ratio": 0.3,
        "min_white_space_ratio": 0.2,
        "max_element_overlap": 0.05,
        "golden_ratio_preference": True,
    },
}

# Processing Timeouts (in seconds)
PROCESSING_TIMEOUTS = {
    "content_analysis": 30,
    "image_generation": 60,
    "layout_creation": 20,
    "text_formatting": 15,
    "final_composition": 45,
    "s3_upload": 30,
}

# Retry Configuration
RETRY_CONFIG = {
    "max_retries": 3,
    "base_delay": 1.0,
    "max_delay": 30.0,
    "exponential_base": 2,
    "jitter": True,
}

# Cache Configuration
CACHE_CONFIG = {
    "enable_caching": True,
    "cache_ttl": 3600,  # 1 hour
    "max_cache_size": 100,  # Maximum number of cached items
    "cache_key_prefix": "infographic_",
}

# Batch Generation Configuration
BATCH_GENERATION = {
    "default_platforms": ["whatsapp", "twitter", "instagram", "general"],
    "max_concurrent_generations": 4,
    "batch_timeout": 300,  # 5 minutes
    "retry_failed_platforms": True,
    "platform_priorities": {
        "whatsapp": 1,
        "instagram": 2,
        "twitter": 3,
        "linkedin": 4,
        "discord": 5,
        "reddit": 6,
        "general": 7,
    },
    "optimization_strategies": {
        "parallel_processing": True,
        "shared_content_analysis": True,
        "cached_image_assets": True,
        "progressive_quality": True,
        "adaptive_sizing": True,
        "smart_cropping": True,
        "format_optimization": True,
        "compression_tuning": True,
    },
    "platform_groups": {
        "mobile": ["whatsapp", "instagram"],
        "desktop": ["twitter", "linkedin", "discord", "reddit"],
        "universal": ["general"],
    },
    "adaptive_quality": {
        "high_priority": ["whatsapp", "instagram", "twitter"],
        "medium_priority": ["linkedin", "discord"],
        "low_priority": ["reddit", "general"],
    },
    "batch_processing_modes": {
        "sequential": {"max_concurrent": 1, "memory_efficient": True},
        "parallel": {"max_concurrent": 4, "speed_optimized": True},
        "adaptive": {"max_concurrent": 2, "balanced": True},
    },
    "quality_tiers": {
        "premium": {"compression": 95, "processing_time": "extended"},
        "standard": {"compression": 85, "processing_time": "normal"},
        "fast": {"compression": 75, "processing_time": "minimal"},
    },
}

# Platform-Specific Layout Templates
PLATFORM_LAYOUT_TEMPLATES = {
    "whatsapp": {
        "header_height_ratio": 0.15,
        "content_height_ratio": 0.7,
        "footer_height_ratio": 0.15,
        "grid_columns": 2,
        "grid_rows": 3,
        "preferred_elements": ["title", "key_points", "image", "call_to_action"],
        "element_priorities": {"title": 1, "image": 2, "key_points": 3, "call_to_action": 4},
        "layout_styles": ["minimal", "card", "story"],
    },
    "twitter": {
        "header_height_ratio": 0.2,
        "content_height_ratio": 0.6,
        "footer_height_ratio": 0.2,
        "grid_columns": 3,
        "grid_rows": 2,
        "preferred_elements": ["title", "subtitle", "image", "stats", "hashtags"],
        "element_priorities": {"title": 1, "image": 2, "stats": 3, "subtitle": 4, "hashtags": 5},
        "layout_styles": ["news", "quote", "statistic", "announcement"],
    },
    "instagram": {
        "header_height_ratio": 0.1,
        "content_height_ratio": 0.8,
        "footer_height_ratio": 0.1,
        "grid_columns": 3,
        "grid_rows": 3,
        "preferred_elements": ["title", "image", "key_points", "branding"],
        "element_priorities": {"image": 1, "title": 2, "key_points": 3, "branding": 4},
        "layout_styles": ["aesthetic", "lifestyle", "educational", "promotional"],
    },
    "linkedin": {
        "header_height_ratio": 0.15,
        "content_height_ratio": 0.7,
        "footer_height_ratio": 0.15,
        "grid_columns": 4,
        "grid_rows": 2,
        "preferred_elements": ["title", "subtitle", "content", "image", "company_info"],
        "element_priorities": {"title": 1, "content": 2, "image": 3, "subtitle": 4, "company_info": 5},
        "layout_styles": ["professional", "corporate", "thought_leadership", "industry_news"],
    },
    "discord": {
        "header_height_ratio": 0.1,
        "content_height_ratio": 0.8,
        "footer_height_ratio": 0.1,
        "grid_columns": 4,
        "grid_rows": 3,
        "preferred_elements": ["title", "content", "image", "reactions", "metadata"],
        "element_priorities": {"content": 1, "title": 2, "image": 3, "reactions": 4, "metadata": 5},
        "layout_styles": ["gaming", "community", "announcement", "meme"],
    },
    "reddit": {
        "header_height_ratio": 0.12,
        "content_height_ratio": 0.76,
        "footer_height_ratio": 0.12,
        "grid_columns": 3,
        "grid_rows": 2,
        "preferred_elements": ["title", "content", "image", "upvotes", "comments"],
        "element_priorities": {"title": 1, "content": 2, "image": 3, "upvotes": 4, "comments": 5},
        "layout_styles": ["discussion", "news", "meme", "educational"],
    },
    "general": {
        "header_height_ratio": 0.15,
        "content_height_ratio": 0.7,
        "footer_height_ratio": 0.15,
        "grid_columns": 4,
        "grid_rows": 4,
        "preferred_elements": ["title", "subtitle", "content", "image", "footer"],
        "element_priorities": {"title": 1, "content": 2, "image": 3, "subtitle": 4, "footer": 5},
        "layout_styles": ["presentation", "report", "infographic", "poster"],
    },
}

# Platform-Specific Typography Rules
PLATFORM_TYPOGRAPHY = {
    "whatsapp": {
        "font_families": ["Arial", "Helvetica", "Roboto"],
        "title_font": "Arial Bold",
        "body_font": "Arial Regular",
        "accent_font": "Arial Medium",
        "line_height_ratios": {"title": 1.2, "body": 1.4, "caption": 1.3},
        "letter_spacing": {"title": 0, "body": 0.5, "caption": 0.3},
        "text_alignment_preferences": ["center", "left"],
        "max_lines_per_element": {"title": 2, "body": 4, "caption": 1},
    },
    "twitter": {
        "font_families": ["Helvetica", "Arial", "Twitter Chirp"],
        "title_font": "Helvetica Bold",
        "body_font": "Helvetica Regular",
        "accent_font": "Helvetica Medium",
        "line_height_ratios": {"title": 1.1, "body": 1.3, "caption": 1.2},
        "letter_spacing": {"title": -0.5, "body": 0, "caption": 0.2},
        "text_alignment_preferences": ["left", "center"],
        "max_lines_per_element": {"title": 2, "body": 3, "caption": 1},
    },
    "instagram": {
        "font_families": ["Montserrat", "Poppins", "Arial"],
        "title_font": "Montserrat Bold",
        "body_font": "Montserrat Regular",
        "accent_font": "Montserrat SemiBold",
        "line_height_ratios": {"title": 1.2, "body": 1.4, "caption": 1.3},
        "letter_spacing": {"title": 0.5, "body": 0.3, "caption": 0.2},
        "text_alignment_preferences": ["center", "left"],
        "max_lines_per_element": {"title": 2, "body": 3, "caption": 1},
    },
    "linkedin": {
        "font_families": ["Open Sans", "Arial", "Calibri"],
        "title_font": "Open Sans Bold",
        "body_font": "Open Sans Regular",
        "accent_font": "Open Sans SemiBold",
        "line_height_ratios": {"title": 1.3, "body": 1.5, "caption": 1.4},
        "letter_spacing": {"title": 0, "body": 0.2, "caption": 0.1},
        "text_alignment_preferences": ["left", "justify"],
        "max_lines_per_element": {"title": 2, "body": 5, "caption": 2},
    },
    "discord": {
        "font_families": ["Whitney", "Helvetica", "Arial"],
        "title_font": "Whitney Bold",
        "body_font": "Whitney Regular",
        "accent_font": "Whitney Medium",
        "line_height_ratios": {"title": 1.2, "body": 1.4, "caption": 1.3},
        "letter_spacing": {"title": 0, "body": 0.1, "caption": 0.1},
        "text_alignment_preferences": ["left", "center"],
        "max_lines_per_element": {"title": 3, "body": 6, "caption": 2},
    },
    "reddit": {
        "font_families": ["Noto Sans", "Arial", "Helvetica"],
        "title_font": "Noto Sans Bold",
        "body_font": "Noto Sans Regular",
        "accent_font": "Noto Sans Medium",
        "line_height_ratios": {"title": 1.3, "body": 1.4, "caption": 1.3},
        "letter_spacing": {"title": 0, "body": 0.1, "caption": 0.1},
        "text_alignment_preferences": ["left", "justify"],
        "max_lines_per_element": {"title": 2, "body": 8, "caption": 2},
    },
    "general": {
        "font_families": ["Arial", "Helvetica", "Times New Roman"],
        "title_font": "Arial Bold",
        "body_font": "Arial Regular",
        "accent_font": "Arial Medium",
        "line_height_ratios": {"title": 1.3, "body": 1.5, "caption": 1.4},
        "letter_spacing": {"title": 0, "body": 0.2, "caption": 0.1},
        "text_alignment_preferences": ["left", "center", "justify"],
        "max_lines_per_element": {"title": 3, "body": 10, "caption": 3},
    },
}

# Platform-Specific Text Optimization Rules
PLATFORM_TEXT_OPTIMIZATION = {
    "whatsapp": {
        "readability_priority": "high",
        "font_size_scaling": 1.1,  # Slightly larger for mobile
        "line_spacing_multiplier": 1.4,
        "character_density_limit": 0.6,
        "emoji_support": True,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": False,
        "text_effects": ["shadow", "outline"],
        "accessibility_level": "enhanced",
    },
    "twitter": {
        "readability_priority": "medium",
        "font_size_scaling": 1.0,
        "line_spacing_multiplier": 1.3,
        "character_density_limit": 0.7,
        "emoji_support": True,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": True,
        "text_effects": ["shadow"],
        "accessibility_level": "standard",
    },
    "instagram": {
        "readability_priority": "medium",
        "font_size_scaling": 1.05,
        "line_spacing_multiplier": 1.4,
        "character_density_limit": 0.5,
        "emoji_support": True,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": False,
        "text_effects": ["shadow", "gradient", "outline"],
        "accessibility_level": "enhanced",
    },
    "linkedin": {
        "readability_priority": "very_high",
        "font_size_scaling": 1.0,
        "line_spacing_multiplier": 1.5,
        "character_density_limit": 0.8,
        "emoji_support": False,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": True,
        "text_effects": [],
        "accessibility_level": "enhanced",
    },
    "discord": {
        "readability_priority": "high",
        "font_size_scaling": 0.95,
        "line_spacing_multiplier": 1.4,
        "character_density_limit": 0.9,
        "emoji_support": True,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": False,
        "text_effects": ["shadow", "glow"],
        "accessibility_level": "standard",
    },
    "reddit": {
        "readability_priority": "high",
        "font_size_scaling": 1.0,
        "line_spacing_multiplier": 1.4,
        "character_density_limit": 0.85,
        "emoji_support": True,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": True,
        "text_effects": ["shadow"],
        "accessibility_level": "enhanced",
    },
    "general": {
        "readability_priority": "high",
        "font_size_scaling": 1.0,
        "line_spacing_multiplier": 1.4,
        "character_density_limit": 0.75,
        "emoji_support": True,
        "rtl_support": True,
        "text_wrapping": "word",
        "hyphenation": True,
        "text_effects": ["shadow"],
        "accessibility_level": "enhanced",
    },
}

# Platform-Specific Layout Optimization Rules
PLATFORM_LAYOUT_OPTIMIZATION = {
    "whatsapp": {
        "grid_system": {"columns": 2, "rows": 3, "gutter": 20},
        "element_spacing": {"minimum": 15, "optimal": 25, "maximum": 40},
        "visual_weight_distribution": "center_heavy",
        "content_flow": "top_to_bottom",
        "attention_zones": ["center", "top_center"],
        "safe_areas": {"top": 60, "bottom": 60, "left": 60, "right": 60},
        "responsive_breakpoints": {"small": 720, "medium": 1080},
    },
    "twitter": {
        "grid_system": {"columns": 3, "rows": 2, "gutter": 15},
        "element_spacing": {"minimum": 10, "optimal": 20, "maximum": 30},
        "visual_weight_distribution": "left_heavy",
        "content_flow": "left_to_right",
        "attention_zones": ["left_third", "center"],
        "safe_areas": {"top": 40, "bottom": 40, "left": 50, "right": 50},
        "responsive_breakpoints": {"small": 600, "medium": 1200},
    },
    "instagram": {
        "grid_system": {"columns": 3, "rows": 3, "gutter": 20},
        "element_spacing": {"minimum": 20, "optimal": 30, "maximum": 50},
        "visual_weight_distribution": "balanced",
        "content_flow": "radial",
        "attention_zones": ["center", "rule_of_thirds"],
        "safe_areas": {"top": 80, "bottom": 80, "left": 80, "right": 80},
        "responsive_breakpoints": {"small": 600, "medium": 1080},
    },
    "linkedin": {
        "grid_system": {"columns": 4, "rows": 2, "gutter": 25},
        "element_spacing": {"minimum": 15, "optimal": 25, "maximum": 35},
        "visual_weight_distribution": "top_heavy",
        "content_flow": "top_to_bottom",
        "attention_zones": ["top_left", "center"],
        "safe_areas": {"top": 60, "bottom": 60, "left": 80, "right": 80},
        "responsive_breakpoints": {"small": 600, "medium": 1200},
    },
    "discord": {
        "grid_system": {"columns": 4, "rows": 3, "gutter": 20},
        "element_spacing": {"minimum": 12, "optimal": 22, "maximum": 35},
        "visual_weight_distribution": "balanced",
        "content_flow": "flexible",
        "attention_zones": ["center", "top_center", "bottom_center"],
        "safe_areas": {"top": 50, "bottom": 50, "left": 80, "right": 80},
        "responsive_breakpoints": {"small": 960, "medium": 1920},
    },
    "reddit": {
        "grid_system": {"columns": 3, "rows": 2, "gutter": 18},
        "element_spacing": {"minimum": 10, "optimal": 18, "maximum": 28},
        "visual_weight_distribution": "left_heavy",
        "content_flow": "top_to_bottom",
        "attention_zones": ["top_left", "center_left"],
        "safe_areas": {"top": 40, "bottom": 40, "left": 60, "right": 60},
        "responsive_breakpoints": {"small": 600, "medium": 1200},
    },
    "general": {
        "grid_system": {"columns": 4, "rows": 4, "gutter": 20},
        "element_spacing": {"minimum": 15, "optimal": 25, "maximum": 40},
        "visual_weight_distribution": "balanced",
        "content_flow": "flexible",
        "attention_zones": ["center", "top_center", "rule_of_thirds"],
        "safe_areas": {"top": 50, "bottom": 50, "left": 50, "right": 50},
        "responsive_breakpoints": {"small": 800, "medium": 1920},
    },
}

# Platform-Specific Color Preferences
PLATFORM_COLOR_SCHEMES = {
    "whatsapp": {
        "brand_colors": ["#25D366", "#128C7E", "#075E54"],
        "preferred_palettes": ["green_nature", "minimal_mono", "warm_earth"],
        "avoid_colors": ["#FF0000", "#FF6B6B"],  # Avoid aggressive reds
        "contrast_requirements": "high",
        "accessibility_mode": "enhanced",
    },
    "twitter": {
        "brand_colors": ["#1DA1F2", "#14171A", "#657786"],
        "preferred_palettes": ["blue_tech", "modern_corporate", "news_professional"],
        "avoid_colors": ["#FF1744", "#E91E63"],  # Avoid competing with Twitter blue
        "contrast_requirements": "very_high",
        "accessibility_mode": "standard",
    },
    "instagram": {
        "brand_colors": ["#E4405F", "#833AB4", "#F77737"],
        "preferred_palettes": ["vibrant_gradient", "aesthetic_pastel", "lifestyle_warm"],
        "avoid_colors": ["#424242", "#616161"],  # Avoid dull grays
        "contrast_requirements": "medium",
        "accessibility_mode": "enhanced",
    },
    "linkedin": {
        "brand_colors": ["#0077B5", "#313335", "#86888A"],
        "preferred_palettes": ["professional_blue", "corporate_neutral", "business_formal"],
        "avoid_colors": ["#FF5722", "#E91E63"],  # Avoid casual/playful colors
        "contrast_requirements": "very_high",
        "accessibility_mode": "enhanced",
    },
    "discord": {
        "brand_colors": ["#5865F2", "#57F287", "#FEE75C"],
        "preferred_palettes": ["gaming_neon", "tech_dark", "community_vibrant"],
        "avoid_colors": ["#8B4513", "#A0522D"],  # Avoid earth tones
        "contrast_requirements": "high",
        "accessibility_mode": "standard",
    },
    "reddit": {
        "brand_colors": ["#FF4500", "#0079D3", "#24A0ED"],
        "preferred_palettes": ["discussion_neutral", "upvote_orange", "tech_blue"],
        "avoid_colors": ["#FF1744", "#AD1457"],  # Avoid aggressive colors
        "contrast_requirements": "high",
        "accessibility_mode": "enhanced",
    },
    "general": {
        "brand_colors": ["#2196F3", "#4CAF50", "#FF9800"],
        "preferred_palettes": ["universal_accessible", "neutral_professional", "balanced_modern"],
        "avoid_colors": [],  # No restrictions for general use
        "contrast_requirements": "medium",
        "accessibility_mode": "standard",
    },
}

# Image Processing Constants
IMAGE_PROCESSING = {
    "default_dpi": 300,
    "compression_quality": 95,
    "max_file_size_mb": 10,
    "supported_formats": ["PNG", "JPEG", "JPG", "PDF"],
    "thumbnail_size": (200, 200),
    "watermark_opacity": 0.1,
    "optimization_levels": {
        "mobile": {"dpi": 72, "quality": 85, "progressive": True},
        "web": {"dpi": 72, "quality": 90, "progressive": True},
        "desktop": {"dpi": 96, "quality": 95, "progressive": False},
        "print": {"dpi": 300, "quality": 100, "progressive": False},
    },
    "format_preferences": {
        "whatsapp": {"primary": "PNG", "fallback": "JPEG", "transparency": True},
        "twitter": {"primary": "PNG", "fallback": "JPEG", "transparency": False},
        "instagram": {"primary": "JPEG", "fallback": "PNG", "transparency": False},
        "linkedin": {"primary": "PNG", "fallback": "JPEG", "transparency": False},
        "discord": {"primary": "PNG", "fallback": "WEBP", "transparency": True},
        "reddit": {"primary": "PNG", "fallback": "JPEG", "transparency": False},
        "general": {"primary": "PNG", "fallback": "JPEG", "transparency": False},
    },
    "compression_strategies": {
        "lossless": {"png_optimize": True, "jpeg_quality": 100},
        "balanced": {"png_optimize": True, "jpeg_quality": 90},
        "aggressive": {"png_optimize": True, "jpeg_quality": 75},
    },
}