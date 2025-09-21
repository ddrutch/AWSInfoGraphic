# Testing Infrastructure for AWS Infographic Generator

This directory contains the testing infrastructure and patterns for the AWS Infographic Generator system. The testing approach focuses on comprehensive validation, mocking strategies, and performance monitoring without requiring actual test execution.

## Testing Philosophy

The system is designed with testability in mind, following these principles:

1. **Dependency Injection**: All components accept their dependencies, making them easy to mock
2. **Clear Interfaces**: Well-defined interfaces between components enable isolated testing
3. **Comprehensive Validation**: Built-in validation at all levels supports testing scenarios
4. **Error Handling**: Robust error handling with categorization supports error scenario testing
5. **Monitoring Integration**: Performance tracking and metrics collection support load testing

## Testing Infrastructure Components

### 1. Test Helpers (`utils/test_helpers.py`)

Provides utilities for creating test data and mock objects:

- **MockDataFactory**: Creates mock data objects for all system types
- **MockAWSServices**: Provides mock AWS service responses
- **TestDataGenerator**: Generates test data for various scenarios
- **MockImageGenerator**: Creates test images for validation
- **ValidationHelpers**: Validates outputs and system behavior
- **PerformanceBenchmarks**: Performance expectations and validation

### 2. Configuration Management (`utils/config.py`)

Supports testing through environment-specific configurations:

- **Testing Environment**: Automatically enables mocking and safe defaults
- **Mock Service Configuration**: Disables external service calls in testing mode
- **Validation Configuration**: Configurable validation rules for different environments

### 3. Validation Framework (`utils/validation.py`)

Comprehensive validation for all system components:

- **Input Validation**: Validates user inputs and system parameters
- **Output Validation**: Validates generated content and system outputs
- **System Validation**: Validates system readiness and configuration
- **Comprehensive Validation**: End-to-end validation orchestration

### 4. Error Handling (`utils/error_handling.py`)

Structured error handling that supports testing:

- **Error Categories**: Categorized errors for specific testing scenarios
- **Retry Logic**: Configurable retry strategies for testing resilience
- **Circuit Breakers**: Failure prevention patterns for load testing
- **Fallback Mechanisms**: Graceful degradation for testing edge cases

### 5. Monitoring (`utils/monitoring.py`)

Performance monitoring and metrics collection:

- **Performance Tracking**: Operation timing and success rate tracking
- **Health Monitoring**: System health checks and alerting
- **Agent Performance**: Individual agent performance metrics
- **Structured Logging**: Consistent logging for test analysis

## Testing Patterns

### 1. Unit Testing Pattern

```python
class TestContentAnalyzer(unittest.TestCase):
    def setUp(self):
        # Use test helpers to create mock dependencies
        self.mock_factory = MockDataFactory()
        self.aws_mocks = MockAWSServices()
        
        # Create test configuration
        self.config = create_testing_config()
        
        # Set up validation helpers
        self.validator = ValidationHelpers()
    
    def test_content_analysis(self):
        # Generate test data
        test_text = TestDataGenerator.generate_sample_text("medium")
        
        # Create mock responses
        mock_analysis = self.mock_factory.create_mock_content_analysis()
        
        # Validate inputs
        input_validation = validate_text_input(test_text)
        self.assertTrue(input_validation["valid"])
        
        # Test the functionality (with mocked dependencies)
        # ... test implementation ...
        
        # Validate outputs
        output_validation = validate_content_analysis(result)
        self.assertTrue(output_validation["valid"])
```

### 2. Integration Testing Pattern

```python
class TestMultiAgentWorkflow(unittest.TestCase):
    def setUp(self):
        # Set up complete test environment
        self.test_env = setup_test_environment()
        
        # Configure system for testing
        self.config = create_testing_config()
        
        # Set up monitoring
        self.health_monitor = get_health_monitor()
    
    def test_end_to_end_generation(self):
        # Test complete workflow with mocked AWS services
        # Validate each step of the process
        # Check performance metrics
        # Verify error handling
```

### 3. Performance Testing Pattern

```python
class TestPerformance(unittest.TestCase):
    def test_content_analysis_performance(self):
        # Use performance benchmarks
        benchmarks = PerformanceBenchmarks.get_performance_expectations()
        
        # Time the operation
        start_time = time.time()
        # ... perform operation ...
        duration = time.time() - start_time
        
        # Validate performance
        performance_result = PerformanceBenchmarks.validate_performance(
            "content_analysis", duration
        )
        
        self.assertTrue(performance_result["within_max"])
```

### 4. Error Scenario Testing Pattern

```python
class TestErrorHandling(unittest.TestCase):
    def test_error_scenarios(self):
        # Generate error scenarios
        error_scenarios = TestDataGenerator.generate_error_scenarios()
        
        for scenario in error_scenarios:
            with self.subTest(scenario=scenario["scenario"]):
                # Test error handling behavior
                # Verify retry logic
                # Check fallback mechanisms
```

## Mock Strategies

### AWS Service Mocking

The system provides comprehensive AWS service mocking:

```python
# Mock Bedrock responses
mock_bedrock_response = MockAWSServices.create_mock_bedrock_json_response({
    "analysis": "mock analysis result"
})

# Mock S3 operations
mock_s3_response = MockAWSServices.create_mock_s3_upload_response(
    bucket="test-bucket", key="test-image.png"
)

# Mock Nova Canvas image generation
mock_image_data = b"mock-image-data"
mock_nova_response = MockAWSServices.create_mock_nova_canvas_response(mock_image_data)
```

