# Developer Guide

This guide provides comprehensive information for developers who want to extend, customize, or contribute to the AWS Infographic Generator.

## Architecture Overview

The AWS Infographic Generator follows a multi-agent architecture pattern using the AWS Strands framework. Each agent is responsible for a specific aspect of infographic generation.

### Core Principles

1. **Separation of Concerns:** Each agent handles one specific task
2. **Loose Coupling:** Agents communicate through well-defined interfaces
3. **Fault Tolerance:** Each agent includes error handling and fallback mechanisms
4. **Scalability:** Agents can be scaled independently based on workload
5. **Extensibility:** New agents and tools can be added without modifying existing code

## Development Environment Setup

### Prerequisites

- Python 3.12 or higher
- AWS CLI v2 configured with appropriate permissions
- Access to Amazon Bedrock (Claude 3.5 Sonnet and Nova Canvas)
- S3 bucket for asset storage
- Git for version control

### Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd 02-samples/14-aws-infographic-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env with your AWS credentials and configuration

# Verify setup
python -c "import main; print('Setup successful')"
```

### Development Dependencies

```bash
# Install development dependencies
pip install -e ".[dev]"

# This includes:
# - pytest for testing
# - black for code formatting
# - isort for import sorting
# - mypy for type checking
# - pre-commit for git hooks
```

## Agent Development

### Creating a New Agent

To create a new agent, follow the AWS Strands framework patterns:

```python
# agents/my_new_agent.py
from typing import Dict, Any, List
from aws_strands import Agent, tool
from utils.types import MyDataType

class MyNewAgent(Agent):
    """Agent for handling specific functionality."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config or {})
        self.agent_name = "MyNewAgent"
    
    @tool
    async def my_tool_function(self, input_data: str) -> MyDataType:
        """
        Tool function that performs specific operations.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed data in MyDataType format
        """
        # Implementation here
        pass
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for the agent."""
        try:
            # Agent logic here
            result = await self.my_tool_function(request.get("input"))
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### Agent Integration

To integrate your new agent into the orchestrator:

```python
# main.py - Add to InfographicOrchestrator
from agents.my_new_agent import MyNewAgent

class InfographicOrchestrator:
    def __init__(self, config: Dict = None):
        # ... existing initialization
        self.my_new_agent = MyNewAgent(config)
    
    async def generate_infographic(self, user_input: str, platform: str = "general"):
        # ... existing workflow
        
        # Add your agent to the workflow
        my_result = await self.my_new_agent.process_request({
            "input": processed_content
        })
        
        # ... continue workflow
```

## Tool Development

### Creating Custom Tools

Tools are utility functions that agents use to perform specific operations:

```python
# tools/my_custom_tools.py
import asyncio
from typing import Optional, Dict, Any
from utils.error_handling import handle_aws_errors

class MyCustomTools:
    """Custom tools for specific functionality."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @handle_aws_errors
    async def custom_operation(self, input_data: str) -> Dict[str, Any]:
        """
        Perform a custom operation.
        
        Args:
            input_data: Data to process
            
        Returns:
            Operation result
            
        Raises:
            CustomToolError: When operation fails
        """
        try:
            # Implementation here
            result = await self._process_data(input_data)
            return {"status": "success", "data": result}
        except Exception as e:
            raise CustomToolError(f"Custom operation failed: {e}")
    
    async def _process_data(self, data: str) -> Any:
        """Private method for data processing."""
        # Implementation details
        pass
```

### Tool Integration Patterns

```python
# Integration with agents
from tools.my_custom_tools import MyCustomTools

class MyAgent(Agent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.custom_tools = MyCustomTools(config)
    
    @tool
    async def use_custom_tool(self, input_data: str) -> Dict[str, Any]:
        """Use custom tool in agent context."""
        return await self.custom_tools.custom_operation(input_data)
```

## Data Model Extensions

### Creating New Data Types

Define new data types in the utils/types.py file:

