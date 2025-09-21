# API Reference

This document provides comprehensive API documentation for all agents, tools, and configuration options in the AWS Infographic Generator.

## Core Classes

### InfographicOrchestrator

The main orchestrator class that coordinates the multi-agent workflow.

```python
class InfographicOrchestrator:
    """Main orchestrator for infographic generation workflow."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Optional configuration dictionary
        """
    
    async def generate_infographic(
        self, 
        user_input: str, 
        platform: str = "general",
        output_format: str = "PNG"
    ) -> InfographicResult:
        """
        Generate an infographic from text input.
        
        Args:
            user_input: Text content to convert to infographic
            platform: Target platform ("whatsapp", "twitter", "discord", "general")
            output_format: Output format ("PNG", "JPEG", "PDF")
            
        Returns:
            InfographicResult with S3 URL and metadata
            
        Raises:
            ValueError: Invalid platform or format
            AWSServiceError: AWS service unavailable
            GenerationError: Infographic generation failed
        """
    
    async def get_status(self, request_id: str) -> ProcessingStatus:
        """
        Get the status of an infographic generation request.
        
        Args:
            request_id: Unique identifier for the generation request
            
        Returns:
            ProcessingStatus with current state and progress
        """
```

### Configuration Options

```python
DEFAULT_CONFIG = {
    # AWS Configuration
    "aws_region": "us-east-1",
    "bedrock_model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "nova_canvas_model_id": "amazon.nova-canvas-v1:0",
    "s3_bucket_name": None,  # Required
    
    # Image Configuration
    "max_image_size": 2048,
    "image_quality": 95,
    "default_format": "PNG",
    
    # Generation Configuration
    "max_retries": 3,
    "timeout_seconds": 300,
    "enable_caching": True,
    
    # Platform Specifications
    "platforms": {
        "whatsapp": {"dimensions": (1080, 1080), "format": "PNG"},
        "twitter": {"dimensions": (1200, 675), "format": "PNG"},
        "discord": {"dimensions": (1920, 1080), "format": "PNG"},
        "general": {"dimensions": (1920, 1080), "format": "PNG"}
    },
    
    # Design Configuration
    "color_schemes": {
        "professional": {
            "primary": "#2563EB",
            "secondary": "#64748B", 
            "accent": "#10B981",
            "background": "#F8FAFC"
        },
        "tech": {
            "primary": "#7C3AED",
            "secondary": "#374151",
            "accent": "#F59E0B", 
            "background": "#111827"
        }
    },
    
    # Text Configuration
    "fonts": {
        "primary": "Arial",
        "secondary": "Helvetica",
        "monospace": "Courier New"
    },
    "min_font_size": 14,
    "line_height": 1.4
}
```

## Agent APIs

### ContentAnalyzer

Analyzes text content and extracts structured information.

```python
class ContentAnalyzer:
    """Agent for analyzing and structuring text content."""
    
    async def analyze_content(self, text: str) -> ContentAnalysis:
        """
        Analyze text content and extract key information.
        
        Args:
            text: Input text to analyze
            
        Returns:
            ContentAnalysis with structured data
        """
    
    async def extract_key_points(self, text: str, max_points: int = 7) -> List[str]:
        """
        Extract key points from text.
        
        Args:
            text: Input text
            max_points: Maximum number of points to extract
            
        Returns:
            List of key points
        """
    
    async def generate_title(self, text: str) -> str:
        """
        Generate a suitable title for the content.
        
        Args:
            text: Input text
            
        Returns:
            Generated title string
        """
```

#### ContentAnalysis Data Model

```python
@dataclass
class ContentAnalysis:
    main_topic: str                    # Primary topic/theme
    key_points: List[str]             # Extracted key points
    hierarchy: Dict[str, Any]         # Content structure
    summary: str                      # Brief summary
    suggested_title: str              # Generated title
    content_type: str                 # Type classification
    sentiment: str                    # Sentiment analysis
    complexity_score: float           # Content complexity (0-1)
    estimated_reading_time: int       # Reading time in seconds
```

### ImageSourcer

Sources and generates images for infographics.

