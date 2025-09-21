# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the AWS Infographic Generator.

## Quick Diagnostics

### Health Check Script

Run this script to verify your setup:

```python
#!/usr/bin/env python3
"""Health check script for AWS Infographic Generator."""

import os
import asyncio
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

async def health_check():
    """Perform comprehensive health check."""
    
    print("🔍 AWS Infographic Generator Health Check")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    required_vars = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY", 
        "AWS_REGION",
        "S3_BUCKET_NAME",
        "BEDROCK_MODEL_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 4) + value[-4:]}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing variables: {', '.join(missing_vars)}")
        return False
    
    # Check AWS credentials
    print("\n🔐 AWS Credentials:")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ User/Role: {identity['Arn']}")
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        return False
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False
    
    # Check S3 bucket
    print("\n📦 S3 Bucket:")
    try:
        s3 = boto3.client('s3')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' accessible")
        
        # Test upload
        test_key = "health-check/test.txt"
        s3.put_object(Bucket=bucket_name, Key=test_key, Body=b"test")
        s3.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Upload/delete permissions working")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to bucket '{bucket_name}'")
        else:
            print(f"❌ S3 error: {e}")
        return False
    
    # Check Bedrock access
    print("\n🧠 Amazon Bedrock:")
    try:
        bedrock = boto3.client('bedrock-runtime')
        model_id = os.getenv('BEDROCK_MODEL_ID')
        
        # Test model invocation
        response = bedrock.invoke_model(
            modelId=model_id,
            body='{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"Hello"}]}'
        )
        print(f"✅ Model '{model_id}' accessible")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print(f"❌ Access denied to Bedrock model '{model_id}'")
            print("   Check model access in Bedrock console")
        elif error_code == 'ValidationException':
            print(f"❌ Invalid model ID: '{model_id}'")
        else:
            print(f"❌ Bedrock error: {e}")
        return False
    
    # Check Nova Canvas (if configured)
    nova_model = os.getenv('NOVA_CANVAS_MODEL_ID')
    if nova_model:
        print("\n🎨 Amazon Nova Canvas:")
        try:
            # Test Nova Canvas access (simplified check)
            bedrock.invoke_model(
                modelId=nova_model,
                body='{"taskType":"TEXT_IMAGE","textToImageParams":{"text":"test"}}'
            )
            print(f"✅ Nova Canvas '{nova_model}' accessible")
        except ClientError as e:
            print(f"❌ Nova Canvas error: {e}")
    
    print("\n✅ Health check completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(health_check())
```

## Common Issues

### 1. AWS Credentials Issues

#### Symptom
```
NoCredentialsError: Unable to locate credentials
```

#### Causes & Solutions

**Missing AWS credentials:**
```bash
# Solution 1: Configure AWS CLI
aws configure

# Solution 2: Set environment variables
export AWS_ACCESS_KEY_ID=your_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_here
export AWS_DEFAULT_REGION=us-east-1

# Solution 3: Use IAM roles (for EC2/Lambda)
# Attach appropriate IAM role to your compute resource
```

**Incorrect credentials:**
```bash
# Verify credentials
aws sts get-caller-identity

# Expected output:
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012", 
    "Arn": "arn:aws:iam::123456789012:user/username"
}
```

**Region mismatch:**
```bash
# Check current region
aws configure get region

# Set correct region
aws configure set region us-east-1
```

### 2. Bedrock Access Issues

#### Symptom
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel
```

#### Solutions

**Enable model access:**
1. Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access" in left sidebar
3. Click "Request model access"
4. Enable access for required models:
   - Anthropic Claude 3.5 Sonnet
   - Amazon Nova Canvas

**Check IAM permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:*::foundation-model/amazon.nova-canvas-v1:0"
            ]
        }
    ]
}
```

**Region availability:**
```python
# Check if Bedrock is available in your region
import boto3

bedrock = boto3.client('bedrock', region_name='us-east-1')
try:
    models = bedrock.list_foundation_models()
    print("Bedrock available in region")
except Exception as e:
    print(f"Bedrock not available: {e}")
```

### 3. S3 Bucket Issues

