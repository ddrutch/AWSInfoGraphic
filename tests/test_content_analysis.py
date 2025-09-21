"""
Unit tests for content analysis functionality.

Tests the ContentTools class and ContentAnalyzerAgent to ensure proper
text analysis, key point extraction, and content structuring.

This test file demonstrates comprehensive testing patterns for the AWS
Infographic Generator system, including mocking strategies, validation
patterns, and performance testing approaches.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.content_tools import ContentTools, ContentAnalysisError
from agents.content_analyzer import ContentAnalyzerAgent, create_content_analyzer_agent
from utils.types import AnalyzedContent, AgentResponse
from utils.test_helpers import MockDataFactory, MockAWSServices, TestDataGenerator, ValidationHelpers
from utils.validation import validate_content_analysis, validate_text_input
from utils.config import create_testing_config
from utils.error_handling import InfographicError, ErrorCategory
from utils.monitoring import get_health_monitor


class TestContentTools(unittest.TestCase):
    """Test cases for ContentTools class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock BedrockTools to avoid AWS calls during testing
        self.mock_bedrock_tools = Mock()
        self.content_tools = ContentTools(bedrock_tools=self.mock_bedrock_tools)
        
        # Sample test data
        self.sample_text = """
        Artificial Intelligence is transforming the modern workplace. 
        AI technologies are being adopted across industries to improve efficiency and productivity.
        Machine learning algorithms can analyze vast amounts of data to identify patterns and insights.
        Companies are investing heavily in AI research and development.
        The future of work will be shaped by human-AI collaboration.
        """
        
        self.short_text = "AI is good."
        self.long_text = "A" * 15000  # Text longer than max limit
    
    def test_preprocess_text_valid_input(self):
        """Test text preprocessing with valid input."""
        result = self.content_tools.preprocess_text(self.sample_text)
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertNotIn('\n', result)  # Should remove newlines
        self.assertNotIn('  ', result)  # Should remove double spaces
    
    def test_preprocess_text_empty_input(self):
        """Test text preprocessing with empty input."""
        with self.assertRaises(ContentAnalysisError):
            self.content_tools.preprocess_text("")
    
    def test_preprocess_text_too_short(self):
        """Test text preprocessing with text too short."""
        with self.assertRaises(ContentAnalysisError):
            self.content_tools.preprocess_text("Hi")
    
    def test_preprocess_text_too_long(self):
        """Test text preprocessing with text too long."""
        result = self.content_tools.preprocess_text(self.long_text)
        self.assertLessEqual(len(result), 10000)  # Should be truncated
    
    def test_extract_key_points_success(self):
        """Test successful key point extraction."""
        # Mock Bedrock response
        mock_response = json.dumps([
            "AI is transforming workplaces",
            "Machine learning analyzes data patterns", 
            "Companies invest in AI research",
            "Future involves human-AI collaboration"
        ])
        self.mock_bedrock_tools.invoke_model.return_value = mock_response
        
        result = self.content_tools.extract_key_points(self.sample_text, max_points=4)
        
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 4)
        self.assertTrue(all(isinstance(point, str) for point in result))
        self.assertTrue(all(len(point) <= 80 for point in result))
    
    def test_extract_key_points_fallback(self):
        """Test key point extraction with fallback method."""
        # Mock Bedrock to return invalid JSON
        self.mock_bedrock_tools.invoke_model.return_value = "Invalid JSON response"
        
        result = self.content_tools.extract_key_points(self.sample_text, max_points=3)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(isinstance(point, str) for point in result))
    
    def test_analyze_content_structure_success(self):
        """Test successful content structure analysis."""
        # Mock Bedrock response
        mock_structure = {
            "title": "AI in the Workplace",
            "sections": [
                {"heading": "AI Adoption", "points": ["Efficiency improvement", "Productivity gains"]},
                {"heading": "Future Trends", "points": ["Human-AI collaboration"]}
            ],
            "flow_direction": "top-to-bottom",
            "complexity_level": "moderate",
            "visual_hierarchy": "title-focused"
        }
        self.mock_bedrock_tools.invoke_model.return_value = json.dumps(mock_structure)
        
        result = self.content_tools.analyze_content_structure(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("title", result)
        self.assertIn("sections", result)
        self.assertIn("flow_direction", result)
        self.assertLessEqual(len(result["title"]), 60)
    
    def test_analyze_content_structure_fallback(self):
        """Test content structure analysis with fallback method."""
        # Mock Bedrock to return invalid JSON
        self.mock_bedrock_tools.invoke_model.return_value = "Invalid JSON"
        
        result = self.content_tools.analyze_content_structure(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("title", result)
        self.assertIn("sections", result)
        self.assertIn("flow_direction", result)
    
    def test_extract_content_metadata_success(self):
        """Test successful content metadata extraction."""
        # Mock Bedrock response
        mock_metadata = {
            "tone": "professional",
            "target_audience": "business",
            "content_type": "informational",
            "suggested_colors": ["blue", "corporate"],
            "estimated_reading_time": 2,
            "key_statistics": ["50%", "2024"],
            "action_items": []
        }
        self.mock_bedrock_tools.invoke_model.return_value = json.dumps(mock_metadata)
        
        result = self.content_tools.extract_content_metadata(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("tone", result)
        self.assertIn("word_count", result)
        self.assertIn("analysis_timestamp", result)
    
    def test_extract_content_metadata_fallback(self):
        """Test content metadata extraction with fallback method."""
        # Mock Bedrock to return invalid JSON
        self.mock_bedrock_tools.invoke_model.return_value = "Invalid JSON"
        
        result = self.content_tools.extract_content_metadata(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("tone", result)
        self.assertIn("word_count", result)
        self.assertGreater(result["word_count"], 0)
    
    def test_create_content_analysis_success(self):
        """Test comprehensive content analysis."""
        # Mock all Bedrock responses
        self.mock_bedrock_tools.invoke_model.side_effect = [
            json.dumps(["Key point 1", "Key point 2", "Key point 3"]),  # key points
            json.dumps({  # structure
                "title": "AI Overview",
                "sections": [{"heading": "Main", "points": ["Point 1"]}],
                "flow_direction": "top-to-bottom",
                "complexity_level": "simple",
                "visual_hierarchy": "title-focused"
            }),
            json.dumps({  # metadata
                "tone": "professional",
                "target_audience": "general",
                "content_type": "informational",
                "suggested_colors": ["blue"],
                "estimated_reading_time": 1,
                "key_statistics": [],
                "action_items": []
            }),
            "Concise summary of AI content",  # summary
            "AI in Modern Workplace"  # title
        ]
        
        result = self.content_tools.create_content_analysis(self.sample_text)
        
        self.assertIsInstance(result, ContentAnalysis)
        self.assertIsInstance(result.main_topic, str)
        self.assertIsInstance(result.key_points, list)
        self.assertIsInstance(result.hierarchy, dict)
        self.assertIsInstance(result.summary, str)
        self.assertIsInstance(result.suggested_title, str)
        self.assertIsInstance(result.content_structure, dict)
    
    def test_create_content_analysis_with_errors(self):
        """Test content analysis with Bedrock errors."""
        # Mock Bedrock to raise exception
        self.mock_bedrock_tools.invoke_model.side_effect = Exception("Bedrock error")
        
        with self.assertRaises(ContentAnalysisError):
            self.content_tools.create_content_analysis(self.sample_text)


class TestContentAnalyzerAgent(unittest.TestCase):
    """Test cases for ContentAnalyzerAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the Strands components to avoid AWS calls
        self.mock_bedrock_model = Mock()
        self.mock_agent = Mock()
        
        # Sample test data
        self.sample_text = """
        Cloud computing has revolutionized how businesses operate.
        Companies can now scale their infrastructure on demand.
        Cost savings and flexibility are major benefits.
        Security and compliance remain important considerations.
        """
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_agent_initialization(self, mock_agent_class, mock_bedrock_model_class):
        """Test agent initialization."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        agent = ContentAnalyzerAgent()
        
        self.assertIsNotNone(agent.agent)
        self.assertIsNotNone(agent.content_tools)
        mock_bedrock_model_class.assert_called_once()
        mock_agent_class.assert_called_once()
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_analyze_content_tool(self, mock_agent_class, mock_bedrock_model_class):
        """Test the analyze_content_tool method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.create_content_analysis method
        mock_analysis = ContentAnalysis(
            main_topic="Cloud Computing",
            key_points=["Scalability", "Cost savings", "Flexibility"],
            hierarchy={"sections": []},
            summary="Cloud computing benefits",
            suggested_title="Cloud Computing Overview",
            content_structure={"metadata": {}}
        )
        
        with patch.object(agent.content_tools, 'create_content_analysis', return_value=mock_analysis):
            result = agent.analyze_content_tool(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("main_topic", result)
        self.assertIn("key_points", result)
        self.assertEqual(result["main_topic"], "Cloud Computing")
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_extract_key_points_tool(self, mock_agent_class, mock_bedrock_model_class):
        """Test the extract_key_points_tool method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.extract_key_points method
        mock_key_points = ["Point 1", "Point 2", "Point 3"]
        
        with patch.object(agent.content_tools, 'extract_key_points', return_value=mock_key_points):
            result = agent.extract_key_points_tool(self.sample_text, max_points=3)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("key_points", result)
        self.assertEqual(len(result["key_points"]), 3)
        self.assertEqual(result["count"], 3)
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_analyze_structure_tool(self, mock_agent_class, mock_bedrock_model_class):
        """Test the analyze_structure_tool method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.analyze_content_structure method
        mock_structure = {
            "title": "Test Title",
            "sections": [],
            "flow_direction": "top-to-bottom"
        }
        
        with patch.object(agent.content_tools, 'analyze_content_structure', return_value=mock_structure):
            result = agent.analyze_structure_tool(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("structure", result)
        self.assertEqual(result["structure"]["title"], "Test Title")
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_extract_metadata_tool(self, mock_agent_class, mock_bedrock_model_class):
        """Test the extract_metadata_tool method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.extract_content_metadata method
        mock_metadata = {
            "tone": "professional",
            "word_count": 50,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        with patch.object(agent.content_tools, 'extract_content_metadata', return_value=mock_metadata):
            result = agent.extract_metadata_tool(self.sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["tone"], "professional")
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_preprocess_text_tool(self, mock_agent_class, mock_bedrock_model_class):
        """Test the preprocess_text_tool method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.preprocess_text method
        preprocessed = "Clean text without extra spaces"
        
        with patch.object(agent.content_tools, 'preprocess_text', return_value=preprocessed):
            result = agent.preprocess_text_tool("  Messy   text  with   spaces  ")
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertIn("preprocessed_text", result)
        self.assertEqual(result["preprocessed_text"], preprocessed)
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_analyze_method(self, mock_agent_class, mock_bedrock_model_class):
        """Test the main analyze method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        # Mock agent response
        self.mock_agent.return_value = "Analysis complete with key insights"
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.create_content_analysis method
        mock_analysis = ContentAnalysis(
            main_topic="Test Topic",
            key_points=["Point 1", "Point 2"],
            hierarchy={"sections": []},
            summary="Test summary",
            suggested_title="Test Title",
            content_structure={"metadata": {}}
        )
        
        with patch.object(agent.content_tools, 'create_content_analysis', return_value=mock_analysis):
            result = agent.analyze(self.sample_text)
        
        self.assertIsInstance(result, AgentResponse)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertIn("agent_response", result.data)
        self.assertIn("structured_analysis", result.data)
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_extract_key_points_method(self, mock_agent_class, mock_bedrock_model_class):
        """Test the extract_key_points method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        # Mock agent response
        self.mock_agent.return_value = "Key points extracted successfully"
        
        agent = ContentAnalyzerAgent()
        
        # Mock the content_tools.extract_key_points method
        mock_key_points = ["Point A", "Point B", "Point C"]
        
        with patch.object(agent.content_tools, 'extract_key_points', return_value=mock_key_points):
            result = agent.extract_key_points(self.sample_text, max_points=3)
        
        self.assertIsInstance(result, AgentResponse)
        self.assertTrue(result.success)
        self.assertIn("key_points", result.data)
        self.assertEqual(len(result.data["key_points"]), 3)
    
    @patch('agents.content_analyzer.BedrockModel')
    @patch('agents.content_analyzer.Agent')
    def test_get_agent_info(self, mock_agent_class, mock_bedrock_model_class):
        """Test the get_agent_info method."""
        mock_bedrock_model_class.return_value = self.mock_bedrock_model
        mock_agent_class.return_value = self.mock_agent
        
        # Mock agent tools
        self.mock_agent.tools = [Mock(), Mock(), Mock()]
        
        agent = ContentAnalyzerAgent()
        
        info = agent.get_agent_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info["agent_type"], "ContentAnalyzer")
        self.assertIn("model_id", info)
        self.assertIn("capabilities", info)
        self.assertIn("tools_count", info)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    @patch('agents.content_analyzer.create_content_analyzer_agent')
    def test_analyze_content_for_infographic(self, mock_create_agent):
        """Test the analyze_content_for_infographic convenience function."""
        # Mock agent and its analyze method
        mock_agent = Mock()
        mock_response = AgentResponse(
            success=True,
            data={"analysis": "complete"},
            metadata={"test": True}
        )
        mock_agent.analyze.return_value = mock_response
        mock_create_agent.return_value = mock_agent
        
        from agents.content_analyzer import analyze_content_for_infographic
        
        result = analyze_content_for_infographic("Test text")
        
        self.assertIsInstance(result, AgentResponse)
        self.assertTrue(result.success)
        mock_create_agent.assert_called_once()
        mock_agent.analyze.assert_called_once_with("Test text")
    
    @patch('agents.content_analyzer.create_content_analyzer_agent')
    def test_extract_infographic_key_points(self, mock_create_agent):
        """Test the extract_infographic_key_points convenience function."""
        # Mock agent and its extract_key_points method
        mock_agent = Mock()
        mock_response = AgentResponse(
            success=True,
            data={"key_points": ["Point 1", "Point 2"]},
            metadata={"count": 2}
        )
        mock_agent.extract_key_points.return_value = mock_response
        mock_create_agent.return_value = mock_agent
        
        from agents.content_analyzer import extract_infographic_key_points
        
        result = extract_infographic_key_points("Test text", max_points=3)
        
        self.assertIsInstance(result, AgentResponse)
        self.assertTrue(result.success)
        mock_create_agent.assert_called_once()
        mock_agent.extract_key_points.assert_called_once_with("Test text", 3)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)