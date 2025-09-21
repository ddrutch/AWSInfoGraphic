#!/usr/bin/env python3
"""
AWS CDK application for AWS Infographic Generator
Provides Infrastructure as Code using AWS CDK instead of CloudFormation
"""
import os
from aws_cdk import (
    App,
    Environment,
    Stack,
    StackProps,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)
from constructs import Construct

class InfographicGeneratorStack(Stack):
    """CDK Stack for AWS Infographic Generator"""
    
    def __init__(self, scope: Construct, construct_id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.environment = environment
        self.project_name = "aws-infographic-generator"
        
        # Create S3 bucket for assets
        self.create_s3_bucket()
        
        # Create IAM roles and policies
        self.create_iam_roles()
        
        # Create Lambda function
        self.create_lambda_function()
        
        # Create CloudWatch resources
        self.create_monitoring()
        
        # Create SNS topic for notifications
        self.create_notifications()
    
    def create_s3_bucket(self):
        """Create S3 bucket for storing infographic assets"""
        self.assets_bucket = s3.Bucket(
            self, "AssetsBucket",
            bucket_name=f"{self.project_name}-assets-{self.environment}-{self.account}",
            versioned=True,
            public_read_access=True,
            cors=[
                s3.CorsRule(
                    allowed_headers=["*"],
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
                        s3.HttpMethods.DELETE,
                        s3.HttpMethods.HEAD
                    ],
                    allowed_origins=["*"],
                    max_age=3000
                )
            ],
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    enabled=True,
                    noncurrent_version_expiration=Duration.days(30)
                ),
                s3.LifecycleRule(
                    id="DeleteIncompleteMultipartUploads",
                    enabled=True,
                    abort_incomplete_multipart_upload_after=Duration.days(7)
                )
            ],
            removal_policy=RemovalPolicy.DESTROY if self.environment == "dev" else RemovalPolicy.RETAIN
        )
    
    def create_iam_roles(self):
        """Create IAM roles and policies"""
        
        # Lambda execution role
        self.lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            role_name=f"{self.project_name}-lambda-execution-role-{self.environment}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Bedrock access policy
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            resources=["*"]
        )
        
        # S3 access policy
        s3_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            resources=[
                self.assets_bucket.bucket_arn,
                f"{self.assets_bucket.bucket_arn}/*"
            ]
        )
        
        # CloudWatch metrics policy
        cloudwatch_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "cloudwatch:PutMetricData",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            resources=["*"]
        )
        
        # Add policies to Lambda role
        self.lambda_role.add_to_policy(bedrock_policy)
        self.lambda_role.add_to_policy(s3_policy)
        self.lambda_role.add_to_policy(cloudwatch_policy)
        
        # ECS task role
        self.ecs_task_role = iam.Role(
            self, "ECSTaskRole",
            role_name=f"{self.project_name}-ecs-task-role-{self.environment}",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        self.ecs_task_role.add_to_policy(bedrock_policy)
        self.ecs_task_role.add_to_policy(s3_policy)
        
        # ECS execution role
        self.ecs_execution_role = iam.Role(
            self, "ECSExecutionRole",
            role_name=f"{self.project_name}-ecs-execution-role-{self.environment}",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )
    
    def create_lambda_function(self):
        """Create Lambda function for serverless execution"""
        
        # Create log group
        self.lambda_log_group = logs.LogGroup(
            self, "LambdaLogGroup",
            log_group_name=f"/aws/lambda/{self.project_name}-generator-{self.environment}",
            retention=logs.RetentionDays.TWO_WEEKS,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create Lambda function
        self.lambda_function = lambda_.Function(
            self, "InfographicGeneratorFunction",
            function_name=f"{self.project_name}-generator-{self.environment}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=self.lambda_role,
            timeout=Duration.minutes(15),
            memory_size=3008,  # Maximum memory for image processing
            environment={
                "S3_BUCKET": self.assets_bucket.bucket_name,
                "ENVIRONMENT": self.environment,
                "LOG_LEVEL": "INFO" if self.environment == "prod" else "DEBUG"
            },
            log_group=self.lambda_log_group
        )
        
        # Health check function
        self.health_check_function = lambda_.Function(
            self, "HealthCheckFunction",
            function_name=f"{self.project_name}-health-check-{self.environment}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_handler.health_check_handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=self.lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={
                "S3_BUCKET": self.assets_bucket.bucket_name,
                "ENVIRONMENT": self.environment
            }
        )
    
    def create_monitoring(self):
        """Create CloudWatch monitoring resources"""
        
        # Application log group
        self.app_log_group = logs.LogGroup(
            self, "ApplicationLogGroup",
            log_group_name=f"/aws/infographic-generator/{self.environment}",
            retention=logs.RetentionDays.TWO_WEEKS,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Custom metrics
        self.success_metric = cloudwatch.Metric(
            namespace="InfographicGenerator",
            metric_name="SuccessfulGenerations",
            statistic="Sum"
        )
        
        self.error_metric = cloudwatch.Metric(
            namespace="InfographicGenerator",
            metric_name="GenerationErrors",
            statistic="Sum"
        )
        
        self.critical_error_metric = cloudwatch.Metric(
            namespace="InfographicGenerator",
            metric_name="CriticalErrors",
            statistic="Sum"
        )
        
        # CloudWatch Dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "InfographicGeneratorDashboard",
            dashboard_name=f"InfographicGenerator-{self.environment}"
        )
        
        # Add widgets to dashboard
        self.dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Infographic Generation Metrics",
                left=[self.success_metric, self.error_metric, self.critical_error_metric],
                width=12,
                height=6
            ),
            cloudwatch.GraphWidget(
                title="Lambda Function Metrics",
                left=[
                    self.lambda_function.metric_duration(),
                    self.lambda_function.metric_invocations(),
                    self.lambda_function.metric_errors(),
                    self.lambda_function.metric_throttles()
                ],
                width=12,
                height=6
            )
        )
    
    def create_notifications(self):
        """Create SNS topic for notifications"""
        
        self.alarm_topic = sns.Topic(
            self, "AlarmTopic",
            topic_name=f"{self.project_name}-alarms-{self.environment}",
            display_name=f"{self.project_name} Alarms ({self.environment})"
        )
        
        # Add email subscription if email is provided
        notification_email = os.environ.get("NOTIFICATION_EMAIL")
        if notification_email:
            self.alarm_topic.add_subscription(
                subscriptions.EmailSubscription(notification_email)
            )
        
        # Create alarms
        self.create_alarms()
    
    def create_alarms(self):
        """Create CloudWatch alarms"""
        
        # Lambda error rate alarm
        lambda_error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorRateAlarm",
            alarm_name=f"{self.project_name}-lambda-error-rate-{self.environment}",
            alarm_description="High error rate in Lambda function",
            metric=self.lambda_function.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        lambda_error_alarm.add_alarm_action(
            cloudwatch.SnsAction(self.alarm_topic)
        )
        
        # Lambda duration alarm
        lambda_duration_alarm = cloudwatch.Alarm(
            self, "LambdaDurationAlarm",
            alarm_name=f"{self.project_name}-lambda-duration-{self.environment}",
            alarm_description="Lambda function taking too long to execute",
            metric=self.lambda_function.metric_duration(),
            threshold=600000,  # 10 minutes in milliseconds
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )
        lambda_duration_alarm.add_alarm_action(
            cloudwatch.SnsAction(self.alarm_topic)
        )
        
        # Critical errors alarm
        critical_error_alarm = cloudwatch.Alarm(
            self, "CriticalErrorAlarm",
            alarm_name=f"{self.project_name}-critical-errors-{self.environment}",
            alarm_description="Critical errors in infographic generation system",
            metric=self.critical_error_metric,
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD
        )
        critical_error_alarm.add_alarm_action(
            cloudwatch.SnsAction(self.alarm_topic)
        )

def main():
    """Main CDK application"""
    app = App()
    
    # Get environment from context or environment variable
    environment = app.node.try_get_context("environment") or os.environ.get("ENVIRONMENT", "dev")
    region = app.node.try_get_context("region") or os.environ.get("AWS_REGION", "us-east-1")
    account = app.node.try_get_context("account") or os.environ.get("CDK_DEFAULT_ACCOUNT")
    
    # Create stack
    InfographicGeneratorStack(
        app, 
        f"InfographicGeneratorStack-{environment}",
        environment=environment,
        env=Environment(account=account, region=region),
        description=f"AWS Infographic Generator Stack for {environment} environment"
    )
    
    app.synth()

if __name__ == "__main__":
    main()