### Agent Mocking

Agents can be mocked at different levels:

```python
# Mock entire agent
mock_agent = Mock()
mock_agent.analyze.return_value = MockDataFactory.create_mock_agent_response()

# Mock agent tools
with patch('agents.content_analyzer.ContentTools') as mock_tools:
    mock_tools.return_value.create_content_analysis.return_value = mock_analysis
    # ... test with mocked tools ...
```

## Validation Strategies

### Input Validation Testing

```python
def test_input_validation(self):
    # Test valid inputs
    valid_text = TestDataGenerator.generate_sample_text("medium")
    validation = validate_text_input(valid_text)
    self.assertTrue(validation["valid"])
    
    # Test invalid inputs
    invalid_inputs = ["", "x" * 20000, None]
    for invalid_input in invalid_inputs:
        validation = validate_text_input(invalid_input)
        self.assertFalse(validation["valid"])
```

### Output Validation Testing

```python
def test_output_validation(self):
    # Create test output
    analysis = MockDataFactory.create_mock_content_analysis()
    
    # Validate structure and content
    validation = ValidationHelpers.validate_content_analysis(analysis)
    
    # Check all validation criteria
    for criterion, passed in validation.items():
        self.assertTrue(passed, f"Validation failed for: {criterion}")
```

## Performance Testing

### Benchmarking

The system includes performance benchmarks for all operations:

```python
# Get expected performance benchmarks
benchmarks = PerformanceBenchmarks.get_performance_expectations()

# Validate operation performance
performance_result = PerformanceBenchmarks.validate_performance(
    operation="content_analysis",
    duration=actual_duration
)

# Check performance status
self.assertIn(performance_result["status"], ["excellent", "good"])
```

### Load Testing

```python
def test_concurrent_requests(self):
    # Test multiple concurrent requests
    # Monitor system resources
    # Validate performance under load
    # Check error rates and fallback behavior
```

## Error Handling Testing

### Error Categories

Test different error categories:

```python
error_scenarios = [
    {"category": ErrorCategory.NETWORK, "should_retry": True},
    {"category": ErrorCategory.VALIDATION, "should_retry": False},
    {"category": ErrorCategory.AWS_SERVICE, "should_retry": True},
    {"category": ErrorCategory.RATE_LIMIT, "should_retry": True}
]
```

### Retry Logic Testing

```python
def test_retry_behavior(self):
    # Test exponential backoff
    # Test retry limits
    # Test circuit breaker behavior
    # Test fallback mechanisms
```

## Test Data Management

### Sample Data

The system provides various sample data generators:

```python
# Different text lengths
short_text = TestDataGenerator.generate_sample_text("short")
medium_text = TestDataGenerator.generate_sample_text("medium")
long_text = TestDataGenerator.generate_sample_text("long")

# Platform-specific test cases
platform_cases = TestDataGenerator.generate_platform_test_cases()

# Error scenarios
error_cases = TestDataGenerator.generate_error_scenarios()
```

### Mock Images

```python
# Create test images
test_image = MockImageGenerator.create_test_image(512, 512)
image_file = MockImageGenerator.save_test_image(test_image)

# Clean up after tests
cleanup_test_files([image_file])
```

## Configuration for Testing

### Test Environment Setup

```python
# Create testing configuration
config = create_testing_config()

# Set up mock environment
env = ConfigurationHelpers.create_mock_environment()

# Configure for testing mode
config.testing_config.mock_aws_services = True
config.testing_config.skip_external_calls = True
```

### Environment Variables

Set these environment variables for testing:

```bash
ENVIRONMENT=testing
TESTING=true
MOCK_AWS_SERVICES=true
LOG_LEVEL=DEBUG
```

## Monitoring and Metrics

### Test Monitoring

```python
# Track test performance
health_monitor = get_health_monitor()
tracker = health_monitor.get_agent_tracker("test_agent")

with tracker.track_operation("test_operation"):
    # ... perform test operation ...
    pass

# Get performance stats
stats = tracker.get_stats()
```

### Health Checks

```python
def test_system_health(self):
    # Perform system health check
    health_report = get_health_monitor().check_system_health()
    
    # Validate system status
    self.assertEqual(health_report["status"], "healthy")
```

## Best Practices

1. **Use Dependency Injection**: Always inject dependencies to enable mocking
2. **Validate Inputs and Outputs**: Use the validation framework consistently
3. **Mock External Services**: Never make real AWS calls in tests
4. **Track Performance**: Monitor operation timing and resource usage
5. **Test Error Scenarios**: Include comprehensive error handling tests
6. **Clean Up Resources**: Always clean up temporary files and resources
7. **Use Structured Logging**: Enable structured logging for test analysis
8. **Isolate Tests**: Ensure tests don't depend on each other
9. **Test Edge Cases**: Include boundary conditions and edge cases
10. **Document Test Intent**: Clearly document what each test validates

## Running Tests

While this infrastructure supports comprehensive testing, actual test execution should follow the project's testing policies. The infrastructure provides:

- Mock factories for creating test data
- Validation helpers for verifying behavior
- Performance benchmarks for timing validation
- Error simulation for resilience testing
- Configuration management for test environments

This testing infrastructure ensures the system is thoroughly testable while maintaining flexibility in how tests are actually executed and managed.