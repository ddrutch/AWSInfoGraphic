"""Small demo runner to exercise the full AWS infographic pipeline.

This script runs the complete pipeline: ContentAnalyzer -> Image Sourcing -> Layout Agent.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force demo mode for local testing
os.environ['AWSINFOGRAPHIC_DEMO_MODE'] = '1'

from agents.content_analyzer import create_content_analyzer_agent
from agents.image_sourcer import create_image_sourcer_agent
from agents.layout_agent import create_layout_agent


async def demo():
    sample = (
        "The rise of serverless computing has transformed how teams build and scale applications."
        " Key benefits include reduced operational overhead, pay-for-usage pricing, and automatic scaling."
        " Use cases: web backends, event-driven processing, batch jobs."
    )

    print('=== Input Content ===')
    print(sample)
    print()

    # Step 1: Content Analysis
    print('=== Step 1: Content Analysis ===')
    content_analyzer = create_content_analyzer_agent()
    content_result = await content_analyzer.process(sample)
    print(json.dumps(content_result, indent=2))

    if not content_result.get('success', False):
        print("Content analysis failed, stopping pipeline")
        return

    content_analysis = content_result['analysis']
    print()

    # Step 2: Image Sourcing
    print('=== Step 2: Image Sourcing ===')
    image_agent = create_image_sourcer_agent()
    image_result = await image_agent.process(content_analysis)
    print(json.dumps(image_result, indent=2))

    if not image_result.get('success', False):
        print("Image sourcing failed, stopping pipeline")
        return

    image_assets = image_result['images'] if 'images' in image_result else image_result.get('assets', [])
    print()

    # Step 3: Layout Generation
    print('=== Step 3: Layout Generation ===')
    layout_agent = create_layout_agent()
    layout_result = await layout_agent.process(content_analysis, image_assets)
    print(json.dumps(layout_result, indent=2))

    print()
    print('=== Pipeline Complete ===')
    print(f"Content points: {len(content_analysis.get('key_points', []))}")
    print(f"Images sourced: {len(image_assets)}")
    print(f"Layout type: {layout_result.get('layout', {}).get('layout_type', 'unknown')}")


if __name__ == '__main__':
    asyncio.run(demo())


if __name__ == '__main__':
    asyncio.run(demo())
