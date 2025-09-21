"""
Simplified data models for clean agent-to-agent communication
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel


class PlatformType(str, Enum):
    """Supported social media platforms"""
    WHATSAPP = "whatsapp"
    TWITTER = "twitter"
    DISCORD = "discord"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    GENERAL = "general"


class ImageFormat(str, Enum):
    """Supported image formats"""
    PNG = "PNG"
    JPEG = "JPEG"


# Core data models for agent communication

@dataclass
class InfographicRequest:
    """Initial request for infographic generation"""
    content: str
    platform: str
    

@dataclass  
class AnalyzedContent:
    """Output from ContentAnalyzer agent"""
    key_points: List[str]
    title: str
    structure: Dict[str, Any]
    

@dataclass
class ImageAsset:
    """Output from ImageSourcer agent"""
    url: str
    description: str
    

@dataclass
class LayoutSpec:
    """Output from DesignLayout agent"""
    dimensions: Tuple[int, int]
    sections: List[Dict[str, Any]]
    

@dataclass
class FormattedText:
    """Output from TextFormatter agent"""
    elements: List[Dict[str, Any]]
    styling: Dict[str, Any]
    

@dataclass
class FinalInfographic:
    """Output from ImageComposer agent"""
    image_url: str
    metadata: Dict[str, Any]
    

# Agent response wrapper for consistent communication

class AgentResponse(BaseModel):
    """Standard response wrapper for all agents"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    

# Legacy types for backward compatibility (to be removed in future versions)

@dataclass
class InfographicResult:
    """Legacy result type - use FinalInfographic instead"""
    image_path: str
    s3_url: str
    metadata: Dict[str, Any]