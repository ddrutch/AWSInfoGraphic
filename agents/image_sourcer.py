"""
Minimal ImageSourcer agent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to image sourcing tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, Optional

try:
    from strands import Agent
    from strands.models import BedrockModel
except Exception:
    # Provide lightweight shims so the ImageSourcer can be exercised
    # locally without the Strands SDK or Bedrock access. The shimbed
    # Agent simply calls the image sourcing tools directly.
    Agent = None
    class BedrockModel:  # simple placeholder
        def __init__(self, model_id=None):
            self.model_id = model_id


    class AgentShim:
        def __init__(self, name: str, system_prompt: str = None, model: Any = None, tools: Optional[list] = None):
            self.name = name
            self.system_prompt = system_prompt
            self.model = model
            # tools is a list of callables; we keep reference for completeness
            self.tools = tools or []

        async def invoke_async(self, prompt: str):
            # Minimal prompt parsing: extract content analysis from the prompt
            import re
            from tools.image_sourcing_tools import (
                source_images,
            )

            # Parse content analysis from prompt
            content_match = re.search(r"Content Analysis:\s*(\{.*?\})", prompt, re.S)
            if content_match:
                import json
                try:
                    content_analysis = json.loads(content_match.group(1))
                except:
                    content_analysis = {"main_topic": "sample topic", "key_points": ["point 1"]}
            else:
                content_analysis = {"main_topic": "sample topic", "key_points": ["point 1"]}

            # Use the existing tools (they have local fallbacks) to produce
            # a structured response resembling what the full agent would return.
            images = await source_images(content_analysis.get('main_topic', 'infographic'), count=2)

            return images

    Agent = AgentShim

from tools.image_sourcing_tools import get_image_sourcing_tools
from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)


class ImageSourcer:
    """
    Minimal ImageSourcer agent focused on orchestration and reasoning.
    
    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """
    
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize ImageSourcer agent with tools."""
        self.model_id = model_id or BEDROCK_MODEL_ID
        self.region = region or BEDROCK_REGION
        
        # Initialize Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.model_id
        )
        
        # Get image sourcing tools
        tools = get_image_sourcing_tools()
        
        # Create agent with reasoning prompt and tools
        self.agent = Agent(
            name="image_sourcer",
            system_prompt="""You are an image sourcing expert for infographic creation.

Your role is to generate and source appropriate images that enhance visual storytelling.

Core responsibilities:
- Analyze content to determine optimal visual elements
- Generate images using Nova Canvas that support the message
- Validate images meet platform requirements and quality standards
- Reason about visual metaphors and composition for maximum impact

Use your tools to:
- generate_image_with_nova: Create images using Amazon Nova Canvas
- create_image_prompt: Craft optimized prompts for image generation
- validate_generated_image: Ensure images meet platform specifications
- get_fallback_image: Provide alternatives when generation fails

Focus on visual storytelling, platform optimization, and professional aesthetics.
Consider how images will work within the overall infographic layout and design.""",
            model=self.bedrock_model,
            tools=tools
        )
        
        logger.info(f"ImageSourcer agent initialized with {len(tools)} tools")
    
    async def process(self, content_analysis: Dict[str, Any], platform: str = "general") -> Dict[str, Any]:
        """
        Process content analysis to source appropriate images using AI reasoning.
        
        Args:
            content_analysis: Analysis results from ContentAnalyzer
            platform: Target platform for optimization
            
        Returns:
            Image sourcing results from agent reasoning
        """
        try:
            prompt = f"""Source images for {platform} infographic based on this content analysis:

Content Analysis: {content_analysis}

Please:
1. Analyze what visual elements would best support this content
2. Generate 2-3 relevant images using Nova Canvas
3. Validate images meet platform requirements
4. Provide fallback options if generation fails

Consider:
- Visual metaphors that enhance understanding
- Platform-specific dimensions and style requirements
- Professional aesthetic suitable for infographics
- How images will integrate with text and layout

Focus on creating visually compelling images that support the message."""
            
            response = await self.agent.invoke_async(prompt)
            
            return {
                "success": True,
                "images": response,
                "platform": platform,
                "content_topic": content_analysis.get("main_topic", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Image sourcing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }


def create_image_sourcer_agent(
    model_id: Optional[str] = None,
    region: Optional[str] = None
) -> ImageSourcer:
    """
    Factory function to create ImageSourcer agent.
    
    Args:
        model_id: Optional Bedrock model ID
        region: Optional AWS region
        
    Returns:
        Configured ImageSourcer agent instance
    """
    return ImageSourcer(model_id=model_id, region=region)