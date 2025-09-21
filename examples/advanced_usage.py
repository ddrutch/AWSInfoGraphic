#!/usr/bin/env python3
"""
Advanced usage examples for the AWS Infographic Generator.

This script demonstrates advanced features like custom agents,
error handling, monitoring, and integration patterns.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add the parent directory to the path so we can import from the main module
import sys
sys.path.append(str(Path(__file__).parent.parent))

from main import InfographicOrchestrator
from agents.content_analyzer import ContentAnalyzer
from agents.image_sourcer import ImageSourcer
from agents.design_layout import DesignLayout
from tools.s3_tools import S3Tools
from utils.monitoring import setup_logging, log_performance


# Setup logging
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomInfographicOrchestrator(InfographicOrchestrator):
    """Extended orchestrator with custom functionality."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.generation_history: List[Dict] = []
    
    async def generate_with_analytics(self, user_input: str, platform: str = "general") -> Dict:
        """Generate infographic with detailed analytics."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Generate infographic
            result = await self.generate_infographic(user_input, platform)
            
            # Calculate metrics
            end_time = asyncio.get_event_loop().time()
            generation_time = end_time - start_time
            
            # Store analytics
            analytics = {
                "generation_time": generation_time,
                "platform": platform,
                "content_length": len(user_input),
                "success": True,
                "timestamp": end_time
            }
            
            self.generation_history.append(analytics)
            
            logger.info(f"Generated infographic in {generation_time:.2f}s for platform: {platform}")
            
            return {
                "result": result,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            
            analytics = {
                "generation_time": asyncio.get_event_loop().time() - start_time,
                "platform": platform,
                "content_length": len(user_input),
                "success": False,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
            
            self.generation_history.append(analytics)
            raise
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        if not self.generation_history:
            return {"message": "No generation history available"}
        
        successful_generations = [h for h in self.generation_history if h["success"]]
        failed_generations = [h for h in self.generation_history if not h["success"]]
        
        if successful_generations:
            avg_time = sum(h["generation_time"] for h in successful_generations) / len(successful_generations)
            min_time = min(h["generation_time"] for h in successful_generations)
            max_time = max(h["generation_time"] for h in successful_generations)
        else:
            avg_time = min_time = max_time = 0
        
        return {
            "total_generations": len(self.generation_history),
            "successful_generations": len(successful_generations),
            "failed_generations": len(failed_generations),
            "success_rate": len(successful_generations) / len(self.generation_history) * 100,
            "average_generation_time": avg_time,
            "min_generation_time": min_time,
            "max_generation_time": max_time
        }


async def agent_interaction_example():
    """Example of direct agent interaction."""
    print("🤖 Direct Agent Interaction Example")
    print("=" * 50)
    
    content = """
    Cloud Migration Strategy:
    
    Phase 1: Assessment and Planning (2 months)
    - Current infrastructure audit
    - Cost-benefit analysis
    - Migration roadmap development
    
    Phase 2: Pilot Migration (1 month)
    - Non-critical workloads first
    - Performance testing
    - Security validation
    
    Phase 3: Full Migration (3 months)
    - Critical systems migration
    - Data synchronization
    - Cutover execution
    
    Phase 4: Optimization (Ongoing)
    - Performance tuning
    - Cost optimization
    - Monitoring and alerting
    """
    
    # Direct content analysis
    print("📝 Analyzing content...")
    content_analyzer = ContentAnalyzer()
    analysis_result = await content_analyzer.analyze_content(content)
    print(f"✅ Content analysis: {analysis_result.main_topic}")
    print(f"📊 Key points: {len(analysis_result.key_points)}")
    
    # Direct image sourcing
    print("\n🖼️ Sourcing images...")
    image_sourcer = ImageSourcer()
    image_result = await image_sourcer.source_images(analysis_result.main_topic, count=2)
    print(f"✅ Found {len(image_result)} images")
    
    # Direct layout design
    print("\n🎨 Designing layout...")
    design_layout = DesignLayout()
    layout_result = await design_layout.create_layout(
        content_analysis=analysis_result,
        images=image_result,
        platform="twitter"
    )
    print(f"✅ Layout created: {layout_result.canvas_size}")


async def error_handling_example():
    """Example of comprehensive error handling."""
    print("\n🛡️ Error Handling Example")
    print("=" * 50)
    
    orchestrator = CustomInfographicOrchestrator()
    
    # Test with various problematic inputs
    test_cases = [
        {
            "name": "Empty content",
            "content": "",
            "platform": "general"
        },
        {
            "name": "Very long content",
            "content": "Lorem ipsum " * 1000,  # Very long text
            "platform": "whatsapp"
        },
        {
            "name": "Invalid platform",
            "content": "Test content",
            "platform": "invalid_platform"
        },
        {
            "name": "Special characters",
            "content": "Test with émojis 🚀 and spëcial çharacters",
            "platform": "twitter"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        try:
            result = await orchestrator.generate_with_analytics(
                user_input=test_case['content'],
                platform=test_case['platform']
            )
            print(f"✅ Success: {result['result'].s3_url}")
            
        except Exception as e:
            print(f"❌ Expected error handled: {type(e).__name__}: {e}")
    
    # Show performance stats
    stats = orchestrator.get_performance_stats()
    print(f"\n📊 Performance Stats:")
    print(json.dumps(stats, indent=2))


async def monitoring_example():
    """Example of monitoring and logging."""
    print("\n📊 Monitoring and Logging Example")
    print("=" * 50)
    
    @log_performance
    async def monitored_generation(content: str, platform: str):
        """Generate infographic with performance monitoring."""
        orchestrator = InfographicOrchestrator()
        return await orchestrator.generate_infographic(content, platform)
    
    content = """
    DevOps Best Practices:
    
    1. Infrastructure as Code (IaC)
    2. Continuous Integration/Continuous Deployment (CI/CD)
    3. Automated Testing and Quality Gates
    4. Monitoring and Observability
    5. Security Integration (DevSecOps)
    6. Configuration Management
    """
    
    try:
        result = await monitored_generation(content, "discord")
        logger.info(f"Monitored generation completed: {result.s3_url}")
        
    except Exception as e:
        logger.error(f"Monitored generation failed: {e}")


async def s3_integration_example():
    """Example of advanced S3 integration."""
    print("\n📦 Advanced S3 Integration Example")
    print("=" * 50)
    
    s3_tools = S3Tools()
    
    # List existing infographics
    print("📋 Listing existing infographics...")
    try:
        objects = await s3_tools.list_objects(prefix="infographics/")
        print(f"✅ Found {len(objects)} existing infographics")
        
        for obj in objects[:5]:  # Show first 5
            print(f"  • {obj['Key']} ({obj['Size']} bytes)")
            
    except Exception as e:
        print(f"❌ Error listing objects: {e}")
    
    # Generate and upload with custom metadata
    print("\n🎯 Generating with custom metadata...")
    orchestrator = InfographicOrchestrator()
    
    content = """
    API Performance Metrics:
    
    Average Response Time: 120ms
    Throughput: 1,000 requests/second
    Error Rate: 0.1%
    Uptime: 99.9%
    Cache Hit Rate: 85%
    """
    
    try:
        result = await orchestrator.generate_infographic(content, "general")
        
        # Add custom metadata
        metadata = {
            "content_type": "performance_metrics",
            "generated_by": "aws_infographic_generator",
            "platform": "general",
            "version": "1.0"
        }
        
        # Upload with metadata (this would be done in the actual implementation)
        print(f"✅ Generated with metadata: {result.s3_url}")
        print(f"📊 Metadata: {metadata}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def batch_processing_example():
    """Example of efficient batch processing."""
    print("\n⚡ Batch Processing Example")
    print("=" * 50)
    
    orchestrator = CustomInfographicOrchestrator()
    
    # Simulate multiple content items
    content_items = [
        ("Sales Report", "Q4 Sales: $5M revenue, 200 new customers, 95% satisfaction"),
        ("Team Update", "New hires: 5 engineers, 2 designers. Office expansion planned."),
        ("Product Launch", "New feature: AI-powered analytics. Beta testing starts next week."),
        ("Security Alert", "Security update deployed. All systems secure. No action required."),
        ("Training Schedule", "Next training: AWS Certification prep, March 15-17, 2024")
    ]
    
    # Process in parallel with concurrency limit
    semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent generations
    
    async def process_item(title: str, content: str):
        async with semaphore:
            print(f"🎯 Processing: {title}")
            try:
                result = await orchestrator.generate_with_analytics(content, "whatsapp")
                return {"title": title, "success": True, "url": result['result'].s3_url}
            except Exception as e:
                return {"title": title, "success": False, "error": str(e)}
    
    # Execute batch processing
    tasks = [process_item(title, content) for title, content in content_items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Summary
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    failed = [r for r in results if isinstance(r, dict) and not r.get("success")]
    
    print(f"\n📊 Batch Processing Results:")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    for result in successful:
        print(f"  • {result['title']}: {result['url']}")
    
    for result in failed:
        print(f"  • {result['title']}: Error - {result.get('error', 'Unknown error')}")
    
    # Show overall performance stats
    stats = orchestrator.get_performance_stats()
    print(f"\n📈 Overall Performance:")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    print(f"Average Time: {stats['average_generation_time']:.2f}s")


async def main():
    """Run all advanced examples."""
    print("🚀 AWS Infographic Generator - Advanced Examples")
    print("=" * 60)
    
    try:
        await agent_interaction_example()
        await error_handling_example()
        await monitoring_example()
        await s3_integration_example()
        await batch_processing_example()
        
        print("\n🎉 All advanced examples completed!")
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())