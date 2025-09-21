# AWS Infographic Generator 🎨 🤖

Author: AWS AI Agent Global Hackathon Team

AWS Infographic Generator is a multi-agent system that transforms text content into visually compelling infographics using AWS services. Built with the Strands SDK and powered by Amazon Bedrock, this system orchestrates specialized agents for content analysis, image sourcing, layout design, text formatting, and final image generation. The project migrates from Google services (ADK, Slides API, Gemini) to a fully AWS-native solution for the AWS AI Agent Global Hackathon.

## Architecture Overview

The AWS Infographic Generator uses a multi-agent architecture powered by AWS services. For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

### High-Level Architecture

```mermaid
graph TB
    User[👤 User Input] --> Orchestrator[🎯 InfographicOrchestrator]
    
    Orchestrator --> ContentAnalyzer[📝 ContentAnalyzer]
    Orchestrator --> ImageSourcer[🖼️ ImageSourcer]
    Orchestrator --> DesignLayout[🎨 DesignLayout]
    Orchestrator --> TextFormatter[✍️ TextFormatter]
    Orchestrator --> ImageComposer[🖌️ ImageComposer]
    
    ContentAnalyzer --> Bedrock1[🧠 Amazon Bedrock<br/>Claude 3.5 Sonnet]
    ImageSourcer --> NovaCanvas[🎨 Amazon Nova Canvas<br/>Image Generation]
    DesignLayout --> Bedrock2[🧠 Amazon Bedrock<br/>Layout Intelligence]
    TextFormatter --> PIL[🔤 PIL/Pillow<br/>Text Processing]
    ImageComposer --> PIL2[🖼️ PIL/Pillow<br/>Image Composition]
    
    ImageSourcer --> S3Cache[📦 Amazon S3<br/>Image Cache]
    ImageComposer --> S3Output[📤 Amazon S3<br/>Final Output]
    
    S3Output --> URLs[🔗 Shareable URLs<br/>Platform Optimized]
    
    subgraph "AWS Services"
        Bedrock1
        Bedrock2
        NovaCanvas
        S3Cache
        S3Output
    end
    
    subgraph "Platform Outputs"
        WhatsApp[📱 WhatsApp<br/>1080x1080]
        Twitter[🐦 Twitter<br/>1200x675]
        Discord[💬 Discord<br/>1920x1080]
        General[🌐 General<br/>1920x1080]
    end
    
    URLs --> WhatsApp
    URLs --> Twitter
    URLs --> Discord
    URLs --> General
    
    style User fill:#e1f5fe
    style Orchestrator fill:#f3e5f5
    style Bedrock1 fill:#fff3e0
    style Bedrock2 fill:#fff3e0
    style NovaCanvas fill:#fff3e0
    S3Cache fill:#e8f5e8
    style S3Output fill:#e8f5e8
```

📊 **[View Detailed Architecture Diagrams](docs/architecture_diagram.md)** - Comprehensive system architecture, data flow, security, and deployment diagrams.

### AWS Services Integration

The system leverages multiple AWS services for a fully cloud-native solution:

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Amazon Bedrock** | Content analysis & reasoning | Claude 3.5 Sonnet model |
| **Amazon Nova Canvas** | AI image generation | Text-to-image generation |
| **Amazon S3** | Asset storage & hosting | Public read bucket with lifecycle policies |
| **AWS Strands SDK** | Multi-agent orchestration | Agent framework and communication |
| **Amazon CloudWatch** | Monitoring & logging | Custom metrics and dashboards |

## 1. What is this?

A **multi-agent infographic generator** that creates platform-optimized visual content from text input.

| Function | Agent | AWS Service | Output |
|----------|-------|-------------|--------|
| **Orchestration** | `InfographicOrchestrator` | Strands SDK + Bedrock | Coordinated workflow |
| **Content Analysis** | `ContentAnalyzer` | Amazon Bedrock | Structured content extraction |
| **Image Sourcing** | `ImageSourcer` | Amazon Nova Canvas | Generated/sourced images |
| **Layout Design** | `DesignLayout` | Amazon Bedrock | Visual layout specification |
| **Text Formatting** | `TextFormatter` | Custom algorithms | Typography and styling |
| **Image Generation** | `ImageGenerator` | PIL/Pillow + S3 | Final infographic files |

