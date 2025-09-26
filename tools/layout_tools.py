"""Layout and design tools for the Layout Agent.

These tools generate infographic layout specifications based on content analysis
and image assets. They use Bedrock for AI reasoning with demo-mode fallbacks.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from utils.constants import DEMO_MODE

try:
    from strands import tool
except Exception:
    def tool(fn=None, **kwargs):
        if fn is None:
            def _wrap(f):
                return _wrap
        return fn

logger = logging.getLogger(__name__)

_BEDROCK: Optional[Any] = None

def _get_bedrock():
    global _BEDROCK
    if _BEDROCK is None:
        from tools.bedrock_tools import BedrockTools
        _BEDROCK = BedrockTools()
    return _BEDROCK

def _local_generate_layout(content_analysis: Dict[str, Any], image_assets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Local fallback layout generation for demo mode."""
    key_points = content_analysis.get('key_points', [])
    content_type = content_analysis.get('content_type', 'general')
    num_points = len(key_points)

    # Simple heuristic layout
    if content_type == 'how-to' or num_points > 4:
        layout_type = 'vertical_list'
        sections = [{'type': 'title', 'x': 0.1, 'y': 0.1, 'width': 0.8, 'height': 0.2}]
        for i, point in enumerate(key_points[:5]):
            sections.append({'type': 'bullet', 'text': point, 'x': 0.1, 'y': 0.3 + i*0.1, 'width': 0.6, 'height': 0.08})
    else:
        layout_type = 'grid'
        sections = [{'type': 'title', 'x': 0.1, 'y': 0.1, 'width': 0.8, 'height': 0.2}]
        for i, point in enumerate(key_points[:4]):
            sections.append({'type': 'bullet', 'text': point, 'x': 0.1 + (i%2)*0.4, 'y': 0.3 + (i//2)*0.15, 'width': 0.35, 'height': 0.1})

    # Add image placements
    for i, asset in enumerate(image_assets[:3]):
        sections.append({'type': 'image', 'url': asset.get('url', ''), 'x': 0.7, 'y': 0.3 + i*0.15, 'width': 0.2, 'height': 0.1})

    return {
        'layout_type': layout_type,
        'sections': sections,
        'dimensions': {'width': 800, 'height': 600},
        'background_color': '#ffffff',
        'font_family': 'Arial',
        'raw_response': 'local_fallback'
    }

@tool
async def suggest_layout_type(content_analysis: Dict[str, Any], image_assets: List[Dict[str, Any]]) -> str:
    """Suggest the best layout type (e.g., 'vertical_list', 'grid', 'timeline') based on content."""
    if _should_use_demo_mode():
        key_points = content_analysis.get('key_points', [])
        return 'vertical_list' if len(key_points) > 3 else 'grid'

    bedrock = _get_bedrock()
    try:
        prompt = f"Suggest a layout type for an infographic with content type '{content_analysis.get('content_type', 'general')}' and {len(content_analysis.get('key_points', []))} key points. Options: vertical_list, grid, timeline, radial."
        result = await asyncio.to_thread(bedrock.analyze_content, prompt, "general")
        return str(result).lower().strip() if result else 'vertical_list'
    except Exception as e:
        logger.warning("Bedrock suggest_layout_type failed: %s", e)
        return 'vertical_list'

@tool
async def generate_layout_spec(content_analysis: Dict[str, Any], image_assets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a detailed layout specification for the infographic."""
    if _should_use_demo_mode():
        return _local_generate_layout(content_analysis, image_assets)

    bedrock = _get_bedrock()
    try:
        prompt = f"Generate a JSON layout spec for an infographic. Content: {json.dumps(content_analysis)}. Images: {json.dumps(image_assets)}. Include sections with type, position (x,y,width,height), and text/image URLs."
        result = await asyncio.to_thread(bedrock.analyze_content, prompt, "structure")
        if isinstance(result, dict):
            return result
        return _local_generate_layout(content_analysis, image_assets)
    except Exception as e:
        logger.warning("Bedrock generate_layout_spec failed: %s", e)
        return _local_generate_layout(content_analysis, image_assets)

def _should_use_demo_mode():
    return DEMO_MODE

def get_layout_tools():
    """Return list of layout tools for agent initialization."""
    return [suggest_layout_type, generate_layout_spec]