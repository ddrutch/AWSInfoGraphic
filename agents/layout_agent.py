"""
Minimal LayoutAgent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to layout tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from strands import Agent
    from strands.models import BedrockModel
except Exception:
    # Provide lightweight shims so the LayoutAgent can be exercised
    # locally without the Strands SDK or Bedrock access. The shimbed
    # Agent simply calls the layout tools directly.
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
            # Minimal prompt parsing: extract content analysis and image assets from the prompt
            import re
            from tools.layout_tools import (
                suggest_layout_type,
                generate_layout_spec,
            )

            # Parse content analysis and image assets from prompt
            content_match = re.search(r"Content Analysis:\s*(\{.*?\})\s*Image Assets:\s*(\[.*?\])", prompt, re.S)
            if content_match:
                import json
                try:
                    content_analysis = json.loads(content_match.group(1))
                    image_assets = json.loads(content_match.group(2))
                except:
                    content_analysis = {"key_points": ["Sample point 1", "Sample point 2"], "content_type": "general"}
                    image_assets = [{"url": "sample.jpg", "type": "image"}]
            else:
                content_analysis = {"key_points": ["Sample point 1", "Sample point 2"], "content_type": "general"}
                image_assets = [{"url": "sample.jpg", "type": "image"}]

            # Use the existing tools (they have local fallbacks) to produce
            # a structured response resembling what the full agent would return.
            layout_type = await suggest_layout_type(content_analysis, image_assets)
            layout_spec = await generate_layout_spec(content_analysis, image_assets)

            return {
                "layout_type": layout_type,
                "layout_spec": layout_spec,
                "recommendations": [
                    "Use consistent spacing",
                    "Ensure good contrast ratios",
                    "Balance text and visual elements"
                ],
            }

    Agent = AgentShim

from tools.layout_tools import get_layout_tools
from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)


class LayoutAgent:
    """
    Minimal LayoutAgent focused on orchestration and reasoning.

    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """

    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize LayoutAgent with tools."""
        self.model_id = model_id or BEDROCK_MODEL_ID
        self.region = region or BEDROCK_REGION

        # Initialize Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.model_id
        )

        # Get layout tools
        tools = get_layout_tools()

        # Create agent with reasoning prompt and tools
        self.agent = Agent(
            name="layout_agent",
            system_prompt="""You are a layout design expert for infographic creation.

Your role is to create optimal layouts that combine content analysis and image assets
into visually appealing and effective infographic designs.

Core responsibilities:
- Suggest appropriate layout types based on content and available images
- Generate detailed layout specifications with positioning and styling
- Ensure layouts are balanced, readable, and visually engaging
- Optimize for different platforms and use cases

Use your tools to:
- suggest_layout_type: Choose the best layout structure for the content
- generate_layout_spec: Create detailed positioning and styling specifications

Focus on visual hierarchy, readability, and aesthetic appeal when making decisions.
Consider how text and images work together to communicate the message effectively.""",
            model=self.bedrock_model,
            tools=tools
        )

        logger.info(f"LayoutAgent initialized with {len(tools)} tools")

    async def process(self, content_analysis: Dict[str, Any], image_assets: List[Dict[str, Any]], platform: str = "general") -> Dict[str, Any]:
        """
        Process content analysis and image assets to generate layout specifications.

        Args:
            content_analysis: Results from content analyzer
            image_assets: List of image assets from image sourcing
            platform: Target platform for optimization

        Returns:
            Layout specification results from agent reasoning
        """
        try:
            prompt = f"""Design an optimal layout for {platform} infographic:

Content Analysis: {content_analysis}

Image Assets: {image_assets}

Please:
1. Suggest the best layout type for this content and images
2. Generate a detailed layout specification with positioning and styling
3. Ensure the layout is visually balanced and effective for {platform}
4. Provide recommendations for visual hierarchy and element placement

Focus on creating a layout that effectively communicates the content visually."""

            response = await self.agent.invoke_async(prompt)

            return {
                "success": True,
                "layout": response,
                "platform": platform,
                "content_points": len(content_analysis.get('key_points', [])),
                "image_count": len(image_assets)
            }

        except Exception as e:
            logger.error(f"Layout generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }


def create_layout_agent(
    model_id: Optional[str] = None,
    region: Optional[str] = None
) -> LayoutAgent:
    """
    Factory function to create LayoutAgent.

    Args:
        model_id: Optional Bedrock model ID
        region: Optional AWS region

    Returns:
        Configured LayoutAgent instance
    """
    return LayoutAgent(model_id=model_id, region=region)