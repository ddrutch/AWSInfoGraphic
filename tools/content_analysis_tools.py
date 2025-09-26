"""Content analysis tools for the ContentAnalyzer agent.

These are implemented as async callables (decorated with `@tool` when the
Strands SDK is available). They call into the Bedrock wrapper and normalize
responses to the project's ContentAnalysis contract.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from utils.constants import DEMO_MODE

try:
    from strands import tool
except Exception:
    # Provide a no-op decorator so modules can be imported without the
    # Strands SDK (useful for unit tests and CI environments).
    def tool(fn=None, **kwargs):
        if fn is None:
            def _wrap(f):
                return f
            return _wrap
        return fn

logger = logging.getLogger(__name__)


_BEDROCK: Optional[Any] = None


def _get_bedrock():
    """Lazily create and return a BedrockTools singleton instance.

    Delays client creation until a tool is actually invoked so importing this
    module doesn't require AWS credentials to be present.
    """
    global _BEDROCK
    if _BEDROCK is None:
        # Import BedrockTools lazily to avoid requiring heavy AWS deps at
        # module import time (useful for unit tests that mock _get_bedrock).
        from tools.bedrock_tools import BedrockTools
        _BEDROCK = BedrockTools()
    return _BEDROCK


def _ensure_list(obj: Any) -> List[str]:
    """Coerce various Bedrock result shapes into a list of strings."""
    if obj is None:
        return []
    if isinstance(obj, list):
        return [str(x) for x in obj]
    if isinstance(obj, str):
        # Try parsing JSON arrays
        try:
            parsed = json.loads(obj)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
        # Fallback: split by lines
        return [line.strip() for line in obj.splitlines() if line.strip()]
    return [str(obj)]


def _local_analyze_structure(content: str) -> Dict[str, Any]:
    """Lightweight local analysis used as a fallback when Bedrock isn't available.

    Produces a reasonable ContentAnalysis-shaped dict using simple heuristics.
    """
    if not content:
        return {
            "main_topic": "",
            "key_points": [],
            "hierarchy": {},
            "summary": "",
            "suggested_title": "",
            "content_type": "general",
            "sentiment": "neutral",
            "complexity_score": 0.0,
            "estimated_reading_time": 0,
            "raw_response": "local_fallback"
        }

    # Simple sentence split
    sentences = [s.strip() for s in content.replace('\n', ' ').split('.') if s.strip()]
    main_topic = sentences[0][:80] if sentences else content[:80]

    # Key points: pick up to 5 sentences that look like bullets (contain ':' or 'use case' or are short)
    candidates = [s for s in sentences if len(s.split()) <= 20 or ':' in s.lower() or 'use case' in s.lower()]
    if not candidates:
        candidates = sentences[:5]

    key_points = [c.strip() for c in candidates][:5]

    summary = ' '.join(sentences[:2]) if sentences else content[:200]
    suggested_title = main_topic

    words = content.split()
    wcount = len(words)
    estimated_reading_time = max(1, int(wcount / 200))

    complexity_score = min(1.0, max(0.0, sum(len(w) for w in words) / (wcount * 6.0))) if wcount else 0.0

    # Lightweight content-type heuristics
    text_low = content.lower()
    if 'how to' in text_low or 'step' in text_low or 'steps' in text_low:
        content_type = 'how-to'
    elif 'news' in text_low or 'breaking' in text_low:
        content_type = 'news'
    elif 'use case' in text_low or 'use cases' in text_low:
        content_type = 'case-study'
    elif wcount < 25:
        content_type = 'snippet'
    else:
        content_type = 'general'

    return {
        "main_topic": main_topic,
        "key_points": key_points,
        "hierarchy": {},
        "summary": summary,
        "suggested_title": suggested_title,
        "content_type": content_type,
        "sentiment": "neutral",
        "complexity_score": complexity_score,
        "estimated_reading_time": estimated_reading_time,
        "raw_response": "local_fallback"
    }


def _local_extract_key_messages(content: str, max_points: int = 5) -> List[str]:
    """Extract concise key messages locally if Bedrock isn't available."""
    if not content:
        return []
    sentences = [s.strip() for s in content.replace('\n', ' ').split('.') if s.strip()]
    # Prefer short sentences and those with colon or 'use case'
    candidates = [s for s in sentences if len(s.split()) <= 20 or ':' in s.lower() or 'use case' in s.lower()]
    if not candidates:
        candidates = sentences
    messages = [c.strip() for c in candidates][:max_points]
    return messages


@tool
async def summarize_for_title(content: str, max_words: int = 8) -> str:
    """Produce a short title-like summary suitable for infographic headings.

    This is deterministic and fast; used in demo mode or as a fallback.
    """
    if not content:
        return ""
    # Prefer the first sentence, truncate to max_words
    first = content.replace('\n', ' ').split('.')[0]
    words = [w.strip() for w in first.split() if w.strip()]
    title = ' '.join(words[:max_words])
    # Capitalize nicely
    return title.strip().capitalize()


