import asyncio
from unittest.mock import patch

import pytest

from tools import layout_tools as ltools


@pytest.mark.asyncio
async def test_suggest_layout_type_normal_operation():
    content_analysis = {
        "key_points": ["Point 1", "Point 2", "Point 3", "Point 4"],
        "content_type": "how-to"
    }
    image_assets = [{"url": "image1.jpg", "type": "image"}]

    fake_response = "vertical_list"

    with patch("tools.layout_tools._get_bedrock") as gb:
        class FakeBedrock:
            def analyze_content(self, prompt, analysis_type):
                return fake_response

        gb.return_value = FakeBedrock()
        result = await ltools.suggest_layout_type(content_analysis, image_assets)

    assert result == "vertical_list"


@pytest.mark.asyncio
async def test_suggest_layout_type_fallback_on_error():
    content_analysis = {
        "key_points": ["Point 1", "Point 2"],
        "content_type": "general"
    }
    image_assets = []

    # Make bedrock raise an exception
    with patch("tools.layout_tools._get_bedrock") as gb:
        class FakeBedrock:
            def analyze_content(self, prompt, analysis_type):
                raise Exception("bedrock down")

        gb.return_value = FakeBedrock()
        result = await ltools.suggest_layout_type(content_analysis, image_assets)

    assert result == "vertical_list"  # default fallback when bedrock fails


@pytest.mark.asyncio
async def test_generate_layout_spec_normal_operation():
    content_analysis = {
        "key_points": ["Point 1", "Point 2"],
        "content_type": "general"
    }
    image_assets = [{"url": "image1.jpg", "type": "image"}]

    fake_response = {
        "layout_type": "grid",
        "sections": [
            {"type": "title", "x": 0.1, "y": 0.1, "width": 0.8, "height": 0.2},
            {"type": "bullet", "text": "Point 1", "x": 0.1, "y": 0.3, "width": 0.35, "height": 0.1}
        ],
        "dimensions": {"width": 800, "height": 600}
    }

    with patch("tools.layout_tools._get_bedrock") as gb:
        class FakeBedrock:
            def analyze_content(self, prompt, analysis_type):
                return fake_response

        gb.return_value = FakeBedrock()
        result = await ltools.generate_layout_spec(content_analysis, image_assets)

    assert result == fake_response
    assert "layout_type" in result
    assert "sections" in result


@pytest.mark.asyncio
async def test_generate_layout_spec_fallback_on_error():
    content_analysis = {
        "key_points": ["Point 1", "Point 2"],
        "content_type": "general"
    }
    image_assets = [{"url": "image1.jpg", "type": "image"}]

    # Make bedrock raise an exception
    with patch("tools.layout_tools._get_bedrock") as gb:
        class FakeBedrock:
            def analyze_content(self, prompt, analysis_type):
                raise Exception("bedrock down")

        gb.return_value = FakeBedrock()
        result = await ltools.generate_layout_spec(content_analysis, image_assets)

    # Should return local fallback
    assert "layout_type" in result
    assert "sections" in result
    assert "dimensions" in result
    assert result["raw_response"] == "local_fallback"


@pytest.mark.asyncio
async def test_demo_mode_layout_generation():
    """Test that demo mode forces local fallbacks."""
    content_analysis = {
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "content_type": "how-to"
    }
    image_assets = [{"url": "image1.jpg", "type": "image"}]

    # Force demo mode by patching the constant
    with patch("tools.layout_tools._should_use_demo_mode", return_value=True):
        result = await ltools.generate_layout_spec(content_analysis, image_assets)

    assert result["layout_type"] == "vertical_list"  # heuristic for how-to with >3 points
    assert result["raw_response"] == "local_fallback"


def test_get_layout_tools():
    """Test that get_layout_tools returns the expected tools."""
    tools = ltools.get_layout_tools()

    assert len(tools) == 2
    tool_names = [tool.__name__ for tool in tools]
    assert "suggest_layout_type" in tool_names
    assert "generate_layout_spec" in tool_names