```python
class ImageSourcer:
    """Agent for sourcing and generating images."""
    
    async def source_images(
        self, 
        topic: str, 
        count: int = 3,
        style: str = "professional"
    ) -> List[ImageAsset]:
        """
        Source relevant images for a topic.
        
        Args:
            topic: Topic to find images for
            count: Number of images to source
            style: Image style preference
            
        Returns:
            List of ImageAsset objects
        """
    
    async def generate_image(
        self, 
        prompt: str, 
        dimensions: Tuple[int, int] = (1024, 1024)
    ) -> ImageAsset:
        """
        Generate an image using Amazon Nova Canvas.
        
        Args:
            prompt: Text prompt for image generation
            dimensions: Image dimensions (width, height)
            
        Returns:
            Generated ImageAsset
        """
    
    async def create_placeholder(
        self, 
        dimensions: Tuple[int, int],
        text: str = "Image"
    ) -> ImageAsset:
        """
        Create a placeholder image.
        
        Args:
            dimensions: Image dimensions
            text: Placeholder text
            
        Returns:
            Placeholder ImageAsset
        """
```

#### ImageAsset Data Model

```python
@dataclass
class ImageAsset:
    url: Optional[str]                # S3 URL if uploaded
    local_path: Optional[str]         # Local file path
    description: str                  # Image description
    dimensions: Tuple[int, int]       # Width, height
    asset_type: str                   # "stock", "generated", "placeholder"
    file_size: int                    # File size in bytes
    format: str                       # Image format (PNG, JPEG, etc.)
    metadata: Dict[str, Any]          # Additional metadata
    generation_prompt: Optional[str]   # Original generation prompt
    cache_key: Optional[str]          # Cache identifier
```

### DesignLayout

Creates optimal visual layouts for infographics.

```python
class DesignLayout:
    """Agent for creating visual layouts."""
    
    async def create_layout(
        self,
        content_analysis: ContentAnalysis,
        images: List[ImageAsset],
        platform: str = "general"
    ) -> LayoutSpecification:
        """
        Create a layout specification for the infographic.
        
        Args:
            content_analysis: Analyzed content structure
            images: Available images
            platform: Target platform
            
        Returns:
            LayoutSpecification with element positioning
        """
    
    async def optimize_for_platform(
        self,
        layout: LayoutSpecification,
        platform: str
    ) -> LayoutSpecification:
        """
        Optimize layout for specific platform requirements.
        
        Args:
            layout: Base layout specification
            platform: Target platform
            
        Returns:
            Platform-optimized layout
        """
    
    async def calculate_text_positioning(
        self,
        text_elements: List[str],
        canvas_size: Tuple[int, int]
    ) -> List[TextPosition]:
        """
        Calculate optimal text positioning.
        
        Args:
            text_elements: List of text elements
            canvas_size: Canvas dimensions
            
        Returns:
            List of text positions
        """
```

#### LayoutSpecification Data Model

```python
@dataclass
class LayoutSpecification:
    canvas_size: Tuple[int, int]      # Canvas dimensions
    elements: List[LayoutElement]     # Layout elements
    color_scheme: ColorScheme         # Color palette
    platform_optimizations: Dict[str, Any]  # Platform-specific settings
    grid_system: GridSystem           # Layout grid
    margins: Margins                  # Canvas margins
    typography: TypographySettings    # Font and text settings
    
@dataclass
class LayoutElement:
    element_type: str                 # "text", "image", "shape"
    position: Tuple[float, float]     # Normalized coordinates (0-1)
    size: Tuple[float, float]         # Normalized size (0-1)
    content: Any                      # Element content
    styling: Dict[str, Any]           # Element-specific styling
    z_index: int                      # Layer order
    alignment: str                    # Text alignment
    padding: Tuple[int, int, int, int]  # Top, right, bottom, left
```

### TextFormatter

Applies typography and text styling.

```python
class TextFormatter:
    """Agent for text formatting and typography."""
    
    async def format_text(
        self,
        text_elements: List[str],
        layout: LayoutSpecification
    ) -> List[FormattedText]:
        """
        Apply formatting to text elements.
        
        Args:
            text_elements: Raw text elements
            layout: Layout specification
            
        Returns:
            List of formatted text objects
        """
    
    async def calculate_font_sizes(
        self,
        text_elements: List[str],
        canvas_size: Tuple[int, int],
        platform: str
    ) -> Dict[str, int]:
        """
        Calculate appropriate font sizes.
        
        Args:
            text_elements: Text elements to size
            canvas_size: Canvas dimensions
            platform: Target platform
            
        Returns:
            Dictionary mapping element types to font sizes
        """
    
    async def apply_text_effects(
        self,
        text: FormattedText,
        effects: List[str]
    ) -> FormattedText:
        """
        Apply visual effects to text.
        
        Args:
            text: Formatted text object
            effects: List of effects to apply
            
        Returns:
            Text with applied effects
        """
```

