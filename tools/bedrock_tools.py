"""
Amazon Bedrock integration tools for AWS infographic generator.

This module provides utilities for invoking Bedrock models for text analysis,
content processing, and other LLM-based operations with comprehensive
error handling and retry logic.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from botocore.config import Config

from utils.error_handling import (
    ErrorHandler, with_error_handling, ErrorCategory, ErrorSeverity,
    AWSServiceError, NetworkError, TimeoutError, ValidationError,
    handle_aws_service_error, log_error_context
)

logger = logging.getLogger(__name__)


class BedrockToolsError(Exception):
    """Base exception for Bedrock tools operations."""
    pass


class BedrockInvocationError(BedrockToolsError):
    """Exception raised when Bedrock model invocation fails."""
    pass


class BedrockConfigurationError(BedrockToolsError):
    """Exception raised when Bedrock configuration is invalid."""
    pass


class BedrockModelNotFoundError(BedrockToolsError):
    """Exception raised when specified Bedrock model is not available."""
    pass


class BedrockTools:
    """
    Amazon Bedrock integration utilities for LLM operations.
    
    Provides methods for invoking Bedrock models with proper error handling,
    retry logic, and support for various model types including Claude, Titan, etc.
    """
    
    # Supported model configurations
    SUPPORTED_MODELS = {
        "anthropic.claude-3-5-sonnet-20241022-v2:0": {
            "provider": "anthropic",
            "max_tokens": 200000,
            "supports_system": True,
            "input_format": "anthropic"
        },
        "anthropic.claude-3-haiku-20240307-v1:0": {
            "provider": "anthropic", 
            "max_tokens": 200000,
            "supports_system": True,
            "input_format": "anthropic"
        },
        "amazon.titan-text-premier-v1:0": {
            "provider": "amazon",
            "max_tokens": 32000,
            "supports_system": False,
            "input_format": "titan"
        },
        "amazon.nova-canvas-v1:0": {
            "provider": "amazon",
            "max_tokens": None,
            "supports_system": False,
            "input_format": "nova_canvas"
        }
    }
    
    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        request_timeout: int = 30
    ):
        """
        Initialize BedrockTools with configuration.
        
        Args:
            model_id: Bedrock model ID (defaults to env var BEDROCK_MODEL_ID)
            region: AWS region (defaults to env var BEDROCK_REGION or AWS_REGION)
            aws_access_key_id: AWS access key (defaults to env var)
            aws_secret_access_key: AWS secret key (defaults to env var)
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
            request_timeout: Request timeout in seconds
        """
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.region = region or os.getenv("BEDROCK_REGION") or os.getenv("AWS_REGION", "us-east-1")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_timeout = request_timeout
        
        # Validate model support
        if self.model_id not in self.SUPPORTED_MODELS:
            logger.warning(f"Model {self.model_id} not in supported models list. Proceeding with default configuration.")
        
        self.model_config = self.SUPPORTED_MODELS.get(self.model_id, {
            "provider": "unknown",
            "max_tokens": 100000,
            "supports_system": True,
            "input_format": "anthropic"
        })
        
        # Configure boto3 client with retry settings
        config = Config(
            region_name=self.region,
            retries={
                'max_attempts': max_retries,
                'mode': 'adaptive'
            },
            read_timeout=request_timeout,
            connect_timeout=10
        )
        
        try:
            # Initialize Bedrock client with optional credentials
            session_kwargs = {}
            if aws_access_key_id and aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': aws_access_key_id,
                    'aws_secret_access_key': aws_secret_access_key
                })
            
            session = boto3.Session(**session_kwargs)
            self.bedrock_client = session.client('bedrock-runtime', config=config)
            
            # Verify model access
            self._verify_model_access()
            
        except NoCredentialsError:
            raise BedrockConfigurationError("AWS credentials not found. Please configure AWS credentials.")
        except Exception as e:
            raise BedrockConfigurationError(f"Failed to initialize Bedrock client: {str(e)}")
    
    def _verify_model_access(self) -> None:
        """Verify that the model is accessible."""
        try:
            # Try a simple invocation to verify access
            test_payload = self._format_request("Test", max_tokens=10)
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(test_payload),
                contentType='application/json'
            )
            
            logger.info(f"Successfully verified access to Bedrock model: {self.model_id}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ValidationException':
                raise BedrockModelNotFoundError(f"Bedrock model '{self.model_id}' not found or not accessible")
            elif error_code == 'AccessDeniedException':
                raise BedrockConfigurationError(f"Access denied to Bedrock model '{self.model_id}'")
            else:
                logger.warning(f"Could not verify model access: {str(e)}")
        except Exception as e:
            logger.warning(f"Could not verify model access: {str(e)}")
    
    def _retry_operation(self, operation, *args, **kwargs):
        """Execute operation with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except (ClientError, BotoCoreError) as e:
                last_exception = e
                
                # Convert to standardized error format
                standardized_error = handle_aws_service_error("Bedrock", e)
                
                # Check if error is retryable
                if isinstance(e, ClientError):
                    error_code = e.response['Error']['Code']
                    if error_code in ['ValidationException', 'AccessDeniedException']:
                        # Don't retry these errors
                        log_error_context(standardized_error, {
                            "operation": operation.__name__ if hasattr(operation, '__name__') else str(operation),
                            "attempt": attempt + 1,
                            "retryable": False
                        })
                        raise standardized_error
                
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Bedrock operation failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {delay}s: {str(e)}")
                    
                    # Log error context for monitoring
                    log_error_context(standardized_error, {
                        "operation": operation.__name__ if hasattr(operation, '__name__') else str(operation),
                        "attempt": attempt + 1,
                        "retry_delay": delay,
                        "retryable": True
                    })
                    
                    time.sleep(delay)
                else:
                    logger.error(f"Bedrock operation failed after {self.max_retries + 1} attempts: {str(e)}")
                    log_error_context(standardized_error, {
                        "operation": operation.__name__ if hasattr(operation, '__name__') else str(operation),
                        "total_attempts": self.max_retries + 1,
                        "final_failure": True
                    })
        
        raise handle_aws_service_error("Bedrock", last_exception)
    
    def _format_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Format request payload based on model provider.
        
        Args:
            prompt: User prompt text
            system_prompt: System prompt (if supported by model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional model-specific parameters
            
        Returns:
            Formatted request payload
        """
        provider = self.model_config["provider"]
        input_format = self.model_config["input_format"]
        
        if input_format == "anthropic":
            # Anthropic Claude format
            messages = [{"role": "user", "content": prompt}]
            
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": min(max_tokens, self.model_config.get("max_tokens", 200000)),
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if system_prompt and self.model_config.get("supports_system", False):
                payload["system"] = system_prompt
                
        elif input_format == "titan":
            # Amazon Titan format
            payload = {
                "inputText": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                "textGenerationConfig": {
                    "maxTokenCount": min(max_tokens, self.model_config.get("max_tokens", 32000)),
                    "temperature": temperature,
                    "topP": top_p
                }
            }
            
        elif input_format == "nova_canvas":
            # Amazon Nova Canvas format (for image generation)
            payload = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    "negativeText": kwargs.get("negative_prompt", ""),
                },
                "imageGenerationConfig": {
                    "numberOfImages": kwargs.get("number_of_images", 1),
                    "height": kwargs.get("height", 1024),
                    "width": kwargs.get("width", 1024),
                    "cfgScale": kwargs.get("cfg_scale", 8.0),
                    "seed": kwargs.get("seed", 0)
                }
            }
            
        else:
            # Default/unknown format - use Anthropic-style
            messages = [{"role": "user", "content": prompt}]
            payload = {
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if system_prompt:
                payload["system"] = system_prompt
        
        return payload
    
    def _parse_response(self, response_body: Dict[str, Any]) -> str:
        """
        Parse response based on model provider.
        
        Args:
            response_body: Raw response from Bedrock
            
        Returns:
            Extracted text content
        """
        provider = self.model_config["provider"]
        input_format = self.model_config["input_format"]
        
        if input_format == "anthropic":
            # Anthropic Claude response format
            if "content" in response_body and response_body["content"]:
                return response_body["content"][0]["text"]
            
        elif input_format == "titan":
            # Amazon Titan response format
            if "results" in response_body and response_body["results"]:
                return response_body["results"][0]["outputText"]
                
        elif input_format == "nova_canvas":
            # Nova Canvas returns image data, not text
            if "images" in response_body:
                return response_body["images"]
        
        # Fallback - try common response fields
        for field in ["content", "text", "output", "response"]:
            if field in response_body:
                content = response_body[field]
                if isinstance(content, list) and content:
                    return content[0].get("text", str(content[0]))
                elif isinstance(content, str):
                    return content
        
        # Last resort - return the whole response as string
        return str(response_body)
    
    @with_error_handling(circuit_breaker_name="bedrock_invoke", fallback_category=ErrorCategory.AWS_SERVICE)
    def invoke_model(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        Invoke a Bedrock model with the given prompt.
        
        Args:
            prompt: User prompt text
            system_prompt: System prompt (if supported by model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text response
            
        Raises:
            BedrockInvocationError: If model invocation fails
        """
        try:
            logger.info(f"Invoking Bedrock model {self.model_id}")
            
            # Format request payload
            payload = self._format_request(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            
            def _invoke():
                return self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(payload),
                    contentType='application/json'
                )
            
            # Execute with retry logic
            response = self._retry_operation(_invoke)

            # Robustly extract bytes/text from response['body'] which may be
            # a StreamingBody, bytes, str, or file-like object depending on SDK
            raw_body = response.get('body') if isinstance(response, dict) else None

            raw_bytes = b''
            try:
                if hasattr(raw_body, 'read'):
                    # botocore.streaming.StreamingBody
                    raw_bytes = raw_body.read()
                elif isinstance(raw_body, (bytes, bytearray)):
                    raw_bytes = bytes(raw_body)
                elif isinstance(raw_body, str):
                    raw_bytes = raw_body.encode('utf-8')
                else:
                    # Some clients return the full dict or string in response
                    # Try to stringify the body
                    raw_bytes = json.dumps(raw_body or {}).encode('utf-8')
            except Exception:
                # As a last resort, try to convert the whole response to str
                try:
                    raw_bytes = str(response).encode('utf-8')
                except Exception:
                    raw_bytes = b''

            # Try to decode bytes as text
            text = None
            try:
                text = raw_bytes.decode('utf-8') if raw_bytes else None
            except Exception:
                text = None

            # If provider returns binary image data (nova_canvas), return bytes
            if text is None or text == '':
                # No text available; return raw bytes
                logger.info("Bedrock returned binary data (non-text). Returning raw bytes")
                return raw_bytes

            # Try parse JSON text into python object
            try:
                response_body = json.loads(text)
                result = self._parse_response(response_body)
            except json.JSONDecodeError:
                # Not JSON; treat as plain text
                result = text

            logger.info(f"Successfully invoked model {self.model_id}")
            return result
            
        except Exception as e:
            error = handle_aws_service_error("Bedrock", e)
            log_error_context(error, {
                "model_id": self.model_id,
                "prompt_length": len(prompt),
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            raise BedrockInvocationError(f"Failed to invoke Bedrock model: {str(e)}")
    
    def analyze_content(
        self,
        text: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze content using Bedrock for infographic generation.
        
        Args:
            text: Text content to analyze
            analysis_type: Type of analysis ("general", "key_points", "structure", "summary")
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            BedrockInvocationError: If content analysis fails
        """
        analysis_prompts = {
            "general": """Analyze the following text for creating an infographic. Extract:
1. Main topic/title
2. Key points (3-5 most important)
3. Supporting details
4. Suggested visual elements
5. Target audience

Text: {text}

Respond in JSON format with keys: main_topic, key_points, supporting_details, visual_suggestions, target_audience""",
            
            "key_points": """Extract the 3-5 most important key points from this text for an infographic:

{text}

Return only a JSON array of key points, each as a short, impactful statement.""",
            
            "structure": """Analyze the structure and hierarchy of this content for infographic layout:

{text}

Return JSON with: title, sections (each with heading and points), flow_direction (top-to-bottom, left-to-right, circular)""",
            
            "summary": """Create a concise summary of this text suitable for an infographic title and subtitle:

{text}

Return JSON with: title (max 8 words), subtitle (max 15 words), one_sentence_summary"""
        }
        
        if analysis_type not in analysis_prompts:
            raise BedrockInvocationError(f"Unknown analysis type: {analysis_type}")
        
        prompt = analysis_prompts[analysis_type].format(text=text)
        
        system_prompt = """You are an expert content analyst specializing in creating infographics. 
Always respond with valid JSON format. Be concise and focus on visual communication."""
        
        try:
            response = self.invoke_model(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000
            )
            
            # Try to parse as JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured response
                return {
                    "analysis_type": analysis_type,
                    "raw_response": response,
                    "error": "Failed to parse JSON response"
                }
                
        except Exception as e:
            raise BedrockInvocationError(f"Content analysis failed: {str(e)}")

    async def invoke_model_async(self, *args, **kwargs) -> str:
        """Async wrapper around invoke_model using threadpool to avoid blocking.

        This is useful for calling Bedrock from async code (e.g., Strands tools).
        """
        return await asyncio.to_thread(self.invoke_model, *args, **kwargs)
    
    def generate_image_prompt(
        self,
        content_analysis: Dict[str, Any],
        style: str = "modern",
        platform: str = "general"
    ) -> str:
        """
        Generate an image generation prompt based on content analysis.
        
        Args:
            content_analysis: Results from analyze_content()
            style: Visual style ("modern", "minimalist", "corporate", "creative")
            platform: Target platform ("whatsapp", "twitter", "discord", "general")
            
        Returns:
            Image generation prompt string
        """
        style_descriptions = {
            "modern": "clean, modern design with bold colors and geometric shapes",
            "minimalist": "minimalist design with lots of white space and simple icons",
            "corporate": "professional corporate style with blue and gray color scheme",
            "creative": "creative and artistic with vibrant colors and unique layouts"
        }
        
        platform_specs = {
            "whatsapp": "square format, mobile-friendly, high contrast",
            "twitter": "landscape format, social media optimized, eye-catching",
            "discord": "landscape format, dark theme compatible, gaming aesthetic",
            "general": "versatile format, web and print friendly"
        }
        
        main_topic = content_analysis.get("main_topic", "Information")
        key_points = content_analysis.get("key_points", [])
        
        prompt = f"""Create an infographic about "{main_topic}" with {style_descriptions.get(style, 'modern')} style.
        
Key elements to include:
{chr(10).join(f"- {point}" for point in key_points[:4])}

Format: {platform_specs.get(platform, 'general format')}
Style: Professional infographic design, clear typography, data visualization elements
Colors: Harmonious color palette appropriate for the topic
Layout: Well-organized hierarchy with clear visual flow"""
        
        return prompt
    
    def generate_text_content(
        self,
        topic: str,
        content_type: str = "headline",
        style: str = "professional",
        max_length: int = 100
    ) -> str:
        """
        Generate text content for infographic elements.
        
        Args:
            topic: Main topic or theme
            content_type: Type of content ("headline", "subtitle", "bullet_point", "caption")
            style: Writing style ("professional", "casual", "technical", "creative")
            max_length: Maximum character length
            
        Returns:
            Generated text content
        """
        style_instructions = {
            "professional": "formal, business-appropriate tone",
            "casual": "friendly, conversational tone", 
            "technical": "precise, technical language",
            "creative": "engaging, creative language"
        }
        
        content_instructions = {
            "headline": f"Create a compelling headline (max {max_length} characters)",
            "subtitle": f"Create a descriptive subtitle (max {max_length} characters)",
            "bullet_point": f"Create a concise bullet point (max {max_length} characters)",
            "caption": f"Create an informative caption (max {max_length} characters)"
        }
        
        prompt = f"""Generate {content_type} text about "{topic}".
        
Requirements:
- {content_instructions.get(content_type, 'Create appropriate text')}
- Use {style_instructions.get(style, 'professional')}
- Maximum {max_length} characters
- Suitable for infographic display
- Clear and impactful

Return only the text content, no additional formatting or explanation."""
        
        try:
            response = self.invoke_model(
                prompt=prompt,
                temperature=0.7,
                max_tokens=200
            )
            
            # Clean up response and ensure length limit
            cleaned_response = response.strip().strip('"').strip("'")
            if len(cleaned_response) > max_length:
                cleaned_response = cleaned_response[:max_length-3] + "..."
            
            return cleaned_response
            
        except Exception as e:
            raise BedrockInvocationError(f"Text generation failed: {str(e)}")
    
    def extract_key_information(
        self,
        text: str,
        info_type: str = "facts"
    ) -> List[str]:
        """
        Extract specific types of information from text.
        
        Args:
            text: Source text to extract from
            info_type: Type of information ("facts", "statistics", "quotes", "dates", "names")
            
        Returns:
            List of extracted information items
        """
        extraction_prompts = {
            "facts": "Extract the most important factual statements from this text. Return as a JSON array of strings.",
            "statistics": "Extract all numerical data, percentages, and statistics from this text. Return as a JSON array of strings.",
            "quotes": "Extract notable quotes or key statements from this text. Return as a JSON array of strings.",
            "dates": "Extract all dates, time periods, and temporal references from this text. Return as a JSON array of strings.",
            "names": "Extract all proper names (people, places, organizations) from this text. Return as a JSON array of strings."
        }
        
        if info_type not in extraction_prompts:
            raise BedrockInvocationError(f"Unknown information type: {info_type}")
        
        prompt = f"""{extraction_prompts[info_type]}

Text: {text}

Return only valid JSON array format."""
        
        try:
            response = self.invoke_model(
                prompt=prompt,
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000
            )
            
            # Try to parse as JSON array
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback: split by lines and clean up
                lines = [line.strip() for line in response.split('\n') if line.strip()]
                return [line.lstrip('- ').strip('"').strip("'") for line in lines if line]
                
        except Exception as e:
            raise BedrockInvocationError(f"Information extraction failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_id": self.model_id,
            "region": self.region,
            "provider": self.model_config["provider"],
            "max_tokens": self.model_config["max_tokens"],
            "supports_system": self.model_config["supports_system"],
            "input_format": self.model_config["input_format"]
        }


# Convenience functions for common operations
def analyze_text_for_infographic(
    text: str,
    model_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze text for infographic creation.
    
    Args:
        text: Text content to analyze
        model_id: Optional Bedrock model ID
        
    Returns:
        Comprehensive analysis results
    """
    bedrock_tools = BedrockTools(model_id=model_id)
    
    try:
        # Perform comprehensive analysis
        general_analysis = bedrock_tools.analyze_content(text, "general")
        key_points = bedrock_tools.analyze_content(text, "key_points")
        structure = bedrock_tools.analyze_content(text, "structure")
        summary = bedrock_tools.analyze_content(text, "summary")
        
        # Extract additional information
        facts = bedrock_tools.extract_key_information(text, "facts")
        statistics = bedrock_tools.extract_key_information(text, "statistics")
        
        return {
            "general_analysis": general_analysis,
            "key_points": key_points,
            "structure": structure,
            "summary": summary,
            "facts": facts,
            "statistics": statistics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Comprehensive text analysis failed: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def generate_infographic_content(
    topic: str,
    style: str = "professional",
    model_id: Optional[str] = None
) -> Dict[str, str]:
    """
    Convenience function to generate all text content for an infographic.
    
    Args:
        topic: Main topic for the infographic
        style: Writing style
        model_id: Optional Bedrock model ID
        
    Returns:
        Dictionary containing generated content elements
    """
    bedrock_tools = BedrockTools(model_id=model_id)
    
    try:
        content = {
            "headline": bedrock_tools.generate_text_content(topic, "headline", style, 60),
            "subtitle": bedrock_tools.generate_text_content(topic, "subtitle", style, 120),
            "bullet_points": [
                bedrock_tools.generate_text_content(f"{topic} key point {i+1}", "bullet_point", style, 80)
                for i in range(3)
            ],
            "caption": bedrock_tools.generate_text_content(topic, "caption", style, 150)
        }
        
        return content
        
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}")
        return {
            "error": str(e),
            "headline": f"About {topic}",
            "subtitle": "Key Information and Insights",
            "bullet_points": ["Key Point 1", "Key Point 2", "Key Point 3"],
            "caption": f"Learn more about {topic}"
        }


def create_bedrock_tools() -> BedrockTools:
    """
    Factory function to create BedrockTools instance with environment configuration.
    
    Returns:
        Configured BedrockTools instance
    """
    return BedrockTools()