@tool
async def estimate_visual_elements(content: str) -> Dict[str, int]:
    """Estimate counts of visual elements the infographic should include.

    Returns counts for: icons, charts, bullets, images.
    """
    words = content.split()
    wcount = len(words)
    # Heuristics
    icons = min(5, max(1, wcount // 40))
    charts = 1 if any(k in content.lower() for k in ('growth', 'increase', 'percent', '%', 'chart')) else 0
    bullets = min(6, max(1, wcount // 30))
    images = 1 if wcount > 25 else 0
    return {"icons": icons, "charts": charts, "bullets": bullets, "images": images}


@tool
async def extract_metrics(content: str) -> Dict[str, Any]:
    """Find numeric metrics in text (percentages, numbers) for visualization.

    Returns a dict like {"metrics": [{"label":..., "value":..., "unit":...}, ...]}
    """
    import re
    nums = re.findall(r"(\d+[\d,]*\.?\d*%?)", content)
    metrics = []
    for n in nums:
        val = n
        unit = "%" if n.endswith('%') else None
        metrics.append({"label": n, "value": n, "unit": unit})
    return {"metrics": metrics}


@tool
async def generate_icon_prompt(keyword: str, style: str = "flat") -> str:
    """Create a short prompt to generate or search for a simple icon for a keyword.

    Useful for Nova Canvas or search queries.
    """
    return f"A simple {style} icon representing '{keyword}', minimal detail, high contrast, transparent background"


def _should_use_demo_mode():
    return DEMO_MODE


@tool
async def analyze_content_structure(content: str) -> Dict[str, Any]:
    """Analyze text content to extract key points and structure.

    Returns a normalized dictionary that follows the project's
    ContentAnalysis contract (keys present with safe defaults).
    """
    bedrock = _get_bedrock()
    if _should_use_demo_mode():
        return _local_analyze_structure(content)
    bedrock = _get_bedrock()
    try:
        result = await asyncio.to_thread(bedrock.analyze_content, content, "structure")
    except Exception as e:
        logger.warning("Bedrock analyze_content failed, using local fallback: %s", e)
        return _local_analyze_structure(content)

    if isinstance(result, dict):
        return {
            "main_topic": result.get("main_topic") or result.get("title") or "",
            "key_points": _ensure_list(result.get("key_points") or result.get("keyPoints") or []),
            "hierarchy": result.get("hierarchy") or result.get("structure") or {},
            "summary": result.get("summary") or "",
            "suggested_title": result.get("suggested_title") or result.get("suggestedTitle") or "",
            "content_type": result.get("content_type") or result.get("type") or "general",
            "sentiment": result.get("sentiment") or "neutral",
            "complexity_score": float(result.get("complexity_score") or 0.0),
            "estimated_reading_time": int(result.get("estimated_reading_time") or 0),
            "raw_response": result,
        }

    if isinstance(result, list):
        return {
            "main_topic": content.splitlines()[0][:60] if content else "",
            "key_points": _ensure_list(result),
            "hierarchy": {},
            "summary": "",
            "suggested_title": "",
            "content_type": "general",
            "sentiment": "neutral",
            "complexity_score": 0.0,
            "estimated_reading_time": 0,
            "raw_response": result,
        }

    text = str(result)
    return {
        "main_topic": content.splitlines()[0][:60] if content else "",
        "key_points": _ensure_list(text),
        "hierarchy": {},
        "summary": text[:500],
        "suggested_title": text.splitlines()[0][:60] if text else "",
        "content_type": "general",
        "sentiment": "neutral",
        "complexity_score": 0.0,
        "estimated_reading_time": 0,
        "raw_response": text,
    }


@tool
async def extract_key_messages(content: str, max_points: int = 5) -> List[str]:
    """Extract the most important messages from content.

    Returns a list of short, impactful points (length limited by `max_points`).
    """
    if _should_use_demo_mode():
        return _local_extract_key_messages(content, max_points)
    bedrock = _get_bedrock()
    try:
        result = await asyncio.to_thread(bedrock.analyze_content, content, "key_points")
    except Exception as e:
        logger.warning("Bedrock extract_key_messages failed: %s", e)
        return []

    points: List[str]
    if isinstance(result, list):
        points = [str(p).strip() for p in result]
    elif isinstance(result, dict):
        points = _ensure_list(result.get("key_points") or result.get("keyPoints") or result.get("keyPointsList") or [])
    else:
        points = _ensure_list(result)

    return [p for p in points if p][:max_points]


@tool
async def categorize_content_type(content: str) -> str:
    """Determine the type/category of the content.

    Returns a short string like 'general', 'how-to', 'news', etc.
    """
    if _should_use_demo_mode():
        return _local_analyze_structure(content).get("content_type", "general")
    bedrock = _get_bedrock()
    try:
        result = await asyncio.to_thread(bedrock.analyze_content, content, "general")
    except Exception as e:
        logger.warning("Bedrock categorize_content_type failed, using local fallback: %s", e)
        return _local_analyze_structure(content).get("content_type", "general")

    if isinstance(result, dict):
        return result.get("content_type") or result.get("type") or "general"

    text = str(result).lower()
    if "how to" in text or "step" in text:
        return "how-to"
    if "news" in text or "breaking" in text:
        return "news"
    if len(text.split()) < 20:
        return "snippet"
    return "general"


def get_content_analysis_tools():
    """Return list of content analysis tools for agent initialization."""
    return [
        analyze_content_structure,
        extract_key_messages,
        categorize_content_type,
    ]
