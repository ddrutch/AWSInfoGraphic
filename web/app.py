import sys
import os
from pathlib import Path

# Ensure the project root is on sys.path so imports work when running
# this file from the `web/` directory (e.g., `py app.py`).
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flask import Flask, render_template, request, jsonify
import asyncio

from agents.content_analyzer import create_content_analyzer_agent
from agents.image_sourcer import create_image_sourcer_agent
from agents.layout_agent import create_layout_agent
from agents.image_composer import create_image_composer_agent
from utils.constants import DEMO_MODE as GLOBAL_DEMO_MODE

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
    return render_template('index.html', demo_mode=GLOBAL_DEMO_MODE)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    payload = request.json or {}
    content = payload.get('content', '')
    platform = payload.get('platform', 'general')
    demo = payload.get('demo', None)

    # Allow per-request demo override
    if demo is not None:
        os.environ['AWSINFOGRAPHIC_DEMO_MODE'] = '1' if demo else '0'

    agent = create_content_analyzer_agent()

    # Run the async process synchronously for simplicity
    try:
        result = asyncio.run(agent.process(content, platform=platform))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    return jsonify(result)


@app.route('/api/full_analyze', methods=['POST'])
def full_analyze():
    payload = request.json or {}
    content = payload.get('content', '')
    platform = payload.get('platform', 'general')
    demo = payload.get('demo', None)

    # Allow per-request demo override
    if demo is not None:
        os.environ['AWSINFOGRAPHIC_DEMO_MODE'] = '1' if demo else '0'

    async def run_pipeline():
        try:
            # Step 1: Content Analysis
            content_agent = create_content_analyzer_agent()
            content_result = await content_agent.process(content, platform=platform)
            if not content_result.get('success', False):
                return {'success': False, 'error': 'Content analysis failed', 'step': 'content'}

            content_analysis = content_result['analysis']

            # Step 2: Image Sourcing
            image_agent = create_image_sourcer_agent()
            image_result = await image_agent.process(content_analysis)
            if not image_result.get('success', False):
                return {'success': False, 'error': 'Image sourcing failed', 'step': 'images'}

            image_assets = image_result['images'] if 'images' in image_result else image_result.get('assets', [])

            # Step 3: Layout Generation
            layout_agent = create_layout_agent()
            layout_result = await layout_agent.process(content_analysis, image_assets, platform=platform)
            if not layout_result.get('success', False):
                return {'success': False, 'error': 'Layout generation failed', 'step': 'layout'}

            layout_spec = layout_result['layout']

            # Step 4: Image Composition
            composer_agent = create_image_composer_agent()

            # Prepare text specs from content analysis and layout
            text_specs = []
            if 'key_points' in content_analysis and content_analysis['key_points']:
                for i, point in enumerate(content_analysis['key_points'][:6]):  # Limit to 6 points
                    text_specs.append({
                        'text': point,
                        'position': [0.1, 0.2 + i * 0.12],  # Vertical spacing
                        'font_size': 18,
                        'font_family': 'Arial',
                        'color': '#333333',
                        'alignment': 'left'
                    })

            # Add title if available
            if 'suggested_title' in content_analysis and content_analysis['suggested_title']:
                text_specs.insert(0, {
                    'text': content_analysis['suggested_title'],
                    'position': [0.1, 0.1],
                    'font_size': 24,
                    'font_family': 'Arial',
                    'color': '#1a365d',
                    'alignment': 'left',
                    'bold': True
                })

            composition_result = await composer_agent.process(
                layout_spec=layout_spec,
                text_specs=text_specs,
                image_specs=image_assets,
                platform=platform
            )
            if not composition_result.get('success', False):
                return {'success': False, 'error': 'Image composition failed', 'step': 'composition'}

            return {
                'success': True,
                'content_analysis': content_analysis,
                'image_assets': image_assets,
                'layout_spec': layout_spec,
                'final_infographic': composition_result['composition'],
                'platform': platform,
                'pipeline_steps': ['content', 'images', 'layout', 'composition']
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Run the async pipeline synchronously
    result = asyncio.run(run_pipeline())
    return jsonify(result)


if __name__ == '__main__':
    # Helpful defaults for local testing
    app.run(host='127.0.0.1', port=5000, debug=True)
