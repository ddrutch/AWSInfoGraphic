"""Unit tests for the ImageComposer agent."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agents.image_composer import create_image_composer_agent, ImageComposer
from utils.constants import DEMO_MODE


class TestImageComposer:
    """Test cases for ImageComposer agent."""

    @pytest.fixture
    def sample_layout_spec(self):
        """Sample layout specification for testing."""
        return {
            "canvas_size": [1200, 800],
            "color_scheme": {
                "background": "#FFFFFF",
                "primary": "#1a365d",
                "secondary": "#64748b"
            },
            "layout_type": "vertical_flow",
            "sections": [
                {"type": "header", "position": [0.1, 0.1], "size": [0.8, 0.15]},
                {"type": "content", "position": [0.1, 0.3], "size": [0.8, 0.5]},
                {"type": "footer", "position": [0.1, 0.85], "size": [0.8, 0.1]}
            ]
        }

    @pytest.fixture
    def sample_text_specs(self):
        """Sample text specifications for testing."""
        return [
            {
                "text": "How to Accelerate Cloud Migrations",
                "position": [0.1, 0.1],
                "font_size": 24,
                "font_family": "Arial",
                "color": "#1a365d",
                "alignment": "left",
                "bold": True
            },
            {
                "text": "Assess your current workloads and dependencies",
                "position": [0.1, 0.25],
                "font_size": 18,
                "font_family": "Arial",
                "color": "#333333",
                "alignment": "left"
            }
        ]

    @pytest.fixture
    def sample_image_specs(self):
        """Sample image specifications for testing."""
        return [
            {
                "url": "https://example.com/image1.png",
                "position": [0.1, 0.5],
                "size": [0.3, 0.3],
                "type": "illustration"
            }
        ]

    @pytest.mark.asyncio
    async def test_image_composer_creation(self):
        """Test that ImageComposer agent can be created."""
        agent = create_image_composer_agent()
        assert isinstance(agent, ImageComposer)
        assert hasattr(agent, 'process')

    @pytest.mark.asyncio
    async def test_process_demo_mode(self, sample_layout_spec, sample_text_specs, sample_image_specs):
        """Test processing in demo mode."""
        with patch('tools.image_composition_tools.DEMO_MODE', True):
            agent = create_image_composer_agent()

            result = await agent.process(
                layout_spec=sample_layout_spec,
                text_specs=sample_text_specs,
                image_specs=sample_image_specs,
                platform="general"
            )

            assert result["success"] is True
            assert "image_url" in result["composition"]
            assert "composition_id" in result["composition"]
            assert result["composition"]["platform"] == "general"
            assert "demo" in result["composition"]["image_url"]

    @pytest.mark.asyncio
    async def test_process_with_missing_strands(self, sample_layout_spec, sample_text_specs):
        """Test processing when strands SDK is not available (uses shim)."""
        # Mock the import failure
        with patch.dict('sys.modules', {'strands': None, 'strands.models': None}):
            agent = create_image_composer_agent()

            result = await agent.process(
                layout_spec=sample_layout_spec,
                text_specs=sample_text_specs,
                platform="social"
            )

            assert result["success"] is True
            assert "composition" in result
            assert result["platform"] == "social"

    @pytest.mark.asyncio
    async def test_process_empty_specs(self):
        """Test processing with minimal specifications."""
        agent = create_image_composer_agent()

        result = await agent.process(
            layout_spec={"canvas_size": [800, 600]},
            text_specs=[],
            image_specs=None,
            platform="presentation"
        )

        assert result["success"] is True
        assert result["platform"] == "presentation"

    @pytest.mark.asyncio
    async def test_process_error_handling(self):
        """Test error handling during processing."""
        agent = create_image_composer_agent()

        # Test with invalid layout spec that might cause issues
        result = await agent.process(
            layout_spec={},  # Empty spec
            text_specs=[{"invalid": "spec"}],
            platform="general"
        )

        # Should still succeed in demo mode or with fallbacks
        assert isinstance(result, dict)
        assert "success" in result

    def test_agent_initialization(self):
        """Test agent initialization parameters."""
        agent = ImageComposer(model_id="test-model", region="us-west-2")
        assert agent.model_id == "test-model"
        assert agent.region == "us-west-2"

    @pytest.mark.asyncio
    async def test_composition_result_structure(self, sample_layout_spec, sample_text_specs):
        """Test that composition results have expected structure."""
        agent = create_image_composer_agent()

        result = await agent.process(
            layout_spec=sample_layout_spec,
            text_specs=sample_text_specs,
            platform="web"
        )

        assert result["success"] is True
        assert "composition" in result
        assert "platform" in result

        composition = result["composition"]
        assert "image_url" in composition
        assert "platform" in composition