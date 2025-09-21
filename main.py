#!/usr/bin/env python3
"""AWS Infographic Generator - Minimal Agent Orchestrator"""

import asyncio
import logging
import sys
import argparse
from typing import Dict, Any
from datetime import datetime

from strands import Agent
from strands.models import BedrockModel

from agents.content_analyzer import create_content_analyzer_agent
from agents.image_sourcer import create_image_sourcer_agent  
from agents.design_layout import create_design_layout_agent
from agents.text_formatter import create_text_formatter_agent
from agents.image_composer import ImageComposer

from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ORCHESTRATOR_PROMPT = """You are the main orchestrator for an AI infographic generation system.

Coordinate specialized agents through intelligent reasoning:
- ContentAnalyzer: Analyzes text and extracts key information
- ImageSourcer: Generates relevant images using AWS services  
- DesignLayout: Creates optimal visual layouts
- TextFormatter: Applies typography and styling
- ImageComposer: Creates final infographic

Use AI reasoning to determine optimal workflow, coordinate agents, handle errors, and ensure quality output."""


class InfographicOrchestrator:
    """Minimal orchestrator that coordinates agents through AI reasoning."""
    
    def __init__(self):
        self.bedrock_model = BedrockModel(model_id=BEDROCK_MODEL_ID)
        
        # Initialize agents
        self.content_analyzer = create_content_analyzer_agent()
        self.image_sourcer = create_image_sourcer_agent()
        self.design_layout = create_design_layout_agent()
        self.text_formatter = create_text_formatter_agent()
        self.image_composer = ImageComposer()
        
        # Create orchestrator agent for AI reasoning
        self.agent = Agent(system_prompt=ORCHESTRATOR_PROMPT, model=self.bedrock_model)
        logger.info("Infographic Orchestrator initialized")
    
    async def generate_infographic(self, content: str, platform: str = "general", format: str = "PNG") -> Dict[str, Any]:
        """Generate infographic using AI-coordinated agent workflow."""
        try:
            start_time = datetime.now()
            logger.info(f"Starting infographic generation for {platform}")
            
            workflow_prompt = f"""Generate an infographic for this content: "{content}"
Target platform: {platform}, Output format: {format}

Coordinate the agents in optimal sequence to create a high-quality infographic."""
            
            result = await self.agent.invoke_async(workflow_prompt)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": str(result),
                "platform": platform,
                "format": format,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            return {"success": False, "error": str(e), "platform": platform, "format": format}


async def main():
    parser = argparse.ArgumentParser(description="AWS Infographic Generator")
    parser.add_argument("content", help="Text content for infographic")
    parser.add_argument("platform", nargs="?", default="general", help="Target platform")
    parser.add_argument("format", nargs="?", default="PNG", help="Output format")
    
    args = parser.parse_args()
    
    orchestrator = InfographicOrchestrator()
    result = await orchestrator.generate_infographic(args.content, args.platform, args.format)
    
    if result["success"]:
        print(f"✅ Infographic generated successfully!")
        print(f"Platform: {result['platform']}, Time: {result['processing_time']:.2f}s")
    else:
        print(f"❌ Generation failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())