```python
# utils/types.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class MyCustomDataType:
    """Custom data type for specific use case."""
    
    id: str
    name: str
    properties: Dict[str, Any]
    created_at: datetime
    metadata: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MyCustomDataType':
        """Create instance from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            properties=data["properties"],
            created_at=datetime.fromisoformat(data["created_at"]),
            metadata=data.get("metadata")
        )
```

### Validation and Serialization

```python
# utils/validation.py
from typing import Any, Dict
from pydantic import BaseModel, validator

class MyCustomModel(BaseModel):
    """Pydantic model for validation."""
    
    name: str
    value: float
    category: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v
    
    @validator('value')
    def value_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Sample Item",
                "value": 42.0,
                "category": "test"
            }
        }
```

## Configuration Management

### Adding New Configuration Options

```python
# utils/config.py
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass, field

@dataclass
class ExtendedConfig:
    """Extended configuration with custom options."""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    s3_bucket_name: Optional[str] = None
    
    # Custom Configuration
    my_custom_setting: str = "default_value"
    my_feature_enabled: bool = True
    my_numeric_setting: float = 1.0
    
    # Advanced Configuration
    custom_endpoints: Dict[str, str] = field(default_factory=dict)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> 'ExtendedConfig':
        """Load configuration from environment variables."""
        return cls(
            aws_region=os.getenv('AWS_REGION', 'us-east-1'),
            bedrock_model_id=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            s3_bucket_name=os.getenv('S3_BUCKET_NAME'),
            my_custom_setting=os.getenv('MY_CUSTOM_SETTING', 'default_value'),
            my_feature_enabled=os.getenv('MY_FEATURE_ENABLED', 'true').lower() == 'true',
            my_numeric_setting=float(os.getenv('MY_NUMERIC_SETTING', '1.0'))
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.s3_bucket_name:
            raise ValueError("S3_BUCKET_NAME is required")
        
        if self.my_numeric_setting < 0:
            raise ValueError("MY_NUMERIC_SETTING must be non-negative")
```

## Error Handling Patterns

### Custom Exception Classes

```python
# utils/exceptions.py
class InfographicGeneratorError(Exception):
    """Base exception for the infographic generator."""
    pass

class MyCustomError(InfographicGeneratorError):
    """Custom error for specific functionality."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class RetryableError(InfographicGeneratorError):
    """Error that indicates the operation should be retried."""
    
    def __init__(self, message: str, retry_after: int = 5):
        super().__init__(message)
        self.retry_after = retry_after
```

### Error Handling Decorators

```python
# utils/error_handling.py
import functools
import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def handle_retryable_errors(max_retries: int = 3, delay: float = 1.0):
    """Decorator for handling retryable errors with exponential backoff."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except RetryableError as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
                except Exception as e:
                    # Non-retryable error
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
            
            raise last_exception
        
        return wrapper
    return decorator

def handle_aws_errors(func: Callable) -> Callable:
    """Decorator for handling AWS service errors."""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code in ['Throttling', 'ThrottlingException']:
                raise RetryableError(f"AWS throttling: {error_message}", retry_after=5)
            elif error_code in ['ServiceUnavailable', 'InternalError']:
                raise RetryableError(f"AWS service error: {error_message}", retry_after=10)
            else:
                raise MyCustomError(f"AWS error ({error_code}): {error_message}", error_code=error_code)
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper
```

## Testing Strategies

### Unit Testing

```python
# tests/unit/test_my_agent.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from agents.my_new_agent import MyNewAgent
from utils.types import MyDataType

class TestMyNewAgent:
    """Unit tests for MyNewAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        config = {"test_mode": True}
        return MyNewAgent(config)
    
    @pytest.mark.asyncio
    async def test_my_tool_function_success(self, agent):
        """Test successful tool function execution."""
        input_data = "test input"
        
        result = await agent.my_tool_function(input_data)
        
        assert isinstance(result, MyDataType)
        assert result.processed_data == "processed: test input"
    
    @pytest.mark.asyncio
    async def test_my_tool_function_error_handling(self, agent):
        """Test error handling in tool function."""
        with patch.object(agent, '_internal_method', side_effect=Exception("Test error")):
            with pytest.raises(MyCustomError):
                await agent.my_tool_function("invalid input")
    
    @pytest.mark.asyncio
    async def test_process_request_integration(self, agent):
        """Test full request processing."""
        request = {"input": "test data"}
        
        result = await agent.process_request(request)
        
        assert result["success"] is True
        assert "result" in result
```

