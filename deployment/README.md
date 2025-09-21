# AWS Infographic Generator - Deployment Guide

This directory contains all the deployment configurations and scripts for the AWS Infographic Generator system.

## Directory Structure

```
deployment/
├── cloudformation/          # Infrastructure as Code templates
│   └── infographic-generator.yaml
├── docker/                  # Container deployment configurations
│   ├── Dockerfile
│   └── docker-compose.yml
├── lambda/                  # Serverless deployment files
│   ├── lambda_handler.py
│   └── requirements.txt
├── monitoring/              # CloudWatch monitoring setup
│   ├── cloudwatch-dashboard.json
│   └── alarms.yaml
├── iam/                     # IAM policies and roles
│   └── policies.json
├── scripts/                 # Deployment automation scripts
│   └── deploy.py
└── README.md               # This file
```

## Deployment Options

### 1. Infrastructure Deployment (CloudFormation)

Deploy the core AWS infrastructure including S3 buckets, IAM roles, and Lambda functions:

```bash
# Deploy to development environment
python deployment/scripts/deploy.py --environment dev --deployment-type infrastructure

# Deploy to production environment
python deployment/scripts/deploy.py --environment prod --deployment-type infrastructure
```

**Resources Created:**
- S3 bucket for storing generated infographics
- IAM roles and policies for Lambda and ECS
- Lambda function for serverless execution
- CloudWatch log groups

### 2. Lambda Deployment (Serverless)

Deploy the infographic generator as a serverless Lambda function:

```bash
# Deploy Lambda function
python deployment/scripts/deploy.py --environment dev --deployment-type lambda

# Deploy everything (infrastructure + lambda)
python deployment/scripts/deploy.py --environment dev --deployment-type all
```

**Features:**
- Automatic scaling based on demand
- Pay-per-use pricing model
- 15-minute maximum execution time
- 3GB memory allocation for image processing

### 3. Docker Deployment (Containerized)

Deploy using Docker containers for local development or container orchestration:

```bash
# Build and deploy with Docker Compose
python deployment/scripts/deploy.py --environment dev --deployment-type docker

# Or manually with Docker Compose
cd deployment/docker
docker-compose up -d --build
```

**Features:**
- Consistent environment across deployments
- Easy local development setup
- Includes LocalStack for local AWS services testing
- Health checks and logging configuration

## Prerequisites

### AWS Configuration

1. **AWS CLI Setup:**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and default region
   ```

2. **Required AWS Permissions:**
   - CloudFormation stack management
   - IAM role and policy management
   - Lambda function management
   - S3 bucket management
   - CloudWatch logs and metrics

3. **AWS Services Used:**
   - Amazon Bedrock (for LLM capabilities)
   - Amazon S3 (for asset storage)
   - AWS Lambda (for serverless execution)
   - Amazon CloudWatch (for monitoring and logging)
   - AWS IAM (for access control)

### Local Development

1. **Python Dependencies:**
   ```bash
   pip install boto3 botocore
   ```

2. **Docker (for container deployment):**
   ```bash
   # Install Docker and Docker Compose
   docker --version
   docker-compose --version
   ```

3. **Environment Variables:**
   Create a `.env` file in the project root:
   ```env
   AWS_REGION=us-east-1
   S3_BUCKET=aws-infographic-generator-assets-dev
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   ```

## Configuration

### Environment-Specific Settings

The deployment system supports multiple environments with different configurations:

- **Development (`dev`)**: Minimal resources, debug logging
- **Staging (`staging`)**: Production-like setup for testing
- **Production (`prod`)**: Optimized for performance and cost

### CloudFormation Parameters

Key parameters that can be customized:

```yaml
Parameters:
  Environment: dev|staging|prod
  ProjectName: aws-infographic-generator
  S3BucketName: aws-infographic-generator-assets
