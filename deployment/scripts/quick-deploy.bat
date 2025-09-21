@echo off
REM Quick deployment script for AWS Infographic Generator (Windows)
REM Usage: quick-deploy.bat [environment] [deployment-type]

setlocal enabledelayedexpansion

REM Default values
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=dev

set DEPLOYMENT_TYPE=%2
if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=all

set REGION=%AWS_REGION%
if "%REGION%"=="" set REGION=us-east-1

echo 🚀 AWS Infographic Generator Deployment
echo Environment: %ENVIRONMENT%
echo Deployment Type: %DEPLOYMENT_TYPE%
echo Region: %REGION%
echo ----------------------------------------

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check AWS CLI
aws --version >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not found. Please install AWS CLI first.
    exit /b 1
)

REM Check AWS credentials
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS credentials not configured. Please run 'aws configure' first.
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    exit /b 1
)

REM Check Docker (if needed)
if "%DEPLOYMENT_TYPE%"=="docker" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker not found. Please install Docker first.
        exit /b 1
    )
)

if "%DEPLOYMENT_TYPE%"=="all" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Docker not found. Skipping Docker deployment.
    )
)

echo ✅ Prerequisites check passed

REM Install Python dependencies for deployment script
echo 📦 Installing deployment dependencies...
pip install boto3 botocore --quiet

REM Run deployment
echo 🔧 Starting deployment...
cd /d "%~dp0"

python deploy.py --environment %ENVIRONMENT% --region %REGION% --deployment-type %DEPLOYMENT_TYPE% --validate

if errorlevel 1 (
    echo ❌ Deployment failed!
    exit /b 1
)

echo ✅ Deployment completed successfully!

REM Display useful information
echo.
echo 📊 Deployment Information:
echo - Environment: %ENVIRONMENT%
echo - Region: %REGION%
echo - Stack Name: aws-infographic-generator-%ENVIRONMENT%

if "%DEPLOYMENT_TYPE%"=="infrastructure" goto :show_aws_links
if "%DEPLOYMENT_TYPE%"=="all" goto :show_aws_links
goto :show_docker_info

:show_aws_links
echo.
echo 🔗 Useful AWS Console Links:
echo - CloudFormation: https://console.aws.amazon.com/cloudformation/home?region=%REGION%
echo - Lambda Functions: https://console.aws.amazon.com/lambda/home?region=%REGION%
echo - S3 Buckets: https://console.aws.amazon.com/s3/home?region=%REGION%
echo - CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=%REGION%#logsV2:log-groups

:show_docker_info
if "%DEPLOYMENT_TYPE%"=="docker" goto :docker_info
if "%DEPLOYMENT_TYPE%"=="all" goto :docker_info
goto :finish

:docker_info
echo.
echo 🐳 Docker Information:
echo - Container: aws-infographic-generator-%ENVIRONMENT%
echo - Check status: docker ps | findstr infographic
echo - View logs: docker logs aws-infographic-generator

:finish
echo.
echo 🎉 Ready to generate infographics!

endlocal