### ImageComposer

Creates the final infographic image.

```python
class ImageComposer:
    """Agent for final image composition."""
    
    async def compose_infographic(
        self,
        layout: LayoutSpecification,
        formatted_text: List[FormattedText],
        images: List[ImageAsset]
    ) -> ComposedImage:
        """
        Compose the final infographic image.
        
        Args:
            layout: Layout specification
            formatted_text: Formatted text elements
            images: Image assets
            
        Returns:
            Composed infographic image
        """
    
    async def export_image(
        self,
        composed_image: ComposedImage,
        format: str = "PNG",
        quality: int = 95
    ) -> bytes:
        """
        Export image to specified format.
        
        Args:
            composed_image: Composed image object
            format: Output format
            quality: Image quality (1-100)
            
        Returns:
            Image data as bytes
        """
    
    async def upload_to_s3(
        self,
        image_data: bytes,
        filename: str,
        metadata: Dict[str, str] = None
    ) -> str:
        """
        Upload image to S3 and return URL.
        
        Args:
            image_data: Image data as bytes
            filename: S3 object key
            metadata: Optional metadata
            
        Returns:
            S3 URL of uploaded image
        """
```

## Tool APIs

### S3Tools

Utilities for Amazon S3 operations.

```python
class S3Tools:
    """Utilities for S3 operations."""
    
    async def upload_file(
        self,
        file_data: bytes,
        key: str,
        content_type: str = "image/png",
        metadata: Dict[str, str] = None
    ) -> str:
        """Upload file to S3 and return URL."""
    
    async def download_file(self, key: str) -> bytes:
        """Download file from S3."""
    
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> str:
        """Generate presigned URL for S3 object."""
    
    async def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict]:
        """List objects in S3 bucket."""
    
    async def delete_object(self, key: str) -> bool:
        """Delete object from S3."""
```

### BedrockTools

Utilities for Amazon Bedrock operations.

```python
class BedrockTools:
    """Utilities for Bedrock operations."""
    
    async def invoke_model(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Invoke Bedrock model with prompt."""
    
    async def invoke_claude(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 1000
    ) -> str:
        """Invoke Claude model specifically."""
    
    async def invoke_nova_canvas(
        self,
        prompt: str,
        dimensions: Tuple[int, int] = (1024, 1024),
        style: str = "photographic"
    ) -> bytes:
        """Generate image using Nova Canvas."""
    
    async def list_available_models(self) -> List[str]:
        """List available Bedrock models."""
```

## Error Handling

### Exception Classes

```python
class InfographicGeneratorError(Exception):
    """Base exception for infographic generator."""
    pass

class AWSServiceError(InfographicGeneratorError):
    """AWS service related errors."""
    pass

class ContentAnalysisError(InfographicGeneratorError):
    """Content analysis errors."""
    pass

class ImageGenerationError(InfographicGeneratorError):
    """Image generation errors."""
    pass

class LayoutError(InfographicGeneratorError):
    """Layout creation errors."""
    pass

class CompositionError(InfographicGeneratorError):
    """Image composition errors."""
    pass

class ConfigurationError(InfographicGeneratorError):
    """Configuration errors."""
    pass
```

### Error Response Format

```python
@dataclass
class ErrorResponse:
    error_type: str                   # Error classification
    message: str                      # Human-readable message
    details: Dict[str, Any]           # Additional error details
    timestamp: datetime               # When error occurred
    request_id: str                   # Request identifier
    retry_after: Optional[int]        # Retry delay in seconds
    fallback_available: bool          # Whether fallback is possible
```

## Response Models

### InfographicResult

