"""
Pure S3 tools for image storage operations.

These tools provide raw S3 API access without embedded business logic.
All decision-making should happen in AI agent reasoning.
"""

import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from utils.constants import AWS_REGION, S3_BUCKET_NAME

logger = logging.getLogger(__name__)


class ImageS3Tools:
    """
    Pure tools for S3 image storage operations.
    
    Provides raw S3 API access without embedded business logic or decision-making.
    """
    
    def __init__(self, bucket_name: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize S3 tools.
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region for S3 client
        """
        self.bucket_name = bucket_name or S3_BUCKET_NAME
        self.region = region or AWS_REGION
        
        try:
            self.s3_client = boto3.client('s3', region_name=self.region)
        except Exception as e:
            logger.warning(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None
    
    def upload_image(
        self,
        file_path: str,
        s3_key: str,
        content_type: str = "image/png",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload image file to S3.
        Pure upload operation without processing logic.
        
        Args:
            file_path: Local path to image file
            s3_key: S3 key (path) for the uploaded file
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the object
            
        Returns:
            Raw S3 upload results
        """
        try:
            if not self.s3_client:
                return {
                    "success": False,
                    "error": "S3 client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File does not exist: {file_path}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'ContentType': content_type
            }
            
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Upload file
            self.s3_client.upload_file(file_path, **upload_params)
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            return {
                "success": True,
                "s3_url": s3_url,
                "s3_key": s3_key,
                "bucket_name": self.bucket_name,
                "file_path": file_path,
                "content_type": content_type,
                "file_size": os.path.getsize(file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "ClientError",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown'),
                "file_path": file_path,
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "file_path": file_path,
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
    
    def download_image(
        self,
        s3_key: str,
        local_path: str
    ) -> Dict[str, Any]:
        """
        Download image from S3 to local file.
        Pure download operation without processing logic.
        
        Args:
            s3_key: S3 key of the file to download
            local_path: Local path to save the downloaded file
            
        Returns:
            Raw S3 download results
        """
        try:
            if not self.s3_client:
                return {
                    "success": False,
                    "error": "S3 client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Download file
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            
            return {
                "success": True,
                "s3_key": s3_key,
                "local_path": local_path,
                "bucket_name": self.bucket_name,
                "file_size": os.path.getsize(local_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"S3 download error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "ClientError",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown'),
                "s3_key": s3_key,
                "local_path": local_path,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"S3 download failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "s3_key": s3_key,
                "local_path": local_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def check_object_exists(
        self,
        s3_key: str
    ) -> Dict[str, Any]:
        """
        Check if S3 object exists.
        Pure existence check without processing logic.
        
        Args:
            s3_key: S3 key to check
            
        Returns:
            Object existence results
        """
        try:
            if not self.s3_client:
                return {
                    "success": False,
                    "error": "S3 client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if object exists
            try:
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                
                return {
                    "success": True,
                    "exists": True,
                    "s3_key": s3_key,
                    "bucket_name": self.bucket_name,
                    "content_length": response.get('ContentLength', 0),
                    "content_type": response.get('ContentType', ''),
                    "last_modified": response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
                    "timestamp": datetime.now().isoformat()
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return {
                        "success": True,
                        "exists": False,
                        "s3_key": s3_key,
                        "bucket_name": self.bucket_name,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise e
            
        except ClientError as e:
            logger.error(f"S3 head object error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "ClientError",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown'),
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"S3 existence check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
    
    def delete_image(
        self,
        s3_key: str
    ) -> Dict[str, Any]:
        """
        Delete image from S3.
        Pure deletion operation without processing logic.
        
        Args:
            s3_key: S3 key of the file to delete
            
        Returns:
            Raw S3 deletion results
        """
        try:
            if not self.s3_client:
                return {
                    "success": False,
                    "error": "S3 client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Delete object
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            return {
                "success": True,
                "s3_key": s3_key,
                "bucket_name": self.bucket_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"S3 delete error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "ClientError",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown'),
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"S3 delete failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Generate presigned URL for S3 object.
        Pure URL generation without processing logic.
        
        Args:
            s3_key: S3 key of the object
            expiration: URL expiration time in seconds
            http_method: HTTP method for the URL
            
        Returns:
            Presigned URL results
        """
        try:
            if not self.s3_client:
                return {
                    "success": False,
                    "error": "S3 client not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                http_method.lower() + '_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            return {
                "success": True,
                "presigned_url": presigned_url,
                "s3_key": s3_key,
                "bucket_name": self.bucket_name,
                "expiration_seconds": expiration,
                "http_method": http_method,
                "timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"S3 presigned URL error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "ClientError",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown'),
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"S3 presigned URL generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "s3_key": s3_key,
                "timestamp": datetime.now().isoformat()
            }


# Convenience functions for direct usage
def upload_image_to_s3(file_path: str, s3_key: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for S3 image upload.
    
    Args:
        file_path: Local file path
        s3_key: S3 key for upload
        **kwargs: Additional upload parameters
        
    Returns:
        Upload results
    """
    tools = ImageS3Tools()
    return tools.upload_image(file_path, s3_key, **kwargs)


def download_image_from_s3(s3_key: str, local_path: str) -> Dict[str, Any]:
    """
    Convenience function for S3 image download.
    
    Args:
        s3_key: S3 key to download
        local_path: Local path to save file
        
    Returns:
        Download results
    """
    tools = ImageS3Tools()
    return tools.download_image(s3_key, local_path)