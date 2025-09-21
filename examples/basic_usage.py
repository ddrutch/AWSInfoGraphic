#!/usr/bin/env python3
"""
Basic usage examples for the AWS Infographic Generator.

This script demonstrates how to use the infographic generator programmatically
with different platforms and content types.
"""

import asyncio
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the main module
import sys
sys.path.append(str(Path(__file__).parent.parent))

from main import InfographicOrchestrator


async def basic_example():
    """Basic infographic generation example."""
    print("🎯 Basic Infographic Generation Example")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    content = """
    AI Trends in 2024:
    
    1. Large Language Models continue to evolve with better reasoning capabilities
    2. Multimodal AI systems combining text, image, and audio processing
    3. AI agents becoming more autonomous and capable of complex tasks
    4. Edge AI deployment for real-time applications
    5. Ethical AI and responsible development practices gaining importance
    """
    
    try:
        result = await orchestrator.generate_infographic(
            user_input=content,
            platform="general",
            output_format="PNG"
        )
        
        print(f"✅ Generated infographic: {result.s3_url}")
        print(f"📁 Local path: {result.image_path}")
        print(f"📊 Metadata: {result.metadata}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def platform_specific_examples():
    """Generate infographics for different social media platforms."""
    print("\n📱 Platform-Specific Examples")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    content = """
    Company Q4 Results:
    
    Revenue: $2.5M (+25% YoY)
    New Customers: 1,200 (+40% YoY)
    Team Growth: 15 new hires
    Product Launches: 3 major features
    Customer Satisfaction: 4.8/5 stars
    """
    
    platforms = ["whatsapp", "twitter", "discord"]
    
    for platform in platforms:
        print(f"\n🎯 Generating for {platform.title()}...")
        
        try:
            result = await orchestrator.generate_infographic(
                user_input=content,
                platform=platform,
                output_format="PNG"
            )
            
            print(f"✅ {platform.title()} infographic: {result.s3_url}")
            
        except Exception as e:
            print(f"❌ Error for {platform}: {e}")


async def batch_generation_example():
    """Generate multiple infographics in batch."""
    print("\n📦 Batch Generation Example")
    print("=" * 50)
    
    orchestrator = InfographicOrchestrator()
    
    contents = [
        {
            "title": "Tech Stack Overview",
            "content": """
            Our Technology Stack:
            
            Frontend: React, TypeScript, Tailwind CSS
            Backend: Python, FastAPI, PostgreSQL
            Cloud: AWS (Bedrock, S3, Lambda)
            DevOps: Docker, GitHub Actions, Terraform
            Monitoring: CloudWatch, Datadog
            """
        },
        {
            "title": "Marketing Metrics",
            "content": """
            Marketing Performance Q4:
            
            Website Traffic: 50K unique visitors (+30%)
            Conversion Rate: 3.2% (+0.8%)
            Social Media Followers: 10K (+25%)
            Email Open Rate: 28% (+5%)
            Cost per Acquisition: $45 (-15%)
            """
        },
        {
            "title": "Product Roadmap",
            "content": """
            2024 Product Roadmap:
            
            Q1: Mobile app launch
            Q2: API v2.0 release
            Q3: AI-powered analytics
            Q4: Enterprise features
            Ongoing: Performance optimization
            """
        }
    ]
    
    results = []
    
    for item in contents:
        print(f"\n🎯 Generating: {item['title']}")
        
        try:
            result = await orchestrator.generate_infographic(
                user_input=item['content'],
                platform="general",
                output_format="PNG"
            )
            
            results.append({
                "title": item['title'],
                "url": result.s3_url,
                "path": result.image_path
            })
            
            print(f"✅ Generated: {result.s3_url}")
            
        except Exception as e:
            print(f"❌ Error generating {item['title']}: {e}")
    
    print(f"\n📊 Batch Results Summary:")
    print(f"Generated {len(results)} infographics successfully")
    for result in results:
        print(f"  • {result['title']}: {result['url']}")


async def custom_configuration_example():
    """Example with custom configuration options."""
    print("\n⚙️ Custom Configuration Example")
    print("=" * 50)
    
    # Custom configuration
    config = {
        "max_image_size": 1024,
        "color_scheme": "professional",
        "font_family": "Arial",
        "include_branding": True
    }
    
    orchestrator = InfographicOrchestrator(config=config)
    
    content = """
    Security Best Practices:
    
    1. Use strong, unique passwords for all accounts
    2. Enable two-factor authentication (2FA)
    3. Keep software and systems updated
    4. Regular security audits and penetration testing
    5. Employee security awareness training
    6. Backup data regularly and test recovery procedures
    """
    
    try:
        result = await orchestrator.generate_infographic(
            user_input=content,
            platform="twitter",
            output_format="PNG"
        )
        
        print(f"✅ Custom configured infographic: {result.s3_url}")
        print(f"🎨 Applied configuration: {config}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all examples."""
    print("🚀 AWS Infographic Generator - Usage Examples")
    print("=" * 60)
    
    # Check environment setup
    required_env_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", 
        "S3_BUCKET_NAME",
        "BEDROCK_MODEL_ID"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file configuration.")
        return
    
    print("✅ Environment configuration looks good!")
    
    # Run examples
    await basic_example()
    await platform_specific_examples()
    await batch_generation_example()
    await custom_configuration_example()
    
    print("\n🎉 All examples completed!")
    print("Check the generated infographics in your S3 bucket.")


if __name__ == "__main__":
    asyncio.run(main())