```python
@dataclass
class InfographicResult:
    image_path: str                   # Local file path
    s3_url: str                       # S3 URL
    metadata: Dict[str, Any]          # Generation metadata
    platform_variants: Dict[str, str] # Platform-specific URLs
    generation_time: float            # Time taken to generate
    file_size: int                    # File size in bytes
    dimensions: Tuple[int, int]       # Image dimensions
    format: str                       # Image format
    request_id: str                   # Unique request identifier
    
    # Analytics
    content_analysis: ContentAnalysis # Original analysis
    performance_metrics: Dict[str, float]  # Performance data
    aws_costs: Dict[str, float]       # Estimated AWS costs
```

### ProcessingStatus

```python
@dataclass
class ProcessingStatus:
    request_id: str                   # Request identifier
    status: str                       # "pending", "processing", "completed", "failed"
    progress: float                   # Progress percentage (0-100)
    current_step: str                 # Current processing step
    estimated_completion: datetime    # Estimated completion time
    error: Optional[ErrorResponse]    # Error if failed
    result: Optional[InfographicResult]  # Result if completed
```

## Usage Examples

### Basic Usage

```python
from main import InfographicOrchestrator

# Initialize orchestrator
orchestrator = InfographicOrchestrator({
    "s3_bucket_name": "my-infographic-bucket",
    "aws_region": "us-east-1"
})

# Generate infographic
result = await orchestrator.generate_infographic(
    user_input="Q4 Sales Results: $5M revenue, 200 new customers",
    platform="twitter",
    output_format="PNG"
)

print(f"Generated: {result.s3_url}")
```

### Advanced Configuration

```python
config = {
    "aws_region": "us-west-2",
    "bedrock_model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "s3_bucket_name": "my-bucket",
    "max_image_size": 4096,
    "color_schemes": {
        "custom": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "accent": "#45B7D1",
            "background": "#FFFFFF"
        }
    },
    "platforms": {
        "custom_platform": {
            "dimensions": (800, 600),
            "format": "JPEG"
        }
    }
}

orchestrator = InfographicOrchestrator(config)
```

### Error Handling

```python
try:
    result = await orchestrator.generate_infographic(content, "twitter")
except AWSServiceError as e:
    print(f"AWS service error: {e.message}")
    # Implement retry logic
except ContentAnalysisError as e:
    print(f"Content analysis failed: {e.message}")
    # Use simplified content processing
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log error and notify administrators
```

### Monitoring Integration

```python
import boto3

# CloudWatch metrics
cloudwatch = boto3.client('cloudwatch')

def log_generation_metrics(result: InfographicResult):
    cloudwatch.put_metric_data(
        Namespace='InfographicGenerator',
        MetricData=[
            {
                'MetricName': 'GenerationTime',
                'Value': result.generation_time,
                'Unit': 'Seconds'
            },
            {
                'MetricName': 'ImageSize',
                'Value': result.file_size,
                'Unit': 'Bytes'
            }
        ]
    )
```

## Rate Limits and Quotas

### AWS Service Limits

| Service | Limit | Notes |
|---------|-------|-------|
| Bedrock Claude | 200 requests/minute | Per model |
| Nova Canvas | 10 requests/minute | Image generation |
| S3 PUT | 3,500 requests/second | Per prefix |
| S3 GET | 5,500 requests/second | Per prefix |

### Application Limits

```python
RATE_LIMITS = {
    "generations_per_minute": 30,
    "generations_per_hour": 500,
    "max_concurrent_generations": 10,
    "max_content_length": 5000,
    "max_image_size": 4096,
    "cache_ttl_seconds": 3600
}
```

## Security Considerations

### IAM Permissions

Minimum required IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:*::foundation-model/amazon.nova-canvas-v1:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket/*"
        }
    ]
}
```

### Input Validation

```python
def validate_input(user_input: str) -> bool:
    """Validate user input for security and content policy."""
    
    # Length check
    if len(user_input) > 5000:
        raise ValueError("Content too long")
    
    # Content filtering
    prohibited_patterns = [
        r'<script.*?>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'data:.*base64', # Base64 data URLs
    ]
    
    for pattern in prohibited_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            raise ValueError("Prohibited content detected")
    
    return True
```

### Data Privacy

- No persistent storage of user content
- Temporary files cleaned up after processing
- S3 objects can have expiration policies
- Logs sanitized to remove sensitive information