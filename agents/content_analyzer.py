"""
Minimal ContentAnalyzer agent for AWS Infographic Generator.

This agent uses AI reasoning through prompts and connects to content analysis tools
following AWS Strands SDK patterns for multi-agent orchestration.
"""

import logging
from typing import Any, Dict, Optional

from strands import Agent
from strands.models import BedrockModel

from tools.content_analysis_tools import get_content_analysis_tools
from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """
    Minimal ContentAnalyzer agent focused on orchestration and reasoning.
    
    Uses AI prompts for decision-making and tools for actions following
    AWS Strands SDK multi-agent patterns.
    """
    
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        """Initialize ContentAnalyzer agent with tools."""
        self.model_id = model_id or BEDROCK_MODEL_ID
        self.region = region or BEDROCK_REGION
        
        # Initialize Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.model_id
        )
        
        # Get content analysis tools
        tools = get_content_analysis_tools()
        
        # Create agent with reasoning prompt and tools
        self.agent = Agent(
            name="content_analyzer",
            system_prompt="""You are a content analysis expert for infographic creation.

Your role is to analyze text content and extract key information for visual design.

Core responsibilities:
- Analyze content structure and identify key messages
- Extract the most important points for visual representation  
- Categorize content type to guide design decisions
- Reason about optimal information hierarchy for infographics

Use your tools to:
- analyze_content_structure: Break down content into key components
- extract_key_messages: Identify the most impactful points
- categorize_content_type: Determine content category for design guidance

Focus on clarity, visual impact, and audience engagement when making decisions.
Prioritize information that translates well to visual format.""",
            model=self.bedrock_model,
            tools=tools
        )
        
        logger.info(f"ContentAnalyzer agent initialized with {len(tools)} tools")
    
    async def process(self, content: str, platform: str = "general") -> Dict[str, Any]:
        """
        Process content for infographic creation using AI reasoning.
        
        Args:
            content: Text content to analyze
            platform: Target platform for optimization
            
        Returns:
            Analysis results from agent reasoning
        """
        try:
            prompt = f"""Analyze this content for {platform} infographic creation:

Content: {content}

Please:
1. Analyze the content structure and extract key points
2. Identify the most important messages for visual representation
3. Categorize the content type to guide design decisions
4. Provide recommendations for infographic structure and hierarchy

Focus on what will work best visually for the {platform} platform."""
            
            response = await self.agent.invoke_async(prompt)
            
            return {
                "success": True,
                "analysis": response,
                "platform": platform,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }


def create_content_analyzer_agent(
    model_id: Optional[str] = None,
    region: Optional[str] = None
) -> ContentAnalyzer:
    """
    Factory function to create ContentAnalyzer agent.
    
    Args:
        model_id: Optional Bedrock model ID
        region: Optional AWS region
        
    Returns:
        Configured ContentAnalyzer agent instance
    """
    return ContentAnalyzer(model_id=model_id, region=region)