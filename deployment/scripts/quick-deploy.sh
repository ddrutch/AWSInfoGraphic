#!/bin/bash

# Quick deployment script for AWS Infographic Generator
# Usage: ./quick-deploy.sh [environment] [deployment-type]

set -e

# Default values
ENVIRONMENT=${1:-dev}
DEPLOYMENT_TYPE=${2:-all}
REGION=${AWS_REGION:-us-east-1}

echo "🚀 AWS Infographic Generator Deployment"
echo "Environment: $ENVIRONMENT"
echo "Deployment Type: $DEPLOYMENT_TYPE"
echo "Region: $REGION"
echo "----------------------------------------"

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

# Check Docker (if needed)
if [[ "$DEPLOYMENT_TYPE" == "docker" || "$DEPLOYMENT_TYPE" == "all" ]]; then
    if ! command -v docker &> /dev/null; then
        echo "⚠️  Docker not found. Skipping Docker deployment."
        if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
            exit 1
        fi
    fi
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies for deployment script
echo "📦 Installing deployment dependencies..."
pip3 install boto3 botocore --quiet

# Run deployment
echo "🔧 Starting deployment..."
cd "$(dirname "$0")"

python3 deploy.py \
    --environment "$ENVIRONMENT" \
    --region "$REGION" \
    --deployment-type "$DEPLOYMENT_TYPE" \
    --validate

echo "✅ Deployment completed successfully!"

# Display useful information
echo ""
echo "📊 Deployment Information:"
echo "- Environment: $ENVIRONMENT"
echo "- Region: $REGION"
echo "- Stack Name: aws-infographic-generator-$ENVIRONMENT"

if [[ "$DEPLOYMENT_TYPE" == "infrastructure" || "$DEPLOYMENT_TYPE" == "all" ]]; then
    echo ""
    echo "🔗 Useful AWS Console Links:"
    echo "- CloudFormation: https://console.aws.amazon.com/cloudformation/home?region=$REGION"
    echo "- Lambda Functions: https://console.aws.amazon.com/lambda/home?region=$REGION"
    echo "- S3 Buckets: https://console.aws.amazon.com/s3/home?region=$REGION"
    echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups"
fi

if [[ "$DEPLOYMENT_TYPE" == "docker" || "$DEPLOYMENT_TYPE" == "all" ]]; then
    echo ""
    echo "🐳 Docker Information:"
    echo "- Container: aws-infographic-generator-$ENVIRONMENT"
    echo "- Check status: docker ps | grep infographic"
    echo "- View logs: docker logs aws-infographic-generator"
fi

echo ""
echo "🎉 Ready to generate infographics!"