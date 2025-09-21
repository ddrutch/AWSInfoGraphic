#!/usr/bin/env python3
"""
Comprehensive Usage Guide for AWS Infographic Generator

This script demonstrates all major features and usage patterns
for the AWS Infographic Generator system.
"""

import asyncio
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add the parent directory to the path so we can import from the main module
import sys
sys.path.append(str(Path(__file__).parent.parent))

from main import InfographicOrchestrator
from utils.monitoring import setup_logging


def setup_environment():
    """Setup logging and verify environment configuration."""
    setup_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Check required environment variables
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "S3_BUCKET_NAME",
        "BEDROCK_MODEL_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please check your .env file configuration.")
        return False
    
    logger.info("✅ Environment configuration verified")
    return True


async def basic_usage_examples():
    """Demonstrate basic usage patterns."""
    print("\n🎯 Basic Usage Examples")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    # Example 1: Simple text content
    print("\n1. Simple Business Content")
    content = """
    Q3 Business Results:
    
    Revenue: $3.2M (+15% QoQ)
    New Customers: 850 (+22% QoQ)
    Team Size: 45 employees (+8 new hires)
    Customer Satisfaction: 4.7/5 stars
    Product Releases: 2 major features
    """
    
    try:
        result = await orchestrator.generate_infographic(content, "general")
        print(f"✅ Generated: {result.s3_url}")
        print(f"📊 Generation time: {result.generation_time:.2f}s")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Technical content
    print("\n2. Technical Documentation")
    tech_content = """
    System Architecture Overview:
    
    Frontend: React 18 + TypeScript + Vite
    Backend: Python 3.12 + FastAPI + PostgreSQL
    Infrastructure: AWS (ECS + RDS + S3 + CloudFront)
    Monitoring: DataDog + CloudWatch + Sentry
    CI/CD: GitHub Actions + Docker + Terraform
    """
    
    try:
        result = await orchestrator.generate_infographic(tech_content, "discord")
        print(f"✅ Generated: {result.s3_url}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def platform_optimization_examples():
    """Demonstrate platform-specific optimizations."""
    print("\n📱 Platform Optimization Examples")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    content = """
    Marketing Campaign Results:
    
    Email Campaign: 25% open rate, 5% click rate
    Social Media: 50K impressions, 2K engagements
    Paid Ads: $2.50 CPC, 3.2% conversion rate
    Organic Traffic: 15K visitors, 8 min avg session
    Lead Generation: 120 qualified leads
    """
    
    platforms = [
        ("whatsapp", "Square format for mobile sharing"),
        ("twitter", "Landscape format for social media"),
        ("discord", "High resolution for community sharing"),
        ("general", "Universal format for presentations")
    ]
    
    for platform, description in platforms:
        print(f"\n🎯 {platform.title()}: {description}")
        
        try:
            result = await orchestrator.generate_infographic(content, platform)
            print(f"✅ Generated: {result.s3_url}")
            print(f"📐 Dimensions: {result.dimensions}")
            print(f"📁 File size: {result.file_size} bytes")
        except Exception as e:
            print(f"❌ Error for {platform}: {e}")


async def advanced_configuration_examples():
    """Demonstrate advanced configuration options."""
    print("\n⚙️ Advanced Configuration Examples")
    print("=" * 50)
    
    # Custom configuration
    custom_config = {
        "max_image_size": 1024,
        "image_quality": 90,
        "color_scheme": "tech",
        "font_family": "Arial",
        "enable_caching": True,
        "timeout_seconds": 180,
        "max_retries": 5
    }
    
    orchestrator = InfographicOrchestrator(config=custom_config)
    
    content = """
    Security Incident Response:
    
    Detection: Automated monitoring alerts
    Assessment: Security team evaluation (15 min)
    Containment: Isolate affected systems (30 min)
    Investigation: Root cause analysis (2 hours)
    Recovery: System restoration (1 hour)
    Lessons Learned: Post-incident review
    """
    
    try:
        result = await orchestrator.generate_infographic(content, "twitter")
        print(f"✅ Custom configured infographic: {result.s3_url}")
        print(f"🎨 Applied configuration: {json.dumps(custom_config, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def batch_processing_examples():
    """Demonstrate batch processing capabilities."""
    print("\n📦 Batch Processing Examples")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    # Multiple content items for batch processing
    content_batch = [
        {
            "title": "Sales Performance",
            "content": "Q4 Sales: $4.2M revenue (+18% YoY), 1,500 new customers (+25% YoY), 96% customer retention",
            "platform": "whatsapp"
        },
        {
            "title": "Product Roadmap",
            "content": "2024 Roadmap: Q1 Mobile app, Q2 API v3.0, Q3 AI features, Q4 Enterprise tools",
            "platform": "twitter"
        },
        {
            "title": "Team Updates",
            "content": "Team Growth: 12 new engineers, 3 designers, 2 product managers. Remote-first culture.",
            "platform": "discord"
        },
        {
            "title": "Infrastructure Stats",
            "content": "Infrastructure: 99.9% uptime, 50ms avg response time, 10TB data processed, 5M API calls",
            "platform": "general"
        }
    ]
    
    # Process with concurrency control
    semaphore = asyncio.Semaphore(2)  # Limit concurrent generations
    
    async def process_item(item):
        async with semaphore:
            print(f"🎯 Processing: {item['title']}")
            try:
                result = await orchestrator.generate_infographic(
                    item['content'], 
                    item['platform']
                )
                return {
                    "title": item['title'],
                    "success": True,
                    "url": result.s3_url,
                    "platform": item['platform'],
                    "generation_time": result.generation_time
                }
            except Exception as e:
                return {
                    "title": item['title'],
                    "success": False,
                    "error": str(e),
                    "platform": item['platform']
                }
    
    # Execute batch processing
    print("🚀 Starting batch processing...")
    results = await asyncio.gather(*[process_item(item) for item in content_batch])
    
    # Summary
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n📊 Batch Processing Results:")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        avg_time = sum(r["generation_time"] for r in successful) / len(successful)
        print(f"⏱️ Average generation time: {avg_time:.2f}s")
    
    for result in successful:
        print(f"  • {result['title']} ({result['platform']}): {result['url']}")
    
    for result in failed:
        print(f"  • {result['title']} ({result['platform']}): Error - {result['error']}")


async def error_handling_examples():
    """Demonstrate error handling and recovery."""
    print("\n🛡️ Error Handling Examples")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    # Test various error scenarios
    error_test_cases = [
        {
            "name": "Empty Content",
            "content": "",
            "platform": "general",
            "expected": "Content validation error"
        },
        {
            "name": "Extremely Long Content",
            "content": "Very long content. " * 500,  # Very long text
            "platform": "whatsapp",
            "expected": "Content length limit exceeded"
        },
        {
            "name": "Invalid Platform",
            "content": "Test content for invalid platform",
            "platform": "invalid_platform",
            "expected": "Invalid platform error"
        },
        {
            "name": "Special Characters",
            "content": "Content with émojis 🚀🎯📊 and spëcial çharacters ñáéíóú",
            "platform": "twitter",
            "expected": "Should handle gracefully"
        }
    ]
    
    for test_case in error_test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"Expected: {test_case['expected']}")
        
        try:
            result = await orchestrator.generate_infographic(
                test_case['content'], 
                test_case['platform']
            )
            print(f"✅ Handled gracefully: {result.s3_url}")
        except Exception as e:
            print(f"❌ Error (as expected): {type(e).__name__}: {e}")


async def monitoring_examples():
    """Demonstrate monitoring and analytics."""
    print("\n📊 Monitoring and Analytics Examples")
    print("=" * 50)
    
    # Custom orchestrator with analytics
    class AnalyticsOrchestrator(InfographicOrchestrator):
        def __init__(self, config=None):
            super().__init__(config)
            self.analytics = {
                "total_generations": 0,
                "successful_generations": 0,
                "failed_generations": 0,
                "total_time": 0.0,
                "platform_usage": {},
                "error_types": {}
            }
        
        async def generate_with_analytics(self, content: str, platform: str = "general"):
            start_time = asyncio.get_event_loop().time()
            self.analytics["total_generations"] += 1
            
            try:
                result = await self.generate_infographic(content, platform)
                
                # Record success metrics
                self.analytics["successful_generations"] += 1
                generation_time = asyncio.get_event_loop().time() - start_time
                self.analytics["total_time"] += generation_time
                
                # Platform usage tracking
                if platform not in self.analytics["platform_usage"]:
                    self.analytics["platform_usage"][platform] = 0
                self.analytics["platform_usage"][platform] += 1
                
                return result
                
            except Exception as e:
                # Record error metrics
                self.analytics["failed_generations"] += 1
                error_type = type(e).__name__
                
                if error_type not in self.analytics["error_types"]:
                    self.analytics["error_types"][error_type] = 0
                self.analytics["error_types"][error_type] += 1
                
                raise
        
        def get_analytics_summary(self):
            total = self.analytics["total_generations"]
            if total == 0:
                return {"message": "No generations recorded"}
            
            success_rate = (self.analytics["successful_generations"] / total) * 100
            avg_time = (self.analytics["total_time"] / 
                       max(self.analytics["successful_generations"], 1))
            
            return {
                "total_generations": total,
                "success_rate": f"{success_rate:.1f}%",
                "average_generation_time": f"{avg_time:.2f}s",
                "platform_usage": self.analytics["platform_usage"],
                "error_types": self.analytics["error_types"]
            }
    
    # Test with analytics
    analytics_orchestrator = AnalyticsOrchestrator()
    
    test_contents = [
        ("DevOps Metrics: 99.9% uptime, 2min deployment time, 0.1% error rate", "twitter"),
        ("Product Launch: New AI features, 10K beta users, 4.8/5 rating", "whatsapp"),
        ("Team Update: 5 new hires, office expansion, remote work policy", "discord"),
        ("", "general"),  # This should fail
        ("Security Update: Patches deployed, systems secure, monitoring active", "general")
    ]
    
    for content, platform in test_contents:
        try:
            result = await analytics_orchestrator.generate_with_analytics(content, platform)
            print(f"✅ Generated for {platform}: {result.s3_url}")
        except Exception as e:
            print(f"❌ Failed for {platform}: {e}")
    
    # Show analytics summary
    summary = analytics_orchestrator.get_analytics_summary()
    print(f"\n📈 Analytics Summary:")
    print(json.dumps(summary, indent=2))


async def integration_examples():
    """Demonstrate integration patterns."""
    print("\n🔗 Integration Examples")
    print("=" * 50)
    
    # Example: Webhook-style integration
    async def webhook_handler(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate webhook handler for infographic generation."""
        orchestrator = InfographicOrchestrator()
        
        try:
            result = await orchestrator.generate_infographic(
                request_data["content"],
                request_data.get("platform", "general")
            )
            
            return {
                "status": "success",
                "infographic_url": result.s3_url,
                "metadata": {
                    "platform": request_data.get("platform", "general"),
                    "generation_time": result.generation_time,
                    "file_size": result.file_size
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "error_type": type(e).__name__
            }
    
    # Test webhook integration
    webhook_requests = [
        {
            "content": "API Performance: 99.5% uptime, 120ms avg response, 1M requests/day",
            "platform": "twitter"
        },
        {
            "content": "Customer Feedback: 4.9/5 satisfaction, 95% would recommend, 200+ reviews",
            "platform": "whatsapp"
        }
    ]
    
    for request in webhook_requests:
        print(f"\n🎯 Processing webhook request for {request['platform']}")
        response = await webhook_handler(request)
        
        if response["status"] == "success":
            print(f"✅ Success: {response['infographic_url']}")
            print(f"📊 Metadata: {json.dumps(response['metadata'], indent=2)}")
        else:
            print(f"❌ Error: {response['error_message']}")


async def main():
    """Run comprehensive usage guide."""
    print("🚀 AWS Infographic Generator - Comprehensive Usage Guide")
    print("=" * 70)
    
    # Setup environment
    if not setup_environment():
        return
    
    try:
        # Run all example categories
        await basic_usage_examples()
        await platform_optimization_examples()
        await advanced_configuration_examples()
        await batch_processing_examples()
        await error_handling_examples()
        await monitoring_examples()
        await integration_examples()
        
        print("\n🎉 Usage guide completed successfully!")
        print("Check your S3 bucket for all generated infographics.")
        
    except Exception as e:
        logging.error(f"Usage guide execution failed: {e}")
        print(f"❌ Error running usage guide: {e}")


if __name__ == "__main__":
    asyncio.run(main())