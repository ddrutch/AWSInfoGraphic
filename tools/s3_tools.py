"""
S3 integration tools for AWS infographic generator.

This module provides utilities for uploading, downloading, and managing
infographic assets in Amazon S3, including secure URL generation and
comprehensive error handling.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from botocore.config import Config
import time

from utils.error_handling import (
    ErrorHandler, with_error_handling, ErrorCategory, ErrorSeverity,
    AWSServiceError, NetworkError, TimeoutError, ValidationError,
    handle_aws_service_error, log_error_context
)

logger = logging.getLogger(__name__)


class S3ToolsError(Exception):
    """Base exception for S3 tools operations."""
    pass


class S3UploadError(S3ToolsError):
    """Exception raised when S3 upload operations fail."""
    pass


class S3DownloadError(S3ToolsError):
    """Exception raised when S3 download operations fail."""
    pass


class S3ConfigurationError(S3ToolsError):
    """Exception raised when S3 configuration is invalid."""
    pass


class S3Tools:
    """
    S3 integration utilities for infographic asset management.
    
    Provides methods for uploading, downloading, and managing infographic
    assets in Amazon S3 with proper error handling and retry logic.
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize S3Tools with configuration.
        
        Args:
            bucket_name: S3 bucket name (defaults to env var S3_BUCKET_NAME)
            region: AWS region (defaults to env var S3_REGION or AWS_REGION)
            aws_access_key_id: AWS access key (defaults to env var)
            aws_secret_access_key: AWS secret key (defaults to env var)
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME")
        self.region = region or os.getenv("S3_REGION") or os.getenv("AWS_REGION", "us-east-1")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if not self.bucket_name:
            raise S3ConfigurationError("S3 bucket name must be provided via parameter or S3_BUCKET_NAME environment variable")
        
        # Configure boto3 client with retry settings
        config = Config(
            region_name=self.region,
            retries={
                'max_attempts': max_retries,
                'mode': 'adaptive'
            }
        )
        
        try:
            # Initialize S3 client with optional credentials
            session_kwargs = {}
            if aws_access_key_id and aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': aws_access_key_id,
                    'aws_secret_access_key': aws_secret_access_key
                })
            
            session = boto3.Session(**session_kwargs)
            self.s3_client = session.client('s3', config=config)
            
            # Verify bucket access
            self._verify_bucket_access()
            
        except NoCredentialsError:
            raise S3ConfigurationError("AWS credentials not found. Please configure AWS credentials.")
        except Exception as e:
            raise S3ConfigurationError(f"Failed to initialize S3 client: {str(e)}")
    
    def _verify_bucket_access(self) -> None:
        """Verify that the bucket exists and is accessible."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Successfully verified access to S3 bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise S3ConfigurationError(f"S3 bucket '{self.bucket_name}' does not exist")
            elif error_code == '403':
                raise S3ConfigurationError(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                raise S3ConfigurationError(f"Failed to access S3 bucket '{self.bucket_name}': {str(e)}")
    
    def _retry_operation(self, operation, *args, **kwargs):
        """Execute operation with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except (ClientError, BotoCoreError) as e:
                last_exception = e
                
                # Convert to standardized error format
                standardized_error = handle_aws_service_error("S3", e)
                
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"S3 operation failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {delay}s: {str(e)}")
                    
                    # Log error context for monitoring
                    log_error_context(standardized_error, {
                        "operation": operation.__name__ if hasattr(operation, '__name__') else str(operation),
                        "attempt": attempt + 1,
                        "retry_delay": delay,
                        "bucket": self.bucket_name
                    })
                    
                    time.sleep(delay)
                else:
                    logger.error(f"S3 operation failed after {self.max_retries + 1} attempts: {str(e)}")
                    log_error_context(standardized_error, {
                        "operation": operation.__name__ if hasattr(operation, '__name__') else str(operation),
                        "total_attempts": self.max_retries + 1,
                        "bucket": self.bucket_name,
                        "final_failure": True
                    })
        
        raise handle_aws_service_error("S3", last_exception)
    
    @with_error_handling(circuit_breaker_name="s3_upload", fallback_category=ErrorCategory.AWS_SERVICE)
    def upload_file(
        self,
        file_path: str,
        s3_key: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        public_read: bool = False
    ) -> str:
        """
        Upload a file to S3.
        
        Args:
            file_path: Local path to the file to upload
            s3_key: S3 object key (defaults to filename)
            content_type: MIME type of the file (auto-detected if not provided)
            metadata: Additional metadata to store with the object
            public_read: Whether to make the object publicly readable
            
        Returns:
            S3 object key of the uploaded file
            
        Raises:
            S3UploadError: If upload fails
        """
        if not os.path.exists(file_path):
            raise S3UploadError(f"File not found: {file_path}")
        
        if not s3_key:
            s3_key = os.path.basename(file_path)
        
        # Auto-detect content type if not provided
        if not content_type:
            content_type = self._get_content_type(file_path)
        
        # Prepare upload arguments
        upload_args = {
            'ContentType': content_type
        }
        
        if metadata:
            upload_args['Metadata'] = metadata
        
        if public_read:
            upload_args['ACL'] = 'public-read'
        
        try:
            logger.info(f"Uploading {file_path} to s3://{self.bucket_name}/{s3_key}")
            
            def _upload():
                return self.s3_client.upload_file(
                    file_path,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs=upload_args
                )
            
            self._retry_operation(_upload)
            logger.info(f"Successfully uploaded {file_path} to S3")
            return s3_key
            
        except Exception as e:
            error = handle_aws_service_error("S3", e)
            log_error_context(error, {
                "operation": "upload_file",
                "file_path": file_path,
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else None
            })
            raise S3UploadError(f"Failed to upload {file_path} to S3: {str(e)}")
    
    def upload_bytes(
        self,
        data: bytes,
        s3_key: str,
        content_type: str = 'application/octet-stream',
        metadata: Optional[Dict[str, str]] = None,
        public_read: bool = False
    ) -> str:
        """
        Upload bytes data directly to S3.
        
        Args:
            data: Bytes data to upload
            s3_key: S3 object key
            content_type: MIME type of the data
            metadata: Additional metadata to store with the object
            public_read: Whether to make the object publicly readable
            
        Returns:
            S3 object key of the uploaded data
            
        Raises:
            S3UploadError: If upload fails
        """
        # Prepare upload arguments
        upload_args = {
            'ContentType': content_type
        }
        
        if metadata:
            upload_args['Metadata'] = metadata
        
        if public_read:
            upload_args['ACL'] = 'public-read'
        
        try:
            logger.info(f"Uploading {len(data)} bytes to s3://{self.bucket_name}/{s3_key}")
            
            def _upload():
                return self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=data,
                    **upload_args
                )
            
            self._retry_operation(_upload)
            logger.info(f"Successfully uploaded bytes data to S3")
            return s3_key
            
        except Exception as e:
            raise S3UploadError(f"Failed to upload bytes data to S3: {str(e)}")
    
    def download_file(
        self,
        s3_key: str,
        local_path: str
    ) -> str:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key to download
            local_path: Local path where to save the file
            
        Returns:
            Local path of the downloaded file
            
        Raises:
            S3DownloadError: If download fails
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            logger.info(f"Downloading s3://{self.bucket_name}/{s3_key} to {local_path}")
            
            def _download():
                return self.s3_client.download_file(
                    self.bucket_name,
                    s3_key,
                    local_path
                )
            
            self._retry_operation(_download)
            logger.info(f"Successfully downloaded {s3_key} from S3")
            return local_path
            
        except Exception as e:
            raise S3DownloadError(f"Failed to download {s3_key} from S3: {str(e)}")
    
    def download_bytes(self, s3_key: str) -> bytes:
        """
        Download file content as bytes from S3.
        
        Args:
            s3_key: S3 object key to download
            
        Returns:
            File content as bytes
            
        Raises:
            S3DownloadError: If download fails
        """
        try:
            logger.info(f"Downloading s3://{self.bucket_name}/{s3_key} as bytes")
            
            def _download():
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
                return response['Body'].read()
            
            data = self._retry_operation(_download)
            logger.info(f"Successfully downloaded {s3_key} as bytes")
            return data
            
        except Exception as e:
            raise S3DownloadError(f"Failed to download {s3_key} as bytes from S3: {str(e)}")
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> str:
        """
        Generate a presigned URL for secure access to S3 objects.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method for the URL (GET, PUT, etc.)
            
        Returns:
            Presigned URL string
            
        Raises:
            S3ToolsError: If URL generation fails
        """
        try:
            logger.info(f"Generating presigned URL for s3://{self.bucket_name}/{s3_key}")
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
            
            logger.info(f"Generated presigned URL (expires in {expiration}s)")
            return url
            
        except Exception as e:
            raise S3ToolsError(f"Failed to generate presigned URL for {s3_key}: {str(e)}")
    
    def generate_upload_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a presigned URL for uploading files to S3.
        
        Args:
            s3_key: S3 object key for the upload
            expiration: URL expiration time in seconds (default: 1 hour)
            content_type: Expected content type for the upload
            
        Returns:
            Dictionary containing presigned POST data
            
        Raises:
            S3ToolsError: If URL generation fails
        """
        try:
            logger.info(f"Generating presigned upload URL for s3://{self.bucket_name}/{s3_key}")
            
            conditions = []
            if content_type:
                conditions.append({"Content-Type": content_type})
            
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=s3_key,
                ExpiresIn=expiration,
                Conditions=conditions
            )
            
            logger.info(f"Generated presigned upload URL (expires in {expiration}s)")
            return response
            
        except Exception as e:
            raise S3ToolsError(f"Failed to generate presigned upload URL for {s3_key}: {str(e)}")
    
    def delete_object(self, s3_key: str) -> bool:
        """
        Delete an object from S3.
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            S3ToolsError: If deletion fails
        """
        try:
            logger.info(f"Deleting s3://{self.bucket_name}/{s3_key}")
            
            def _delete():
                return self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
            
            self._retry_operation(_delete)
            logger.info(f"Successfully deleted {s3_key} from S3")
            return True
            
        except Exception as e:
            raise S3ToolsError(f"Failed to delete {s3_key} from S3: {str(e)}")
    
    def object_exists(self, s3_key: str) -> bool:
        """
        Check if an object exists in S3.
        
        Args:
            s3_key: S3 object key to check
            
        Returns:
            True if object exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise S3ToolsError(f"Failed to check if {s3_key} exists: {str(e)}")
    
    def get_object_metadata(self, s3_key: str) -> Dict[str, Any]:
        """
        Get metadata for an S3 object.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Dictionary containing object metadata
            
        Raises:
            S3ToolsError: If metadata retrieval fails
        """
        try:
            logger.info(f"Getting metadata for s3://{self.bucket_name}/{s3_key}")
            
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            metadata = {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag'),
                'metadata': response.get('Metadata', {})
            }
            
            return metadata
            
        except Exception as e:
            raise S3ToolsError(f"Failed to get metadata for {s3_key}: {str(e)}")
    
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        List objects in the S3 bucket with optional prefix filter.
        
        Args:
            prefix: Object key prefix to filter by
            max_keys: Maximum number of objects to return
            
        Returns:
            List of object information dictionaries
            
        Raises:
            S3ToolsError: If listing fails
        """
        try:
            logger.info(f"Listing objects in s3://{self.bucket_name} with prefix '{prefix}'")
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })
            
            logger.info(f"Found {len(objects)} objects")
            return objects
            
        except Exception as e:
            raise S3ToolsError(f"Failed to list objects: {str(e)}")
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Determine content type based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME content type string
        """
        import mimetypes
        
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type:
            return content_type
        
        # Fallback for common image types
        ext = os.path.splitext(file_path)[1].lower()
        content_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.json': 'application/json',
            '.txt': 'text/plain'
        }
        
        return content_type_map.get(ext, 'application/octet-stream')


