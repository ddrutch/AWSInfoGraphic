"""
Minimal ImageComposer agent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to image composition tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, Optional, List

try:
    from strands import Agent
    from strands.models import BedrockModel
except Exception:
    # Provide lightweight shims so the ImageComposer can be exercised
    # locally without the Strands SDK or Bedrock access. The shimbed
    # Agent simply calls the image composition tools directly.
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
            # Minimal prompt parsing: extract layout spec, text specs, and image specs from the prompt
            import re
            from tools.image_composition_tools import (
                compose_final_infographic,
                validate_final_output,
            )

            # Parse layout spec from prompt
            layout_match = re.search(r"Layout Specification:\s*(\{.*?\})", prompt, re.S)
            if layout_match:
                import json
                try:
                    layout_spec = json.loads(layout_match.group(1))
                except:
                    layout_spec = {"canvas_size": [1200, 800], "color_scheme": {"background": "#FFFFFF"}}
            else:
                layout_spec = {"canvas_size": [1200, 800], "color_scheme": {"background": "#FFFFFF"}}

            # Parse text specs
            text_match = re.search(r"Text Elements:\s*(\[.*?\])", prompt, re.S)
            if text_match:
                try:
                    text_specs = json.loads(text_match.group(1))
                except:
                    text_specs = [{"text": "Sample Text", "position": [0.1, 0.1], "font_size": 24}]
            else:
                text_specs = [{"text": "Sample Text", "position": [0.1, 0.1], "font_size": 24}]

            # Parse image specs
            image_match = re.search(r"Image Assets:\s*(\[.*?\])", prompt, re.S)
            if image_match:
                try:
                    image_specs = json.loads(image_match.group(1))
                except:
                    image_specs = []
            else:
                image_specs = []

            # Parse platform
            platform_match = re.search(r"for (\w+) platform", prompt, re.I)
            platform = platform_match.group(1) if platform_match else "general"

            # Use the existing tools (they have local fallbacks) to produce
            # a structured response resembling what the full agent would return.
            composition_result = compose_final_infographic(
                layout_spec=layout_spec,
                text_specs=text_specs,
                image_specs=image_specs,
                platform=platform
            )

            # Validate the result
            if composition_result.get("success") and composition_result.get("image_url"):
                validation_result = validate_final_output(
                    composition_result["image_url"],
                    platform
                )
                composition_result["validation"] = validation_result

            return composition_result


logger = logging.getLogger(__name__)


class ImageComposer:
    """
    Minimal ImageComposer agent focused on orchestration and reasoning.

    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """

    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize ImageComposer agent with tools."""
        self.model_id = model_id or "us-east-1"
        self.region = region or "us-east-1"

        # Try to initialize with real SDK, fall back to shim
        try:
            from strands.models import BedrockModel
            from strands import Agent
            from tools.image_composition_tools import get_image_composition_tools
            from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

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

        except Exception as e:
            # Fall back to shim
            logger.warning(f"Using ImageComposer shim due to: {e}")
            from tools.image_composition_tools import get_image_composition_tools
            tools = get_image_composition_tools()
            self.agent = AgentShim(
                name="image_composer",
                system_prompt="Image composition expert",
                tools=tools
            )

    async def process(
        self,
        layout_spec: Dict[str, Any],
        text_specs: List[Dict[str, Any]],
        image_specs: List[Dict[str, Any]] = None,
        platform: str = "general"
    ) -> Dict[str, Any]:
        """
        Process image composition for infographic creation using AI reasoning.

        Args:
            layout_spec: Layout specification with canvas size and styling
            text_specs: Formatted text elements with positioning
            image_specs: Optional image elements with positioning
            platform: Target platform for optimization

        Returns:
            Composition results from agent reasoning
        """
        try:
            prompt = f"""Create the final infographic for {platform} platform:

Layout Specification: {layout_spec}
Text Elements: {text_specs}
Image Assets: {image_specs}

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
                "layout_spec": layout_spec
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