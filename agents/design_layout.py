"""
Minimal DesignLayout agent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to layout design tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, Optional

from strands import Agent
from strands.models import BedrockModel

from tools.layout_design_tools import get_layout_design_tools
from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)


class DesignLayout:
    """
    Minimal DesignLayout agent focused on orchestration and reasoning.
    
    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """
    
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize DesignLayout agent with tools."""
        self.model_id = model_id or BEDROCK_MODEL_ID
        self.region = region or BEDROCK_REGION
        
        # Initialize Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.model_id
        )
        
        # Get layout design tools
        tools = get_layout_design_tools()
        
        # Create agent with reasoning prompt and tools
        self.agent = Agent(
            name="design_layout",
            system_prompt="""You are a layout design expert for infographic creation.

Your role is to create optimal visual layouts that maximize impact and readability.

Core responsibilities:
- Analyze content structure to determine optimal visual hierarchy
- Create platform-specific layout specifications with proper dimensions
- Design element positioning that guides the viewer's eye effectively
- Ensure accessibility and readability across different platforms and devices

Use your tools to:
- create_layout_specification: Generate layout specs based on platform and content
- calculate_text_positioning: Position text elements for optimal readability
- determine_visual_hierarchy: Establish content priority and visual flow
- validate_layout_constraints: Ensure layouts meet platform requirements

Focus on visual hierarchy, balance, and platform optimization when making decisions.
Consider how users will consume content on each platform (mobile vs desktop, quick scan vs detailed read).
Prioritize clarity and visual impact while maintaining professional aesthetics.""",
            model=self.bedrock_model,
            tools=tools
        )
        
        logger.info(f"DesignLayout agent initialized with {len(tools)} tools")
    
    async def process(self, content_analysis: Dict[str, Any], images: Dict[str, Any], platform: str = "general") -> Dict[str, Any]:
        """
        Process content and images to create optimal layout using AI reasoning.
        
        Args:
            content_analysis: Analysis results from ContentAnalyzer
            images: Image results from ImageSourcer
            platform: Target platform for optimization
            
        Returns:
            Layout design results from agent reasoning
        """
        try:
            prompt = f"""Create optimal layout design for {platform} infographic:

Content Analysis: {content_analysis}
Available Images: {images}

Please:
1. Create a layout specification that works well for {platform}
2. Determine visual hierarchy based on content importance
3. Calculate optimal text positioning for readability
4. Validate the layout meets platform constraints and accessibility requirements

Consider:
- Platform-specific dimensions and viewing context
- Visual hierarchy that guides the viewer's attention
- Balance between text and visual elements
- Accessibility requirements (font sizes, contrast, spacing)
- How the layout will appear on target devices

Focus on creating a layout that maximizes visual impact while maintaining clarity."""
            
            response = await self.agent.invoke_async(prompt)
            
            return {
                "success": True,
                "layout": response,
                "platform": platform,
                "content_elements": len(content_analysis.get("key_points", []))
            }
            
        except Exception as e:
            logger.error(f"Layout design failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }


def create_design_layout_agent(
    model_id: Optional[str] = None,
    region: Optional[str] = None
) -> DesignLayout:
    """
    Factory function to create DesignLayout agent.
    
    Args:
        model_id: Optional Bedrock model ID
        region: Optional AWS region
        
    Returns:
        Configured DesignLayout agent instance
    """
    return DesignLayout(model_id=model_id, region=region)