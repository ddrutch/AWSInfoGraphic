"""
Minimal TextFormatter agent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to text formatting tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, Optional

from strands import Agent
from strands.models import BedrockModel

from tools.text_formatting_tools import get_text_formatting_tools
from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)


class TextFormatter:
    """
    Minimal TextFormatter agent focused on orchestration and reasoning.
    
    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """
    
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize TextFormatter agent with tools."""
        self.model_id = model_id or BEDROCK_MODEL_ID
        self.region = region or BEDROCK_REGION
        
        # Initialize Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.model_id
        )
        
        # Get text formatting tools
        tools = get_text_formatting_tools()
        
        # Create agent with reasoning prompt and tools
        self.agent = Agent(
            name="text_formatter",
            system_prompt="""You are a text formatting and typography expert for infographic creation.

Your role is to create visually appealing and readable text layouts that enhance communication.

Core responsibilities:
- Apply platform-specific typography rules for optimal readability
- Calculate appropriate font sizes and hierarchies for visual impact
- Select color schemes that ensure accessibility and brand consistency
- Format text for maximum readability within layout constraints

Use your tools to:
- apply_typography_rules: Apply platform-specific typography standards
- calculate_font_sizes: Determine optimal font sizes for hierarchy
- select_color_scheme: Choose appropriate colors for text and background
- format_text_for_readability: Optimize text layout for comprehension

Focus on clarity, accessibility, and visual hierarchy when making typography decisions.
Ensure text formatting supports the overall infographic message and platform requirements.""",
            model=self.bedrock_model,
            tools=tools
        )
        
        logger.info(f"TextFormatter agent initialized with {len(tools)} tools")
    
    async def process(self, layout_spec: Dict[str, Any], platform: str = "general") -> Dict[str, Any]:
        """
        Process layout specification to create formatted text using AI reasoning.
        
        Args:
            layout_spec: Layout specification from DesignLayout agent
            platform: Target platform for optimization
            
        Returns:
            Text formatting results from agent reasoning
        """
        try:
            prompt = f"""Format text for {platform} infographic based on this layout specification:

Layout Specification: {layout_spec}

Please:
1. Apply appropriate typography rules for the platform
2. Calculate optimal font sizes for visual hierarchy
3. Select color scheme that ensures readability and accessibility
4. Format text content for maximum readability within layout constraints

Consider:
- Platform-specific typography standards and limitations
- Visual hierarchy that guides reader attention effectively
- Color contrast requirements for accessibility
- Text density and spacing for optimal comprehension

Focus on creating professional, readable text formatting that enhances the infographic message."""
            
            response = await self.agent.invoke_async(prompt)
            
            return {
                "success": True,
                "formatted_text": response,
                "platform": platform,
                "layout_elements": len(layout_spec.get("sections", []))
            }
            
        except Exception as e:
            logger.error(f"Text formatting failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }


def create_text_formatter_agent(
    model_id: Optional[str] = None,
    region: Optional[str] = None
) -> TextFormatter:
    """
    Factory function to create TextFormatter agent.
    
    Args:
        model_id: Optional Bedrock model ID
        region: Optional AWS region
        
    Returns:
        Configured TextFormatter agent instance
    """
    return TextFormatter(model_id=model_id, region=region)