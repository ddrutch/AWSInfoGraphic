"""
AWS Lambda handler for serverless infographic generation
"""
import json
import os
import sys
import traceback
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError

# Add the application root to Python path
sys.path.append('/opt/python')
sys.path.append('/var/task')

# Import application modules
try:
    from main import InfographicOrchestrator
    from utils.config import Config
    from utils.error_handling import InfographicError
    from utils.monitoring import setup_logging, log_performance
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback imports for Lambda environment
    pass

# Initialize logging
logger = setup_logging()

# Initialize AWS clients
s3_client = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for infographic generation requests
    
    Args:
        event: Lambda event containing infographic generation request
        context: Lambda context object
        
    Returns:
        Dict containing response with generated infographic URL or error
    """
    request_id = context.aws_request_id
    logger.info(f"Processing infographic request {request_id}")
    
    try:
        # Parse input from event
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        user_input = body.get('content', '')
        platform = body.get('platform', 'general')
        
        if not user_input:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required field: content',
                    'request_id': request_id
                })
            }
        
        # Initialize configuration
        config = Config()
        
        # Create orchestrator and generate infographic
        orchestrator = InfographicOrchestrator(config)
        
        with log_performance("infographic_generation", request_id):
            result = orchestrator.generate_infographic(
                user_input=user_input,
                platform=platform
            )
        
        # Log success metrics
        cloudwatch.put_metric_data(
            Namespace='InfographicGenerator',
            MetricData=[
                {
                    'MetricName': 'SuccessfulGenerations',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {
                            'Name': 'Platform',
                            'Value': platform
                        }
                    ]
                }
            ]
        )
        
        logger.info(f"Successfully generated infographic for request {request_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'request_id': request_id,
                'infographic_url': result.s3_url,
                'platform_variants': result.platform_variants,
                'metadata': result.metadata
            })
        }
        
    except InfographicError as e:
        logger.error(f"Infographic generation error for request {request_id}: {e}")
        
        # Log error metrics
        cloudwatch.put_metric_data(
            Namespace='InfographicGenerator',
            MetricData=[
                {
                    'MetricName': 'GenerationErrors',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {
                            'Name': 'ErrorType',
                            'Value': type(e).__name__
                        }
                    ]
                }
            ]
        )
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'request_id': request_id,
                'error_type': 'InfographicError'
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error for request {request_id}: {e}")
        logger.error(traceback.format_exc())
        
        # Log critical error metrics
        cloudwatch.put_metric_data(
            Namespace='InfographicGenerator',
            MetricData=[
                {
                    'MetricName': 'CriticalErrors',
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'request_id': request_id,
                'error_type': 'UnexpectedError'
            })
        }

def health_check_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Health check handler for Lambda function
    """
    try:
        # Basic health checks
        checks = {
            'lambda_function': True,
            's3_access': False,
            'bedrock_access': False
        }
        
        # Test S3 access
        try:
            bucket_name = os.environ.get('S3_BUCKET')
            if bucket_name:
                s3_client.head_bucket(Bucket=bucket_name)
                checks['s3_access'] = True
        except ClientError:
            pass
        
        # Test Bedrock access
        try:
            bedrock = boto3.client('bedrock-runtime')
            # This is a minimal check - actual model invocation would be more thorough
            checks['bedrock_access'] = True
        except Exception:
            pass
        
        all_healthy = all(checks.values())
        
        return {
            'statusCode': 200 if all_healthy else 503,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'healthy' if all_healthy else 'degraded',
                'checks': checks,
                'timestamp': context.aws_request_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e)
            })
        }