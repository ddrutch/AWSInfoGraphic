#!/usr/bin/env python3
"""
Deployment script for AWS Infographic Generator
Supports CloudFormation, Docker, and Lambda deployments
"""
import argparse
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class DeploymentManager:
    """Manages deployment of the AWS Infographic Generator"""
    
    def __init__(self, environment: str = "dev", region: str = "us-east-1"):
        self.environment = environment
        self.region = region
        self.project_name = "aws-infographic-generator"
        self.stack_name = f"{self.project_name}-{environment}"
        
        # Initialize AWS clients
        try:
            self.cf_client = boto3.client('cloudformation', region_name=region)
            self.lambda_client = boto3.client('lambda', region_name=region)
            self.s3_client = boto3.client('s3', region_name=region)
            self.iam_client = boto3.client('iam', region_name=region)
        except NoCredentialsError:
            print("Error: AWS credentials not configured. Please run 'aws configure' first.")
            sys.exit(1)
    
    def deploy_infrastructure(self) -> Dict[str, str]:
        """Deploy CloudFormation infrastructure"""
        print(f"Deploying infrastructure for environment: {self.environment}")
        
        template_path = Path(__file__).parent.parent / "cloudformation" / "infographic-generator.yaml"
        
        if not template_path.exists():
            raise FileNotFoundError(f"CloudFormation template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            template_body = f.read()
        
        parameters = [
            {
                'ParameterKey': 'Environment',
                'ParameterValue': self.environment
            },
            {
                'ParameterKey': 'ProjectName',
                'ParameterValue': self.project_name
            }
        ]
        
        try:
            # Check if stack exists
            try:
                self.cf_client.describe_stacks(StackName=self.stack_name)
                stack_exists = True
            except ClientError as e:
                if 'does not exist' in str(e):
                    stack_exists = False
                else:
                    raise
            
            if stack_exists:
                print(f"Updating existing stack: {self.stack_name}")
                response = self.cf_client.update_stack(
                    StackName=self.stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_NAMED_IAM']
                )
                operation = "UPDATE"
            else:
                print(f"Creating new stack: {self.stack_name}")
                response = self.cf_client.create_stack(
                    StackName=self.stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_NAMED_IAM']
                )
                operation = "CREATE"
            
            # Wait for stack operation to complete
            print(f"Waiting for stack {operation.lower()} to complete...")
            waiter_name = f"stack_{operation.lower()}_complete"
            waiter = self.cf_client.get_waiter(waiter_name)
            waiter.wait(StackName=self.stack_name)
            
            # Get stack outputs
            response = self.cf_client.describe_stacks(StackName=self.stack_name)
            outputs = {}
            if 'Outputs' in response['Stacks'][0]:
                for output in response['Stacks'][0]['Outputs']:
                    outputs[output['OutputKey']] = output['OutputValue']
            
            print(f"Infrastructure deployment completed successfully!")
            return outputs
            
        except ClientError as e:
            if 'No updates are to be performed' in str(e):
                print("No infrastructure updates needed.")
                # Get existing outputs
                response = self.cf_client.describe_stacks(StackName=self.stack_name)
                outputs = {}
                if 'Outputs' in response['Stacks'][0]:
                    for output in response['Stacks'][0]['Outputs']:
                        outputs[output['OutputKey']] = output['OutputValue']
                return outputs
            else:
                print(f"CloudFormation error: {e}")
                raise
    
    def build_lambda_package(self) -> str:
        """Build Lambda deployment package"""
        print("Building Lambda deployment package...")
        
        project_root = Path(__file__).parent.parent.parent
        lambda_dir = Path(__file__).parent.parent / "lambda"
        package_path = lambda_dir / "deployment-package.zip"
        
        # Create deployment package
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add Lambda handler
            handler_path = lambda_dir / "lambda_handler.py"
            zipf.write(handler_path, "lambda_handler.py")
            
            # Add application code
            for root, dirs, files in os.walk(project_root):
                # Skip deployment, tests, and other non-essential directories
                dirs[:] = [d for d in dirs if d not in ['deployment', 'tests', '__pycache__', '.git', '.kiro']]
                
                for file in files:
                    if file.endswith(('.py', '.json', '.yaml', '.yml')):
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(project_root)
                        zipf.write(file_path, arcname)
        
        print(f"Lambda package created: {package_path}")
        return str(package_path)
    
    def deploy_lambda(self, outputs: Dict[str, str]) -> None:
        """Deploy Lambda function"""
        print("Deploying Lambda function...")
        
        package_path = self.build_lambda_package()
        function_name = f"{self.project_name}-generator-{self.environment}"
        
        with open(package_path, 'rb') as f:
            zip_content = f.read()
        
        try:
            # Update existing function
            self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"Lambda function {function_name} updated successfully!")
            
        except ClientError as e:
            if 'ResourceNotFoundException' in str(e):
                print(f"Lambda function {function_name} not found. It should be created by CloudFormation.")
            else:
                print(f"Lambda deployment error: {e}")
                raise
    
    def build_docker_image(self) -> str:
        """Build Docker image"""
        print("Building Docker image...")
        
        project_root = Path(__file__).parent.parent.parent
        dockerfile_path = Path(__file__).parent.parent / "docker" / "Dockerfile"
        
        image_tag = f"{self.project_name}:{self.environment}"
        
        cmd = [
            "docker", "build",
            "-f", str(dockerfile_path),
            "-t", image_tag,
            str(project_root)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Docker build failed: {result.stderr}")
            raise RuntimeError("Docker build failed")
        
        print(f"Docker image built successfully: {image_tag}")
        return image_tag
    
    def deploy_docker(self) -> None:
        """Deploy using Docker Compose"""
        print("Deploying with Docker Compose...")
        
        compose_path = Path(__file__).parent.parent / "docker" / "docker-compose.yml"
        project_root = Path(__file__).parent.parent.parent
        
        # Set environment variables
        env_vars = {
            'ENVIRONMENT': self.environment,
            'AWS_REGION': self.region
        }
        
        cmd = [
            "docker-compose",
            "-f", str(compose_path),
            "-p", f"{self.project_name}-{self.environment}",
            "up", "-d", "--build"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env={**os.environ, **env_vars},
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Docker Compose deployment failed: {result.stderr}")
            raise RuntimeError("Docker Compose deployment failed")
        
        print("Docker Compose deployment completed successfully!")
    
    def validate_deployment(self, outputs: Dict[str, str]) -> None:
        """Validate deployment by running basic checks"""
        print("Validating deployment...")
        
        # Check S3 bucket
        if 'S3BucketName' in outputs:
            try:
                self.s3_client.head_bucket(Bucket=outputs['S3BucketName'])
                print(f"✓ S3 bucket accessible: {outputs['S3BucketName']}")
            except ClientError as e:
                print(f"✗ S3 bucket check failed: {e}")
        
        # Check Lambda function
        if 'LambdaFunctionArn' in outputs:
            try:
                function_name = outputs['LambdaFunctionArn'].split(':')[-1]
                self.lambda_client.get_function(FunctionName=function_name)
                print(f"✓ Lambda function accessible: {function_name}")
            except ClientError as e:
                print(f"✗ Lambda function check failed: {e}")
        
        print("Deployment validation completed!")

def main():
    parser = argparse.ArgumentParser(description="Deploy AWS Infographic Generator")
    parser.add_argument(
        '--environment', '-e',
        default='dev',
        choices=['dev', 'staging', 'prod'],
        help='Deployment environment'
    )
    parser.add_argument(
        '--region', '-r',
        default='us-east-1',
        help='AWS region'
    )
    parser.add_argument(
        '--deployment-type', '-t',
        default='all',
        choices=['infrastructure', 'lambda', 'docker', 'all'],
        help='Type of deployment to perform'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run deployment validation'
    )
    
    args = parser.parse_args()
    
    deployer = DeploymentManager(args.environment, args.region)
    
    try:
        outputs = {}
        
        if args.deployment_type in ['infrastructure', 'all']:
            outputs = deployer.deploy_infrastructure()
        
        if args.deployment_type in ['lambda', 'all']:
            if not outputs:
                # Get existing stack outputs
                try:
                    response = deployer.cf_client.describe_stacks(StackName=deployer.stack_name)
                    if 'Outputs' in response['Stacks'][0]:
                        for output in response['Stacks'][0]['Outputs']:
                            outputs[output['OutputKey']] = output['OutputValue']
                except ClientError:
                    print("Warning: Could not retrieve stack outputs for Lambda deployment")
            
            deployer.deploy_lambda(outputs)
        
        if args.deployment_type in ['docker', 'all']:
            deployer.deploy_docker()
        
        if args.validate:
            deployer.validate_deployment(outputs)
        
        print("\n🎉 Deployment completed successfully!")
        
        if outputs:
            print("\nDeployment Outputs:")
            for key, value in outputs.items():
                print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()