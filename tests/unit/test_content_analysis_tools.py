import asyncio
from unittest.mock import patch

import pytest

from tools import content_analysis_tools as catools


import asyncio
from unittest.mock import patch

import pytest

from tools import content_analysis_tools as catools


@pytest.mark.asyncio
async def test_analyze_content_structure_normalizes_dict():
    sample_text = "Title\nThis is a paragraph.\nMore details here."

    fake_response = {
        "main_topic": "Sample Title",
        "key_points": ["Point A", "Point B"],
        "hierarchy": {"sections": []},
        "summary": "Short summary",
        "suggested_title": "Sample Title",
        "content_type": "how-to",
        "sentiment": "positive",
        "complexity_score": 0.2,
        "estimated_reading_time": 30,
    }

    with patch("tools.content_analysis_tools._get_bedrock") as gb:
        class FakeBedrock:
            def analyze_content(self, text, analysis_type):
                return fake_response

        gb.return_value = FakeBedrock()
        res = await catools.analyze_content_structure(sample_text)

    assert res["main_topic"] == "Sample Title"
    assert isinstance(res["key_points"], list) and res["key_points"][0] == "Point A"
    assert res["content_type"] == "how-to"


@pytest.mark.asyncio
async def test_extract_key_messages_fallback_on_error():
    sample_text = "Short text"

    # Make bedrock raise an invocation error
    with patch("tools.content_analysis_tools._get_bedrock") as gb:
        class FakeBedrock:
            def analyze_content(self, text, analysis_type):
                raise Exception("bedrock down")

        gb.return_value = FakeBedrock()
        points = await catools.extract_key_messages(sample_text, max_points=3)

    assert points == []
