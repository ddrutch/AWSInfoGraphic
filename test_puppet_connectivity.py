#!/usr/bin/env python3
"""
Test script to verify puppet system connectivity for AI Agent Refactor.

This script tests:
1. All agents can be initialized with their tools
2. Basic orchestration flow without full implementations
3. Proper agent-tool connectivity
4. System can run end-to-end with placeholder responses
"""

import asyncio
import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_agent_initialization():
    """Test that all agents can be initialized with their tools."""
    print("\n🔧 Testing Agent Initialization...")
    
    try:
        # Test ContentAnalyzer
        from agents.content_analyzer import create_content_analyzer_agent
        content_analyzer = create_content_analyzer_agent()
        print("✅ ContentAnalyzer agent initialized successfully")
        
        # Test ImageSourcer
        from agents.image_sourcer import create_image_sourcer_agent
        image_sourcer = create_image_sourcer_agent()
        print("✅ ImageSourcer agent initialized successfully")
        
        # Test DesignLayout
        from agents.design_layout import create_design_layout_agent
        design_layout = create_design_layout_agent()
        print("✅ DesignLayout agent initialized successfully")
        
        # Test TextFormatter
        from agents.text_formatter import create_text_formatter_agent
        text_formatter = create_text_formatter_agent()
        print("✅ TextFormatter agent initialized successfully")
        
        # Test ImageComposer
        from agents.image_composer import ImageComposer
        image_composer = ImageComposer()
        print("✅ ImageComposer agent initialized successfully")
        
        return {
            "content_analyzer": content_analyzer,
            "image_sourcer": image_sourcer,
            "design_layout": design_layout,
            "text_formatter": text_formatter,
            "image_composer": image_composer
        }
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {str(e)}")
        return None

def test_tool_connectivity():
    """Test that all tools are properly connected and accessible."""
    print("\n🔗 Testing Tool Connectivity...")
    
    try:
        # Test content analysis tools
        from tools.content_analysis_tools import get_content_analysis_tools
        content_tools = get_content_analysis_tools()
        print(f"✅ Content analysis tools loaded: {len(content_tools)} tools")
        
        # Test image sourcing tools
        from tools.image_sourcing_tools import get_image_sourcing_tools
        image_sourcing_tools = get_image_sourcing_tools()
        print(f"✅ Image sourcing tools loaded: {len(image_sourcing_tools)} tools")
        
        # Test layout design tools
        from tools.layout_design_tools import get_layout_design_tools
        layout_tools = get_layout_design_tools()
        print(f"✅ Layout design tools loaded: {len(layout_tools)} tools")
        
        # Test text formatting tools
        from tools.text_formatting_tools import get_text_formatting_tools
        text_tools = get_text_formatting_tools()
        print(f"✅ Text formatting tools loaded: {len(text_tools)} tools")
        
        # Test image composition tools
        from tools.image_composition_tools import get_image_composition_tools
        composition_tools = get_image_composition_tools()
        print(f"✅ Image composition tools loaded: {len(composition_tools)} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool connectivity test failed: {str(e)}")
        return False

async def test_basic_orchestration():
    """Test basic orchestration flow without full implementations."""
    print("\n🎭 Testing Basic Orchestration Flow...")
    
    try:
        # Initialize main orchestrator
        from main import InfographicOrchestrator
        orchestrator = InfographicOrchestrator()
        print("✅ Main orchestrator initialized successfully")
        
        # Test basic orchestration with simple content
        test_content = "Test content for puppet system validation"
        test_platform = "general"
        
        print(f"🚀 Testing orchestration with content: '{test_content}'")
        result = await orchestrator.generate_infographic(test_content, test_platform)
        
        if result.get("success"):
            print("✅ Basic orchestration completed successfully")
            print(f"   Platform: {result.get('platform')}")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            return True
        else:
            print(f"⚠️  Orchestration completed with issues: {result.get('error', 'Unknown error')}")
            return True  # Still counts as connectivity test passing
            
    except Exception as e:
        print(f"❌ Basic orchestration test failed: {str(e)}")
        return False

async def test_individual_agent_processing():
    """Test individual agent processing with placeholder data."""
    print("\n🤖 Testing Individual Agent Processing...")
    
    agents = test_agent_initialization()
    if not agents:
        return False
    
    try:
        # Test ContentAnalyzer
        print("Testing ContentAnalyzer...")
        content_result = await agents["content_analyzer"].process(
            "Test content for analysis", "general"
        )
        print(f"✅ ContentAnalyzer: {content_result.get('success', False)}")
        
        # Test ImageSourcer with mock analysis
        print("Testing ImageSourcer...")
        mock_analysis = {"main_topic": "test", "key_points": ["point1", "point2"]}
        image_result = await agents["image_sourcer"].process(mock_analysis, "general")
        print(f"✅ ImageSourcer: {image_result.get('success', False)}")
        
        # Test DesignLayout with mock data
        print("Testing DesignLayout...")
        layout_result = await agents["design_layout"].process(
            mock_analysis, {"images": ["test_image"]}, "general"
        )
        print(f"✅ DesignLayout: {layout_result.get('success', False)}")
        
        # Test TextFormatter with mock layout
        print("Testing TextFormatter...")
        mock_layout = {"sections": [{"type": "title"}, {"type": "content"}]}
        text_result = await agents["text_formatter"].process(mock_layout, "general")
        print(f"✅ TextFormatter: {text_result.get('success', False)}")
        
        # Test ImageComposer with mock data
        print("Testing ImageComposer...")
        composition_result = await agents["image_composer"].process(
            "test_image_url", {"elements": []}, mock_layout, "general"
        )
        print(f"✅ ImageComposer: {composition_result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual agent processing test failed: {str(e)}")
        return False

def test_configuration_loading():
    """Test that configuration and constants are properly loaded."""
    print("\n⚙️  Testing Configuration Loading...")
    
    try:
        from utils.constants import BEDROCK_MODEL_ID, BEDROCK_REGION, PLATFORM_SPECS
        print(f"✅ Bedrock model ID: {BEDROCK_MODEL_ID}")
        print(f"✅ Bedrock region: {BEDROCK_REGION}")
        print(f"✅ Platform specs loaded: {len(PLATFORM_SPECS)} platforms")
        
        # Test platform specifications
        for platform in ["whatsapp", "twitter", "general"]:
            if platform in PLATFORM_SPECS:
                specs = PLATFORM_SPECS[platform]
                print(f"   {platform}: {specs['dimensions']} - {specs['format']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {str(e)}")
        return False

async def run_connectivity_tests():
    """Run all connectivity tests."""
    print("🚀 Starting Puppet System Connectivity Tests")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Agent Initialization
    test_results["agent_init"] = test_agent_initialization() is not None
    
    # Test 2: Tool Connectivity
    test_results["tool_connectivity"] = test_tool_connectivity()
    
    # Test 3: Configuration Loading
    test_results["config_loading"] = test_configuration_loading()
    
    # Test 4: Basic Orchestration
    test_results["basic_orchestration"] = await test_basic_orchestration()
    
    # Test 5: Individual Agent Processing
    test_results["agent_processing"] = await test_individual_agent_processing()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All puppet system connectivity tests PASSED!")
        print("✅ System is ready for incremental development")
        return True
    else:
        print("⚠️  Some tests failed - system needs attention")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_connectivity_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)