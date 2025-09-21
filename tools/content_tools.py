"""
Pure external operation tools for content analysis.

This module provides pure tools for external operations only:
- Bedrock API calls that return raw data
- Basic text validation and preprocessing without business logic
- External service integrations without embedded decision-making

All business logic and reasoning has been moved to AI agent reasoning.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from .bedrock_tools import BedrockTools, BedrockInvocationError
from utils.types import AgentResponse
from utils.constants import VALIDATION_RULES
from utils.error_handling import (
    ValidationError, ProcessingError,
    log_error_context
)

logger = logging.getLogger(__name__)


class ContentToolsError(Exception):
    """Base exception for content tools operations."""
    pass


class ContentTools:
    """
    Pure external operation tools for content processing.
    
    Provides tools for:
    - Raw Bedrock API calls without embedded logic
    - Basic text validation and preprocessing
    - External service integrations
    
    All decision-making and business logic should be handled by AI reasoning.
    """
    
    def __init__(self, bedrock_tools: Optional[BedrockTools] = None):
        """
        Initialize ContentTools with Bedrock integration.
        
        Args:
            bedrock_tools: Optional BedrockTools instance
        """
        self.bedrock_tools = bedrock_tools or BedrockTools()
        
    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """
        Basic text validation without business logic.
        
        Args:
            text: Raw input text
            
        Returns:
            Dictionary with validation results and basic metrics
            
        Raises:
            ValidationError: If text fails basic validation
        """
        try:
            if not text or not text.strip():
                raise ValidationError("Input text cannot be empty")
            
            cleaned_text = text.strip()
            
            # Basic length validation
            if len(cleaned_text) < VALIDATION_RULES["min_input_length"]:
                raise ValidationError(f"Text must be at least {VALIDATION_RULES['min_input_length']} characters long")
            
            if len(cleaned_text) > VALIDATION_RULES["max_input_length"]:
                logger.warning(f"Text exceeds maximum length of {VALIDATION_RULES['max_input_length']} characters")
            
            # Return raw metrics for AI interpretation
            return {
                "is_valid": True,
                "original_length": len(text),
                "cleaned_length": len(cleaned_text),
                "word_count": len(cleaned_text.split()),
                "line_count": len(cleaned_text.split('\n')),
                "character_types": {
                    "letters": sum(c.isalpha() for c in cleaned_text),
                    "digits": sum(c.isdigit() for c in cleaned_text),
                    "spaces": sum(c.isspace() for c in cleaned_text),
                    "punctuation": sum(not c.isalnum() and not c.isspace() for c in cleaned_text)
                },
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ValidationError(f"Text validation failed: {str(e)}")
    
    def clean_text_basic(self, text: str) -> str:
        """
        Basic text cleaning without decision-making logic.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text with basic preprocessing applied
        """
        try:
            # Basic whitespace normalization
            cleaned_text = re.sub(r'\s+', ' ', text.strip())
            
            # Truncate if exceeds maximum length
            if len(cleaned_text) > VALIDATION_RULES["max_input_length"]:
                cleaned_text = cleaned_text[:VALIDATION_RULES["max_input_length"]]
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Basic text cleaning failed: {str(e)}")
            return text  # Return original text if cleaning fails
    
    def bedrock_analyze_raw(
        self, 
        text: str, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Raw Bedrock API call without embedded logic or decision-making.
        
        Args:
            text: Input text to analyze
            prompt: Analysis prompt to send to Bedrock
            system_prompt: Optional system prompt
            temperature: Model temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Raw response from Bedrock model
            
        Raises:
            ContentToolsError: If Bedrock call fails
        """
        try:
            response = self.bedrock_tools.invoke_model(
                prompt=prompt.format(text=text) if "{text}" in prompt else f"{prompt}\n\nText: {text}",
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            raise ContentToolsError(f"Bedrock analysis failed: {str(e)}")
    
    def bedrock_extract_json(
        self, 
        text: str, 
        extraction_prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Raw Bedrock API call that attempts to return JSON data.
        
        Args:
            text: Input text
            extraction_prompt: Prompt for JSON extraction
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with raw response and parsed JSON (if successful)
            
        Raises:
            ContentToolsError: If Bedrock call fails
        """
        try:
            response = self.bedrock_tools.invoke_model(
                prompt=extraction_prompt.format(text=text) if "{text}" in extraction_prompt else f"{extraction_prompt}\n\nText: {text}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Attempt JSON parsing but return both raw and parsed
            result = {
                "raw_response": response,
                "parsed_json": None,
                "parse_success": False,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                parsed = json.loads(response)
                result["parsed_json"] = parsed
                result["parse_success"] = True
            except json.JSONDecodeError as e:
                result["parse_error"] = str(e)
            
            return result
            
        except Exception as e:
            raise ContentToolsError(f"Bedrock JSON extraction failed: {str(e)}")
    
    def extract_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Extract basic text statistics without interpretation.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with raw text statistics
        """
        try:
            # Basic text metrics
            sentences = re.split(r'[.!?]+', text)
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            words = text.split()
            
            # Character analysis
            char_counts = {
                'total': len(text),
                'letters': sum(c.isalpha() for c in text),
                'digits': sum(c.isdigit() for c in text),
                'spaces': sum(c.isspace() for c in text),
                'punctuation': sum(not c.isalnum() and not c.isspace() for c in text)
            }
            
            # Find numbers and percentages
            numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
            
            return {
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "paragraph_count": len(paragraphs),
                "character_counts": char_counts,
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
                "average_sentence_length": len(words) / len([s for s in sentences if s.strip()]) if sentences else 0,
                "numbers_found": numbers,
                "first_sentence": sentences[0].strip() if sentences and sentences[0].strip() else "",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Text statistics extraction failed: {str(e)}")
            return {
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def bedrock_content_analysis(
        self, 
        text: str, 
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Raw Bedrock API call for content analysis without embedded logic.
        
        Args:
            text: Text content to analyze
            analysis_type: Type of analysis to request
            
        Returns:
            Dictionary with raw Bedrock response and metadata
            
        Raises:
            ContentToolsError: If Bedrock call fails
        """
        try:
            # Use the existing bedrock_tools analyze_content method
            response = self.bedrock_tools.analyze_content(text, analysis_type)
            
            # Return raw response with metadata
            return {
                "analysis_type": analysis_type,
                "bedrock_response": response,
                "text_length": len(text),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis_type": analysis_type,
                "bedrock_response": None,
                "text_length": len(text),
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def bedrock_generate_text(
        self, 
        prompt: str, 
        max_length: int = 100,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Raw Bedrock API call for text generation without embedded logic.
        
        Args:
            prompt: Generation prompt
            max_length: Maximum character length for response
            temperature: Model temperature
            
        Returns:
            Dictionary with raw response and metadata
        """
        try:
            response = self.bedrock_tools.invoke_model(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max(50, max_length // 4)  # Rough token estimation
            )
            
            # Basic cleaning without decision-making
            cleaned_response = response.strip().strip('"').strip("'")
            
            return {
                "raw_response": response,
                "cleaned_response": cleaned_response,
                "truncated_response": cleaned_response[:max_length] if len(cleaned_response) > max_length else cleaned_response,
                "response_length": len(cleaned_response),
                "was_truncated": len(cleaned_response) > max_length,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "raw_response": None,
                "cleaned_response": "",
                "truncated_response": "",
                "response_length": 0,
                "was_truncated": False,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }


# Pure external operation tools - no factory functions with embedded logic

def create_content_tools() -> ContentTools:
    """
    Factory function to create ContentTools instance.
    
    Returns:
        Configured ContentTools instance
    """
    return ContentTools()


def validate_and_clean_text(text: str) -> AgentResponse:
    """
    Pure external operation for text validation and basic cleaning.
    
    Args:
        text: Input text to validate and clean
        
    Returns:
        AgentResponse with validation results and cleaned text
    """
    try:
        start_time = datetime.now()
        
        content_tools = create_content_tools()
        
        # Basic validation
        validation_result = content_tools.validate_text_input(text)
        
        # Basic cleaning
        cleaned_text = content_tools.clean_text_basic(text)
        
        # Text statistics
        statistics = content_tools.extract_text_statistics(text)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            success=True,
            data={
                "validation": validation_result,
                "cleaned_text": cleaned_text,
                "statistics": statistics
            },
            metadata={
                "processing_time": processing_time,
                "operation": "validate_and_clean_text",
                "timestamp": datetime.now().isoformat()
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Text validation and cleaning failed: {str(e)}")
        return AgentResponse(
            success=False,
            error=str(e),
            metadata={
                "operation": "validate_and_clean_text",
                "timestamp": datetime.now().isoformat(),
                "text_length": len(text) if text else 0
            }
        )


def call_bedrock_analysis(text: str, analysis_type: str = "general") -> AgentResponse:
    """
    Pure external operation for Bedrock content analysis API call.
    
    Args:
        text: Input text to analyze
        analysis_type: Type of analysis to request
        
    Returns:
        AgentResponse with raw Bedrock analysis results
    """
    try:
        start_time = datetime.now()
        
        content_tools = create_content_tools()
        analysis_result = content_tools.bedrock_content_analysis(text, analysis_type)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AgentResponse(
            success=analysis_result["success"],
            data=analysis_result,
            metadata={
                "processing_time": processing_time,
                "operation": "bedrock_analysis",
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            },
            processing_time=processing_time,
            error=analysis_result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Bedrock analysis call failed: {str(e)}")
        return AgentResponse(
            success=False,
            error=str(e),
            metadata={
                "operation": "bedrock_analysis",
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "text_length": len(text) if text else 0
            }
        )