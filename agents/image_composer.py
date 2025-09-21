"""
Minimal ImageComposer agent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to image composition tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, Optional

from strands import Agent
from strands.models import BedrockModel

from tools.image_composition_tools import get_image_composition_tools
from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)


class ImageComposer:
    """
    Minimal ImageComposer agent focused on orchestration and reasoning.
    
    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """
    
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize ImageComposer agent with tools."""
        self.model_id = model_id or BEDROCK_MODEL_ID
        self.region = region or BEDROCK_REGION
        
        # Initialize Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.model_id
        )
        
        # Get image composition tools
        tools = get_image_composition_tools()
        
        # Create agent with reasoning prompt and tools
        self.agent = Agent(
            name="image_composer",
            system_prompt="""You are an image composition expert for infographic creation.

Your role is to combine all visual elements into the final infographic image.

Core responsibilities:
- Compose final infographic by combining background, text, and visual elements
- Apply visual effects and enhancements for professional appearance
- Ensure platform-specific requirements are met
- Validate final output quality and compliance

Use your tools to:
- compose_final_infographic: Combine all elements into final image
- overlay_text_on_image: Add formatted text overlays
- apply_visual_effects: Enhance with shadows, borders, and effects
- validate_final_output: Ensure quality and platform compliance
- upload_to_s3: Store and share final infographic

Focus on visual impact, readability, and professional presentation.
Ensure the final infographic meets all platform requirements and quality standards.""",
            model=self.bedrock_model,
            tools=tools
        )
        
        logger.info(f"ImageComposer agent initialized with {len(tools)} tools")
    
    async def process(
        self,
        background_image_url: str,
        text_elements: Dict[str, Any],
        layout_spec: Dict[str, Any],
        platform: str = "general"
    ) -> Dict[str, Any]:
        """
        Process image composition for infographic creation using AI reasoning.
        
        Args:
            background_image_url: URL of the background image
            text_elements: Formatted text elements with positioning
            layout_spec: Layout specification for composition
            platform: Target platform for optimization
            
        Returns:
            Composition results from agent reasoning
        """
        try:
            prompt = f"""Create the final infographic for {platform} platform:

Background Image: {background_image_url}
Text Elements: {text_elements}
Layout Specification: {layout_spec}

Please:
1. Compose the final infographic by combining all elements
2. Apply appropriate visual effects for professional appearance
3. Ensure all text overlays are properly positioned and readable
4. Validate the output meets {platform} platform requirements
5. Upload the final result to S3 for sharing

Focus on creating a visually impactful and professional infographic that effectively communicates the content."""
            
            response = await self.agent.invoke_async(prompt)
            
            return {
                "success": True,
                "composition": response,
                "platform": platform,
                "background_url": background_image_url
            }
            
        except Exception as e:
            logger.error(f"Image composition failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }


def create_image_composer_agent(
    model_id: Optional[str] = None,
    region: Optional[str] = None
) -> ImageComposer:
    """
    Factory function to create ImageComposer agent.
    
    Args:
        model_id: Optional Bedrock model ID
        region: Optional AWS region
        
    Returns:
        Configured ImageComposer agent instance
    """
    return ImageComposer(model_id=model_id, region=region)