```

### Lambda Configuration

- **Runtime**: Python 3.11
- **Memory**: 3008 MB (maximum for image processing)
- **Timeout**: 900 seconds (15 minutes)
- **Environment Variables**: S3_BUCKET, ENVIRONMENT, LOG_LEVEL

### Docker Configuration

- **Base Image**: python:3.11-slim
- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for container monitoring

## Monitoring and Logging

### CloudWatch Dashboard

Deploy the monitoring dashboard:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name "InfographicGenerator-dev" \
  --dashboard-body file://deployment/monitoring/cloudwatch-dashboard.json
```

**Metrics Tracked:**
- Successful infographic generations
- Generation errors by type
- Lambda function performance
- S3 storage usage
- Platform-specific usage statistics

### CloudWatch Alarms

Deploy monitoring alarms:

```bash
aws cloudformation deploy \
  --template-file deployment/monitoring/alarms.yaml \
  --stack-name infographic-generator-alarms-dev \
  --parameter-overrides Environment=dev NotificationEmail=your-email@example.com \
  --capabilities CAPABILITY_IAM
```

**Alarms Configured:**
- High error rates
- Long execution times
- Lambda throttling
- Critical system errors
- S3 storage size limits

## Security

### IAM Policies

The system uses least-privilege IAM policies:

- **Bedrock Access**: Limited to specific foundation models
- **S3 Access**: Scoped to project-specific buckets
- **CloudWatch**: Limited to project log groups and metrics
- **Lambda**: Basic execution permissions only

### Security Best Practices

1. **Credential Management**: Use IAM roles, never hardcode credentials
2. **Network Security**: VPC configuration for production deployments
3. **Data Encryption**: S3 server-side encryption enabled
4. **Access Logging**: CloudTrail integration for audit trails
5. **Resource Tagging**: Consistent tagging for cost allocation and management

## Troubleshooting

### Common Issues

1. **CloudFormation Stack Failures:**
   ```bash
   # Check stack events for detailed error messages
   aws cloudformation describe-stack-events --stack-name aws-infographic-generator-dev
   ```

2. **Lambda Deployment Issues:**
   ```bash
   # Check Lambda function logs
   aws logs tail /aws/lambda/aws-infographic-generator-generator-dev --follow
   ```

3. **Docker Build Failures:**
   ```bash
   # Build with verbose output
   docker build --no-cache -f deployment/docker/Dockerfile .
   ```

4. **Permission Errors:**
   - Verify AWS credentials and permissions
   - Check IAM role trust relationships
   - Ensure CloudFormation capabilities are granted

### Validation

Run deployment validation:

```bash
python deployment/scripts/deploy.py --environment dev --validate
```

This checks:
- S3 bucket accessibility
- Lambda function status
- IAM role configurations
- CloudWatch log group creation

## Cost Optimization

### Lambda Pricing

- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second
- **Estimated cost**: ~$0.50 per 1000 infographic generations

### S3 Storage

- **Standard Storage**: $0.023 per GB per month
- **Lifecycle policies**: Automatic cleanup of old files
- **Estimated cost**: ~$2.30 per month for 100GB storage

### Bedrock Usage

- **Model invocation costs** vary by model
- **Claude 3 Haiku**: ~$0.25 per 1M input tokens
- **Nova Canvas**: ~$0.04 per image generation

## Support and Maintenance

### Monitoring

- Set up CloudWatch alarms for proactive monitoring
- Review CloudWatch Insights queries for performance analysis
- Monitor AWS costs using Cost Explorer

### Updates

- Use blue-green deployments for zero-downtime updates
- Test changes in staging environment first
- Maintain rollback procedures for critical issues

### Backup and Recovery

- S3 versioning enabled for generated assets
- CloudFormation templates stored in version control
- Regular backup of configuration and deployment scripts

## Next Steps

1. **Deploy to Development**: Start with `dev` environment
2. **Configure Monitoring**: Set up CloudWatch dashboard and alarms
3. **Test Functionality**: Validate infographic generation end-to-end
4. **Scale to Production**: Deploy to `prod` environment with appropriate sizing
5. **Optimize Costs**: Review usage patterns and adjust resource allocation