## 2. Flow overview 🚦

1. **User** ➜ `InfographicOrchestrator` with text content and platform preference
2. `ContentAnalyzer` extracts key points, topics, and structure using Amazon Bedrock
3. `ImageSourcer` generates relevant images using Amazon Nova Canvas
4. `DesignLayout` creates optimal visual layout for target platform
5. `TextFormatter` applies typography, colors, and styling
6. `ImageGenerator` composites final infographic and uploads to S3
7. **Platform-optimized infographic** returned with shareable S3 URL

## 3. Supported Platforms 📱

The system generates optimized infographics for multiple platforms:

| Platform | Dimensions | Aspect Ratio | Optimizations |
|----------|------------|--------------|---------------|
| **WhatsApp** | 1080x1080 | 1:1 | Square format, larger text |
| **Twitter** | 1200x675 | 16:9 | Landscape, social-friendly |
| **Discord** | 1920x1080 | 16:9 | High resolution, detailed |
| **General** | 1920x1080 | 16:9 | Universal format |

## 4. Quick start 🛠️ (local dev)

### Prerequisites

- Python 3.12+
- AWS CLI v2 configured
- [Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html) to Amazon Bedrock (Claude 3.5 Sonnet)
- [Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html) to Amazon Nova Canvas
- S3 bucket for asset storage

### AWS Setup Instructions

#### 1. Install AWS CLI

**Windows:**
```powershell
# Download and install AWS CLI v2
# Visit: https://awscli.amazonaws.com/AWSCLIV2.msi
# Or use winget
winget install Amazon.AWSCLI

# Verify installation
aws --version
```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install awscli

# Or download installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version
```

**Linux:**
```bash
# Download and install
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

#### 2. Configure AWS Credentials

**Option A: Interactive Configuration**
```bash
aws configure
# AWS Access Key ID [None]: YOUR_ACCESS_KEY
# AWS Secret Access Key [None]: YOUR_SECRET_KEY
# Default region name [None]: us-east-1
# Default output format [None]: json
```

**Option B: Environment Variables**
```bash
# Linux/macOS
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1

# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
$env:AWS_DEFAULT_REGION="us-east-1"
```

**Option C: AWS SSO (Recommended for Organizations)**
```bash
aws configure sso
# Follow the prompts to set up SSO
```

**Verify Configuration:**
```bash
aws sts get-caller-identity
# Should return your account ID and user/role ARN
```

#### 3. Enable Bedrock Model Access

**Step-by-Step Process:**

1. **Navigate to Bedrock Console:**
   - Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
   - Ensure you're in a supported region (us-east-1, us-west-2, eu-west-1)

2. **Request Model Access:**
   - Click "Model access" in the left sidebar
   - Click "Request model access" button
   - Find and enable the following models:

**Required Models:**
- **Anthropic Claude 3.5 Sonnet v2** (`anthropic.claude-3-5-sonnet-20241022-v2:0`)
  - Use case: Content analysis and reasoning
  - Approval: Usually immediate
  
- **Amazon Nova Canvas** (`amazon.nova-canvas-v1:0`)
  - Use case: AI image generation
  - Approval: Usually immediate

3. **Verify Access:**
```bash
# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Test specific model access
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"Hello"}]}' \
  --cli-binary-format raw-in-base64-out \
  response.json
```

#### 4. Create and Configure S3 Bucket

**Create Bucket:**
```bash
# Replace 'your-unique-bucket-name' with your actual bucket name
BUCKET_NAME="your-infographic-bucket-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Verify bucket creation
aws s3 ls | grep $BUCKET_NAME
```

**Configure Bucket for Public Access (Optional):**

Create `bucket-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-infographic-bucket/*"
    }
  ]
}
```