### Integration Testing

```python
# tests/integration/test_full_workflow.py
import pytest
import asyncio
from main import InfographicOrchestrator
from utils.test_helpers import create_test_config, cleanup_test_resources

class TestFullWorkflow:
    """Integration tests for complete infographic generation."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with test configuration."""
        config = create_test_config()
        orchestrator = InfographicOrchestrator(config)
        yield orchestrator
        await cleanup_test_resources(orchestrator)
    
    @pytest.mark.asyncio
    async def test_end_to_end_generation(self, orchestrator):
        """Test complete infographic generation workflow."""
        content = "Test content for infographic generation"
        platform = "general"
        
        result = await orchestrator.generate_infographic(content, platform)
        
        assert result.s3_url is not None
        assert result.image_path is not None
        assert result.metadata["platform"] == platform
        assert result.generation_time > 0
    
    @pytest.mark.asyncio
    async def test_multiple_platforms(self, orchestrator):
        """Test generation for multiple platforms."""
        content = "Multi-platform test content"
        platforms = ["whatsapp", "twitter", "discord"]
        
        results = []
        for platform in platforms:
            result = await orchestrator.generate_infographic(content, platform)
            results.append(result)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.metadata["platform"] == platforms[i]
```

### Mock AWS Services

```python
# tests/mocks/aws_mocks.py
from unittest.mock import AsyncMock, Mock
import json

class MockBedrockClient:
    """Mock Bedrock client for testing."""
    
    def __init__(self):
        self.invoke_model = AsyncMock()
        self.list_foundation_models = AsyncMock()
    
    async def invoke_model(self, modelId: str, body: str) -> Dict:
        """Mock model invocation."""
        if "claude" in modelId:
            return {
                "body": json.dumps({
                    "content": [{"text": "Mocked Claude response"}]
                }).encode()
            }
        elif "nova-canvas" in modelId:
            return {
                "body": b"mocked_image_data"
            }

class MockS3Client:
    """Mock S3 client for testing."""
    
    def __init__(self):
        self.put_object = AsyncMock()
        self.get_object = AsyncMock()
        self.list_objects_v2 = AsyncMock()
    
    async def put_object(self, Bucket: str, Key: str, Body: bytes, **kwargs) -> Dict:
        """Mock S3 upload."""
        return {
            "ETag": "mock-etag",
            "VersionId": "mock-version"
        }
```

## Performance Optimization

### Caching Strategies

```python
# utils/caching.py
import asyncio
from typing import Any, Dict, Optional
from functools import wraps
import hashlib
import json

class AsyncCache:
    """Async-compatible cache implementation."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self._cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {"args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if asyncio.get_event_loop().time() - entry["timestamp"] < self.ttl:
                return entry["value"]
            else:
                del self._cache[key]
        return None
    
    async def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]
        
        self._cache[key] = {
            "value": value,
            "timestamp": asyncio.get_event_loop().time()
        }

def cached(cache_instance: AsyncCache):
    """Decorator for caching function results."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = cache_instance._generate_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_instance.set(cache_key, result)
            return result
        
        return wrapper
    return decorator
```

### Async Optimization

```python
# utils/async_helpers.py
import asyncio
from typing import List, Callable, Any, TypeVar, Coroutine

T = TypeVar('T')

async def gather_with_concurrency(
    coroutines: List[Coroutine[Any, Any, T]], 
    max_concurrency: int = 10
) -> List[T]:
    """Execute coroutines with limited concurrency."""
    
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def sem_coro(coro):
        async with semaphore:
            return await coro
    
    return await asyncio.gather(*[sem_coro(coro) for coro in coroutines])

async def timeout_wrapper(coro: Coroutine[Any, Any, T], timeout: float) -> T:
    """Wrap coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
```

