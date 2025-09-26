import asyncio
import os
import importlib

import asyncio
import os
import importlib

import pytest

cat = importlib.import_module('tools.content_analysis_tools')


@pytest.mark.asyncio
async def test_summarize_for_title():
    res = await cat.summarize_for_title("This is a long sentence that should be shortened to a title.")
    assert isinstance(res, str) and len(res) > 0


@pytest.mark.asyncio
async def test_estimate_visual_elements():
    res = await cat.estimate_visual_elements("Sales increased by 20% in Q1. Growth continues.")
    assert isinstance(res, dict)
    assert 'icons' in res and 'bullets' in res


@pytest.mark.asyncio
async def test_demo_mode_for_structure(monkeypatch):
    # Force DEMO_MODE by monkeypatching the internal flag
    monkeypatch.setattr(cat, '_should_use_demo_mode', lambda: True)
    res = await cat.analyze_content_structure("Short text for demo mode.")
    assert res.get('raw_response') == 'local_fallback'