# Convenience functions for common operations
def upload_infographic(
    file_path: str,
    bucket_name: Optional[str] = None,
    s3_key: Optional[str] = None,
    public_read: bool = True
) -> tuple[str, str]:
    """
    Convenience function to upload an infographic and get a shareable URL.
    
    Args:
        file_path: Local path to the infographic file
        bucket_name: S3 bucket name (optional, uses env var if not provided)
        s3_key: S3 object key (optional, uses filename if not provided)
        public_read: Whether to make the object publicly readable
        
    Returns:
        Tuple of (s3_key, public_url or presigned_url)
    """
    s3_tools = S3Tools(bucket_name=bucket_name)
    
    # Generate timestamped key if not provided
    if not s3_key:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        s3_key = f"infographics/{timestamp}_{name}{ext}"
    
    # Upload the file
    uploaded_key = s3_tools.upload_file(
        file_path=file_path,
        s3_key=s3_key,
        public_read=public_read
    )
    
    # Generate URL
    if public_read:
        url = f"https://{s3_tools.bucket_name}.s3.{s3_tools.region}.amazonaws.com/{uploaded_key}"
    else:
        url = s3_tools.generate_presigned_url(uploaded_key, expiration=86400)  # 24 hours
    
    return uploaded_key, url


def create_s3_tools() -> S3Tools:
    """
    Factory function to create S3Tools instance with environment configuration.
    
    Returns:
        Configured S3Tools instance
    """
    return S3Tools()