#### Symptom
```
NoSuchBucket: The specified bucket does not exist
```

#### Solutions

**Create bucket:**
```bash
# Create S3 bucket
aws s3 mb s3://your-infographic-bucket --region us-east-1

# Verify bucket exists
aws s3 ls s3://your-infographic-bucket
```

**Fix bucket permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject", 
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-infographic-bucket/*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::your-infographic-bucket"
        }
    ]
}
```

**Cross-region issues:**
```bash
# Ensure bucket and compute are in same region
aws s3api get-bucket-location --bucket your-infographic-bucket
```

### 4. Image Generation Issues

#### Symptom
```
ImageGenerationError: Failed to generate image using Nova Canvas
```

#### Solutions

**Check Nova Canvas availability:**
```python
# Verify Nova Canvas is available in your region
import boto3

bedrock = boto3.client('bedrock')
models = bedrock.list_foundation_models()

nova_models = [m for m in models['modelSummaries'] 
               if 'nova-canvas' in m['modelId']]

if nova_models:
    print("Nova Canvas available")
else:
    print("Nova Canvas not available in this region")
```

**Fallback to placeholder images:**
```python
# Enable fallback in configuration
config = {
    "enable_image_fallback": True,
    "fallback_image_type": "placeholder"
}
```

**Prompt optimization:**
```python
# Improve image generation prompts
def optimize_prompt(original_prompt: str) -> str:
    """Optimize prompt for better Nova Canvas results."""
    
    # Add style guidance
    optimized = f"{original_prompt}, professional style, clean design, high quality"
    
    # Remove problematic terms
    problematic_terms = ["violent", "inappropriate", "copyrighted"]
    for term in problematic_terms:
        optimized = optimized.replace(term, "")
    
    return optimized
```

### 5. Memory and Performance Issues

#### Symptom
```
MemoryError: Unable to allocate memory for image processing
```

#### Solutions

**Reduce image size:**
```python
# Configure smaller image sizes
config = {
    "max_image_size": 1024,  # Reduce from 2048
    "image_quality": 85      # Reduce from 95
}
```

**Optimize PIL usage:**
```python
from PIL import Image

# Use memory-efficient image processing
def process_image_efficiently(image_path: str):
    with Image.open(image_path) as img:
        # Process image without loading full resolution
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        return img.copy()
```

**Monitor memory usage:**
```python
import psutil
import gc

def monitor_memory():
    """Monitor memory usage during generation."""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
    
    if memory_mb > 1000:  # 1GB threshold
        gc.collect()  # Force garbage collection
```

### 6. Network and Timeout Issues

#### Symptom
```
TimeoutError: Request timed out after 300 seconds
```

#### Solutions

**Increase timeouts:**
```python
config = {
    "timeout_seconds": 600,  # Increase from 300
    "max_retries": 5,        # Increase retry attempts
    "retry_delay": 2         # Delay between retries
}
```

**Implement exponential backoff:**
```python
import asyncio
import random

async def retry_with_backoff(func, max_retries=3):
    """Retry function with exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

**Check network connectivity:**
```python
import requests

def check_aws_connectivity():
    """Check connectivity to AWS services."""
    
    endpoints = [
        "https://bedrock-runtime.us-east-1.amazonaws.com",
        "https://s3.us-east-1.amazonaws.com"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            print(f"✅ {endpoint}: Reachable")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
```

### 7. Content Analysis Issues

#### Symptom
```
ContentAnalysisError: Unable to extract meaningful content
```

#### Solutions

**Improve content preprocessing:**
```python
def preprocess_content(text: str) -> str:
    """Preprocess content for better analysis."""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Ensure minimum content length
    if len(text) < 10:
        raise ValueError("Content too short for analysis")
    
    # Ensure maximum content length
    if len(text) > 5000:
        text = text[:5000] + "..."
    
    return text
```

**Fallback content structure:**
```python
def create_fallback_analysis(text: str) -> ContentAnalysis:
    """Create basic content analysis when AI analysis fails."""
    
    # Simple sentence splitting
    sentences = text.split('.')
    key_points = [s.strip() for s in sentences if len(s.strip()) > 10][:5]
    
    return ContentAnalysis(
        main_topic="Content Summary",
        key_points=key_points,
        hierarchy={"main": key_points},
        summary=text[:200] + "..." if len(text) > 200 else text,
        suggested_title="Generated Content"
    )
```

### 8. Layout and Design Issues

#### Symptom
```
LayoutError: Unable to fit content in specified dimensions
```

#### Solutions

**Dynamic text sizing:**
```python
def calculate_dynamic_font_size(text: str, max_width: int, max_height: int) -> int:
    """Calculate font size that fits within constraints."""
    
    # Start with reasonable font size
    font_size = 24
    
    while font_size > 8:  # Minimum readable size
        # Estimate text dimensions (simplified)
        estimated_width = len(text) * font_size * 0.6
        estimated_height = font_size * 1.2
        
        if estimated_width <= max_width and estimated_height <= max_height:
            return font_size
        
        font_size -= 2
    
    return 8  # Minimum font size
```

**Responsive layouts:**
```python
def create_responsive_layout(content: ContentAnalysis, platform: str) -> LayoutSpecification:
    """Create layout that adapts to content and platform."""
    
    platform_specs = {
        "whatsapp": {"max_elements": 4, "font_scale": 1.2},
        "twitter": {"max_elements": 5, "font_scale": 1.0},
        "discord": {"max_elements": 7, "font_scale": 0.9}
    }
    
    spec = platform_specs.get(platform, platform_specs["twitter"])
    
    # Limit content to fit platform
    key_points = content.key_points[:spec["max_elements"]]
    
    return LayoutSpecification(
        canvas_size=get_platform_dimensions(platform),
        elements=create_elements(key_points, spec["font_scale"]),
        # ... other layout properties
    )
```

## Debugging Tools

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable AWS SDK debug logging
boto3.set_stream_logger('boto3', logging.DEBUG)
boto3.set_stream_logger('botocore', logging.DEBUG)
```

### Performance Profiling

```python
import cProfile
import pstats
from functools import wraps

def profile_function(func):
    """Decorator to profile function performance."""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # Top 10 functions
    
    return wrapper

# Usage
@profile_function
async def generate_infographic_with_profiling(content: str):
    orchestrator = InfographicOrchestrator()
    return await orchestrator.generate_infographic(content)
```

### Memory Monitoring

```python
import tracemalloc
import asyncio

async def monitor_memory_usage():
    """Monitor memory usage during generation."""
    
    tracemalloc.start()
    
    # Your infographic generation code here
    orchestrator = InfographicOrchestrator()
    result = await orchestrator.generate_infographic("Test content")
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

## Getting Help

### Log Collection

When reporting issues, include these logs:

```bash
# Application logs
tail -f /var/log/infographic-generator.log

# AWS CLI debug
aws --debug s3 ls s3://your-bucket 2>&1 | head -50

# System information
python --version
pip list | grep -E "(boto3|pillow|asyncio)"
```

### Issue Template

When reporting issues, include:

1. **Environment Information:**
   - Python version
   - Operating system
   - AWS region
   - Package versions

2. **Configuration:**
   - Sanitized .env file (remove secrets)
   - Custom configuration options

3. **Error Details:**
   - Full error traceback
   - Input content that caused the error
   - Expected vs actual behavior

4. **Reproduction Steps:**
   - Minimal code to reproduce the issue
   - Sample input data
   - Configuration used

### Support Channels

- **GitHub Issues:** For bug reports and feature requests
- **AWS Support:** For AWS service-specific issues
- **Documentation:** Check API reference and examples
- **Health Check:** Run the diagnostic script first

### Emergency Procedures

**Service Outage:**
1. Check AWS Service Health Dashboard
2. Enable fallback modes in configuration
3. Switch to alternative AWS regions if needed
4. Implement circuit breaker patterns

**Data Loss Prevention:**
1. Enable S3 versioning on your bucket
2. Set up cross-region replication
3. Regular backup of configuration files
4. Monitor S3 access logs

**Security Incident:**
1. Rotate AWS credentials immediately
2. Review CloudTrail logs for unauthorized access
3. Update IAM policies to minimum required permissions
4. Enable AWS Config for compliance monitoring