## Monitoring and Observability

### Custom Metrics

```python
# utils/metrics.py
import time
from typing import Dict, Any, Optional
from functools import wraps
import boto3
from botocore.exceptions import ClientError

class MetricsCollector:
    """Collect and send custom metrics."""
    
    def __init__(self, namespace: str = "InfographicGenerator"):
        self.namespace = namespace
        self.cloudwatch = boto3.client('cloudwatch')
    
    async def put_metric(
        self, 
        metric_name: str, 
        value: float, 
        unit: str = "Count",
        dimensions: Optional[Dict[str, str]] = None
    ) -> None:
        """Send metric to CloudWatch."""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
            
            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': v} for k, v in dimensions.items()
                ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
        except ClientError as e:
            # Log error but don't fail the main operation
            print(f"Failed to send metric {metric_name}: {e}")

def measure_performance(metrics_collector: MetricsCollector, metric_name: str):
    """Decorator to measure function performance."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                await metrics_collector.put_metric(
                    f"{metric_name}_duration",
                    duration,
                    "Seconds"
                )
                await metrics_collector.put_metric(
                    f"{metric_name}_success",
                    1 if success else 0,
                    "Count"
                )
        
        return wrapper
    return decorator
```

## Deployment Considerations

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import main; print('OK')" || exit 1

# Run application
CMD ["python", "main.py"]
```

### Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  infographic-generator:
    build: .
    environment:
      - AWS_REGION=${AWS_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
      - BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## Contributing Guidelines

### Code Style

```python
# Follow PEP 8 and use these tools:
# black for formatting
# isort for import sorting
# mypy for type checking

# Example of well-formatted code:
from typing import Dict, List, Optional, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class WellFormattedClass:
    """Example of properly formatted class."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def process_data(
        self, 
        input_data: List[str], 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input data with optional configuration."""
        options = options or {}
        
        try:
            results = []
            for item in input_data:
                processed = await self._process_item(item, options)
                results.append(processed)
            
            return {"success": True, "results": results}
        
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_item(self, item: str, options: Dict[str, Any]) -> str:
        """Process individual item."""
        # Implementation here
        return f"processed: {item}"
```

### Pull Request Process

1. **Fork and Branch:** Create feature branch from main
2. **Implement:** Follow coding standards and add tests
3. **Test:** Ensure all tests pass and add new tests for new features
4. **Document:** Update documentation and add docstrings
5. **Review:** Submit PR with clear description and examples

### Commit Message Format

```
type(scope): brief description

Longer description if needed

- List specific changes
- Include breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Extension Examples

### Custom Platform Support

```python
# Add support for a new platform
PLATFORM_SPECS["linkedin"] = {
    "dimensions": (1200, 627),
    "format": "PNG",
    "max_text_elements": 6,
    "font_scale": 0.95,
    "color_scheme": "professional"
}

# Extend layout agent
class ExtendedDesignLayout(DesignLayout):
    async def create_linkedin_layout(self, content: ContentAnalysis) -> LayoutSpecification:
        """Create LinkedIn-optimized layout."""
        # LinkedIn-specific layout logic
        pass
```

### Custom Content Processors

```python
# Add support for new content types
class TechnicalContentProcessor:
    """Processor for technical documentation."""
    
    async def process_code_snippets(self, content: str) -> ContentAnalysis:
        """Process content with code snippets."""
        # Extract and format code blocks
        # Identify technical terms
        # Create appropriate visual hierarchy
        pass
    
    async def process_api_documentation(self, content: str) -> ContentAnalysis:
        """Process API documentation content."""
        # Parse API endpoints
        # Extract parameters and responses
        # Create structured layout
        pass
```

This developer guide provides the foundation for extending and customizing the AWS Infographic Generator. Follow these patterns and best practices to maintain code quality and system reliability.