Apply the policy:
```bash
# Apply bucket policy for public read access
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

# Enable public access block settings
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

**Configure Lifecycle Policy (Recommended):**
```json
{
  "Rules": [
    {
      "ID": "DeleteOldInfographics",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "infographics/"
      },
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
```

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket $BUCKET_NAME \
  --lifecycle-configuration file://lifecycle-policy.json
```

#### 5. Set Up IAM Permissions

**Create IAM Policy:**

Create `infographic-generator-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        "arn:aws:bedrock:*::foundation-model/amazon.nova-canvas-v1:0"
      ]
    },
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-infographic-bucket/*"
    },
    {
      "Sid": "S3BucketList",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::your-infographic-bucket"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/infographic-generator/*"
    }
  ]
}
```

**Apply IAM Policy:**
```bash
# Create the policy
aws iam create-policy \
  --policy-name InfographicGeneratorPolicy \
  --policy-document file://infographic-generator-policy.json

# Attach to your user (replace YOUR_USERNAME)
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/InfographicGeneratorPolicy
```

#### 6. Verify Complete Setup

Run this verification script:
```bash
#!/bin/bash
echo "🔍 Verifying AWS Infographic Generator Setup"
echo "============================================"

# Check AWS CLI
echo "✓ Checking AWS CLI..."
aws --version

# Check credentials
echo "✓ Checking AWS credentials..."
aws sts get-caller-identity

# Check Bedrock access
echo "✓ Checking Bedrock access..."
aws bedrock list-foundation-models --region us-east-1 --query 'modelSummaries[?contains(modelId, `claude-3-5-sonnet`)].[modelId]' --output text

# Check S3 bucket
echo "✓ Checking S3 bucket..."
aws s3 ls s3://$BUCKET_NAME

echo "✅ Setup verification complete!"
```

#### 7. Regional Considerations

**Supported Regions for Bedrock:**
- `us-east-1` (N. Virginia) - **Recommended**
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-2` (Sydney)

**Note:** Not all Bedrock models are available in all regions. Check the [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) for current availability.

#### 8. Cost Optimization

**Bedrock Pricing:**
- Claude 3.5 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Nova Canvas: ~$0.04 per image

**S3 Pricing:**
- Standard storage: ~$0.023 per GB/month
- PUT requests: ~$0.0005 per 1,000 requests

**Estimated Costs:**
- 100 infographics/month: ~$5-10/month
- 1,000 infographics/month: ~$30-50/month

**Cost Optimization Tips:**
```bash
# Set up billing alerts
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget '{
  "BudgetName": "InfographicGenerator",
  "BudgetLimit": {"Amount": "50", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}'
```

### Installation

```bash
# Clone and navigate to project
cd 02-samples/14-aws-infographic-generator

# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -e .

# Copy and configure environment
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

### Configuration

Edit `.env` file with your AWS settings:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# S3 Configuration
S3_BUCKET_NAME=your-infographic-bucket
S3_REGION=us-east-1

# Bedrock Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
NOVA_CANVAS_MODEL_ID=amazon.nova-canvas-v1:0

# Application Configuration
MAX_IMAGE_SIZE=2048
DEFAULT_PLATFORM=general
LOG_LEVEL=INFO

# Optional: Custom endpoints for testing
# BEDROCK_ENDPOINT_URL=https://bedrock-runtime.us-east-1.amazonaws.com
# S3_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com
```

### Running the Application

#### Generate infographic via CLI

```bash
# Basic usage
uv run main.py "Your text content here"

# Specify platform and format
uv run main.py "Create an infographic about AI trends" twitter PNG

# WhatsApp optimized
uv run main.py "Company quarterly results summary" whatsapp
```

#### Programmatic usage

```python
from main import InfographicOrchestrator

orchestrator = InfographicOrchestrator()
result = await orchestrator.generate_infographic(
    user_input="Your content here",
    platform="twitter",
    output_format="PNG"
)

print(f"Generated infographic: {result.s3_url}")
```

## 5. AWS Architecture 🏗️ (components)

| Component Type | AWS Service | Description |
|----------------|-------------|-------------|
| **AI/ML Services** | Amazon Bedrock | Content analysis and reasoning |
| **Image Generation** | Amazon Nova Canvas | AI-powered image creation |
| **Storage Layer** | Amazon S3 | Asset storage and final output hosting |
| **Agent Framework** | AWS Strands SDK | Multi-agent orchestration |
| **Compute** | Local/Lambda | Image processing and composition |

## 6. Project Structure 📁

```
aws-infographic-generator/
├── main.py                     # Entry point and orchestrator
├── agents/                     # Specialized agents
│   ├── content_analyzer.py     # Content analysis agent
│   ├── image_sourcer.py        # Image sourcing agent
│   ├── design_layout.py        # Layout design agent
│   ├── text_formatter.py       # Text formatting agent
│   └── image_generator.py      # Final image creation agent
├── tools/                      # Utility tools
│   ├── content_tools.py        # Content analysis utilities
│   ├── image_tools.py          # Image processing utilities
│   ├── layout_tools.py         # Layout calculation tools
│   ├── s3_tools.py            # S3 upload/download tools
│   └── bedrock_tools.py       # Bedrock integration utilities
├── utils/                      # Configuration and types
│   ├── constants.py           # Configuration constants
│   ├── types.py               # Data models and types
│   └── prompts.py             # Agent system prompts
├── pyproject.toml             # Dependencies and project config
├── .env.example              # Environment configuration template
└── README.md                 # This file
```

## 7. Migration from Google Services 🔄

This project migrates from Google-based services to AWS:

| Google Service | AWS Replacement | Migration Notes |
|----------------|-----------------|-----------------|
| **Google ADK** | AWS Strands SDK | Multi-agent framework |
| **Google Gemini** | Amazon Bedrock (Claude) | LLM for content analysis |
| **Google Slides API** | PIL/Pillow + Custom | Image composition |
| **Google Cloud Storage** | Amazon S3 | Asset and output storage |
| **SerpAPI** | Amazon Nova Canvas | Image generation |

## 8. Features ✨

- **Multi-Platform Optimization**: Automatic sizing and formatting for different social platforms
- **AI-Powered Content Analysis**: Intelligent extraction of key points and structure
- **Dynamic Image Generation**: AI-generated images using Amazon Nova Canvas
- **Flexible Layout Engine**: Adaptive layouts based on content and platform
- **AWS-Native**: Fully integrated with AWS services and best practices
- **Scalable Architecture**: Multi-agent system for parallel processing
- **Error Handling**: Comprehensive fallback mechanisms and retry logic

## 9. Troubleshooting 🐞

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| **NoCredentialsError** | AWS credentials not configured | Run `aws configure` or set environment variables |
| **Bedrock AccessDenied** | Model access not enabled | Enable Claude 3.5 Sonnet in Bedrock console |
| **S3 Upload Failed** | Bucket permissions or doesn't exist | Check bucket policy and existence |
| **Nova Canvas Error** | Model not available in region | Ensure Nova Canvas is available in your region |
| **Import Error** | Missing dependencies | Run `uv sync` to install dependencies |
| **Image Generation Failed** | PIL/Pillow issues | Check image processing dependencies |

## 10. Development 🛠️

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/
```

### Code Quality

```bash
# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .

# Linting
uv run pre-commit run --all-files
```

## 11. Contributing 🤝

This project is developed for the AWS AI Agent Global Hackathon. Contributions should focus on:

- AWS service integration improvements
- Agent performance optimization
- Platform-specific enhancements
- Error handling and reliability
- Documentation and examples

## 12. Documentation 📚

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/architecture.md)** - Detailed system architecture, data flow, and AWS service integration
- **[API Reference](docs/api_reference.md)** - Complete API documentation for all agents, tools, and configuration options
- **[Developer Guide](docs/developer_guide.md)** - Information for extending and customizing the system
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues, solutions, and debugging tools

### Examples

The `examples/` directory contains:

- **[Basic Usage](examples/basic_usage.py)** - Simple examples for getting started
- **[Advanced Usage](examples/advanced_usage.py)** - Complex scenarios, error handling, and monitoring
- **[Sample Outputs](examples/sample_outputs.md)** - Example infographics and performance benchmarks

### Quick Links

| Topic | Documentation | Examples |
|-------|---------------|----------|
| **Getting Started** | [README.md](#4-quick-start-🛠️-local-dev) | [Basic Usage](examples/basic_usage.py) |
| **API Integration** | [API Reference](docs/api_reference.md) | [Advanced Usage](examples/advanced_usage.py) |
| **Troubleshooting** | [Troubleshooting Guide](docs/troubleshooting.md) | [Health Check Script](docs/troubleshooting.md#health-check-script) |
| **Architecture** | [Architecture Guide](docs/architecture.md) | [Sample Outputs](examples/sample_outputs.md) |
| **Development** | [Developer Guide](docs/developer_guide.md) | [Extension Examples](docs/developer_guide.md) |

## 13. License 📄

This project is developed for the AWS AI Agent Global Hackathon and follows AWS sample code guidelines.