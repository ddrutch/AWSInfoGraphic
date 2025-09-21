# Images Directory

This directory contains architecture diagrams and visual assets for the AWS Infographic Generator.

## Files

- `architecture.png` - System architecture diagram showing AWS services integration
- `workflow.png` - Multi-agent workflow diagram
- `sample_output.png` - Example infographic outputs

## Architecture Overview

The AWS Infographic Generator uses the following AWS services:

1. **Amazon Bedrock** - Content analysis and reasoning using Claude 3.5 Sonnet
2. **Amazon Nova Canvas** - AI-powered image generation
3. **Amazon S3** - Asset storage and final output hosting
4. **AWS Strands SDK** - Multi-agent orchestration framework

## Multi-Agent Workflow

1. **Content Analyzer** - Extracts key points and structure from text
2. **Image Sourcer** - Generates relevant images using Nova Canvas
3. **Design Layout** - Creates optimal visual layouts for target platforms
4. **Text Formatter** - Applies typography and styling
5. **Image Generator** - Composites final infographic and uploads to S3

The orchestrator coordinates all agents to produce platform-optimized infographics for WhatsApp, Twitter, Discord, and general use.