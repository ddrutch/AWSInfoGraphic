# Architecture Documentation

## System Architecture Diagram

The AWS Infographic Generator follows a multi-agent architecture pattern using AWS Strands framework and AWS services.

```mermaid
graph TB
    %% User Interface Layer
    User[👤 User Input<br/>Text Content] --> CLI[🖥️ CLI Interface<br/>main.py]
    User --> API[🌐 API Interface<br/>FastAPI/Lambda]
    
    %% Orchestration Layer
    CLI --> Orchestrator[🎯 InfographicOrchestrator<br/>Workflow Coordination]
    API --> Orchestrator
    
    %% Agent Layer
    Orchestrator --> ContentAgent[📝 ContentAnalyzer<br/>Text Analysis & Structure]
    Orchestrator --> ImageAgent[🖼️ ImageSourcer<br/>Image Generation & Sourcing]
    Orchestrator --> LayoutAgent[🎨 DesignLayout<br/>Visual Layout Design]
    Orchestrator --> TextAgent[✍️ TextFormatter<br/>Typography & Styling]
    Orchestrator --> ComposerAgent[🖌️ ImageComposer<br/>Final Image Creation]
    
    %% AWS Services Layer
    ContentAgent --> Bedrock1[🧠 Amazon Bedrock<br/>Claude 3.5 Sonnet<br/>Content Analysis]
    ImageAgent --> NovaCanvas[🎨 Amazon Nova Canvas<br/>AI Image Generation]
    LayoutAgent --> Bedrock2[🧠 Amazon Bedrock<br/>Claude 3.5 Sonnet<br/>Layout Intelligence]
    
    %% Storage and Processing
    ImageAgent --> S3Cache[📦 Amazon S3<br/>Image Asset Cache]
    ComposerAgent --> PIL[🖼️ PIL/Pillow<br/>Image Composition]
    ComposerAgent --> S3Output[📤 Amazon S3<br/>Final Output Storage]
    
    %% Output Layer
    S3Output --> URLs[🔗 Shareable URLs<br/>Platform Optimized]
    
    %% Platform Outputs
    URLs --> WhatsApp[📱 WhatsApp<br/>1080x1080 Square]
    URLs --> Twitter[🐦 Twitter<br/>1200x675 Landscape]
    URLs --> Discord[💬 Discord<br/>1920x1080 HD]
    URLs --> General[🌐 General<br/>1920x1080 Universal]
    
    %% Tool Layer (Supporting Services)
    subgraph "Tools & Utilities"
        ContentTools[📊 Content Tools<br/>Analysis Utilities]
        ImageTools[🛠️ Image Tools<br/>Processing Utilities]
        LayoutTools[📐 Layout Tools<br/>Positioning Calculations]
        TextTools[🔤 Text Tools<br/>Font & Styling]
        S3Tools[📦 S3 Tools<br/>Upload/Download]
        BedrockTools[🔧 Bedrock Tools<br/>Model Invocation]
    end
    
    %% Tool Connections
    ContentAgent -.-> ContentTools
    ContentAgent -.-> BedrockTools
    ImageAgent -.-> ImageTools
    ImageAgent -.-> S3Tools
    LayoutAgent -.-> LayoutTools
    LayoutAgent -.-> BedrockTools
    TextAgent -.-> TextTools
    ComposerAgent -.-> S3Tools
    
    %% Monitoring & Logging
    subgraph "Observability"
        CloudWatch[📊 CloudWatch<br/>Metrics & Logs]
        Monitoring[📈 Performance<br/>Monitoring]
    end
    
    Orchestrator -.-> CloudWatch
    S3Output -.-> CloudWatch
    
    %% Styling
    classDef userLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef orchestrationLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef agentLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef awsLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef outputLayer fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef toolLayer fill:#f5f5f5,stroke:#424242,stroke-width:1px
    
    class User,CLI,API userLayer
    class Orchestrator orchestrationLayer
    class ContentAgent,ImageAgent,LayoutAgent,TextAgent,ComposerAgent agentLayer
    class Bedrock1,Bedrock2,NovaCanvas awsLayer
    class S3Cache,S3Output,PIL storageLayer
    class URLs,WhatsApp,Twitter,Discord,General outputLayer
    class ContentTools,ImageTools,LayoutTools,TextTools,S3Tools,BedrockTools toolLayer
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant CA as ContentAnalyzer
    participant IS as ImageSourcer
    participant DL as DesignLayout
    participant TF as TextFormatter
    participant IC as ImageComposer
    participant B as Bedrock
    participant NC as Nova Canvas
    participant S3 as Amazon S3
    
    U->>O: Generate infographic request
    O->>CA: Analyze content
    CA->>B: Extract key points & structure
    B-->>CA: Structured content analysis
    CA-->>O: ContentAnalysis result
    
    O->>IS: Source/generate images
    IS->>NC: Generate relevant images
    NC-->>IS: Generated image data
    IS->>S3: Cache images
    S3-->>IS: Image URLs
    IS-->>O: ImageAsset list
    
    O->>DL: Create layout design
    DL->>B: Optimize layout for platform
    B-->>DL: Layout recommendations
    DL-->>O: LayoutSpecification
    
    O->>TF: Format text elements
    TF-->>O: FormattedText list
    
    O->>IC: Compose final image
    IC->>S3: Download cached images
    S3-->>IC: Image data
    IC->>IC: Composite using PIL/Pillow
    IC->>S3: Upload final infographic
    S3-->>IC: Public URL
    IC-->>O: InfographicResult
    
    O-->>U: Generated infographic URL
```

## Component Architecture

### Agent Framework (AWS Strands)

```mermaid
graph LR
    subgraph "AWS Strands Framework"
        Agent[Agent Base Class]
        Tools[Tool Decorators]
        Context[Context Management]
        Communication[Agent Communication]
    end
    
    subgraph "Specialized Agents"
        ContentAnalyzer --> Agent
        ImageSourcer --> Agent
        DesignLayout --> Agent
        TextFormatter --> Agent
        ImageComposer --> Agent
    end
    
    subgraph "Tool Integration"
        BedrockTools --> Tools
        S3Tools --> Tools
        ImageTools --> Tools
        LayoutTools --> Tools
        TextTools --> Tools
    end
    
    Agent --> Context
    Agent --> Communication
    Tools --> Context
```

### AWS Service Integration

```mermaid
graph TB
    subgraph "Application Layer"
        App[Infographic Generator]
    end
    
    subgraph "AWS AI/ML Services"
        Bedrock[Amazon Bedrock<br/>- Claude 3.5 Sonnet<br/>- Content Analysis<br/>- Layout Intelligence]
        Nova[Amazon Nova Canvas<br/>- Image Generation<br/>- Style Transfer<br/>- Visual Assets]
    end
    
    subgraph "AWS Storage Services"
        S3[Amazon S3<br/>- Asset Storage<br/>- Output Hosting<br/>- Caching Layer]
    end
    
    subgraph "AWS Compute Services"
        Lambda[AWS Lambda<br/>- Serverless Execution<br/>- Event Processing]
        EC2[Amazon EC2<br/>- Container Hosting<br/>- Batch Processing]
    end
    
    subgraph "AWS Monitoring"
        CloudWatch[Amazon CloudWatch<br/>- Metrics & Logs<br/>- Performance Monitoring<br/>- Alerting]
    end
    
    App --> Bedrock
    App --> Nova
    App --> S3
    App --> Lambda
    App --> EC2
    App --> CloudWatch
    
    Bedrock -.-> CloudWatch
    Nova -.-> CloudWatch
    S3 -.-> CloudWatch
```

## Security Architecture

```mermaid
graph TB
    subgraph "Identity & Access"
        IAM[AWS IAM<br/>- Service Roles<br/>- User Policies<br/>- Resource Permissions]
        STS[AWS STS<br/>- Temporary Credentials<br/>- Role Assumption]
    end
    
    subgraph "Network Security"
        VPC[Amazon VPC<br/>- Network Isolation<br/>- Security Groups]
        WAF[AWS WAF<br/>- Application Firewall<br/>- DDoS Protection]
    end
    
    subgraph "Data Security"
        KMS[AWS KMS<br/>- Encryption Keys<br/>- Data Protection]
        S3Encryption[S3 Encryption<br/>- Server-Side Encryption<br/>- Access Control]
    end
    
    subgraph "Application Security"
        InputValidation[Input Validation<br/>- Content Filtering<br/>- Size Limits]
        OutputSanitization[Output Sanitization<br/>- Safe URLs<br/>- Clean Metadata]
    end
    
    subgraph "Monitoring & Compliance"
        CloudTrail[AWS CloudTrail<br/>- API Logging<br/>- Audit Trail]
        Config[AWS Config<br/>- Compliance Monitoring<br/>- Resource Tracking]
    end
    
    IAM --> STS
    VPC --> WAF
    KMS --> S3Encryption
    InputValidation --> OutputSanitization
    CloudTrail --> Config
```

## Deployment Architecture

### Local Development

```mermaid
graph LR
    subgraph "Developer Machine"
        IDE[IDE/Editor]
        LocalEnv[Local Environment<br/>Python 3.12+<br/>Dependencies]
        AWSCreds[AWS Credentials<br/>~/.aws/credentials]
    end
    
    subgraph "AWS Services"
        DevBedrock[Bedrock Dev Access]
        DevS3[S3 Dev Bucket]
        DevCloudWatch[CloudWatch Dev]
    end
    
    IDE --> LocalEnv
    LocalEnv --> AWSCreds
    AWSCreds --> DevBedrock
    AWSCreds --> DevS3
    AWSCreds --> DevCloudWatch
```

### Production Deployment

```mermaid
graph TB
    subgraph "Load Balancer"
        ALB[Application Load Balancer<br/>- SSL Termination<br/>- Health Checks]
    end
    
    subgraph "Compute Layer"
        ECS[Amazon ECS<br/>- Container Orchestration<br/>- Auto Scaling]
        Lambda[AWS Lambda<br/>- Serverless Functions<br/>- Event Processing]
    end
    
    subgraph "Storage Layer"
        S3Prod[Amazon S3<br/>- Production Assets<br/>- CDN Integration]
        EFS[Amazon EFS<br/>- Shared Storage<br/>- Cache Layer]
    end
    
    subgraph "Monitoring"
        CloudWatchProd[CloudWatch<br/>- Production Metrics<br/>- Alerting]
        XRay[AWS X-Ray<br/>- Distributed Tracing<br/>- Performance Analysis]
    end
    
    ALB --> ECS
    ALB --> Lambda
    ECS --> S3Prod
    ECS --> EFS
    Lambda --> S3Prod
    ECS --> CloudWatchProd
    Lambda --> CloudWatchProd
    ECS --> XRay
    Lambda --> XRay
```

## Performance Architecture

### Caching Strategy

```mermaid
graph TB
    subgraph "Cache Layers"
        MemoryCache[In-Memory Cache<br/>- Recent Results<br/>- Hot Data]
        S3Cache[S3 Cache<br/>- Generated Images<br/>- Processed Assets]
        BedrockCache[Bedrock Response Cache<br/>- Content Analysis<br/>- Layout Decisions]
    end
    
    subgraph "Cache Invalidation"
        TTL[Time-Based TTL<br/>- Configurable Expiry<br/>- Automatic Cleanup]
        ContentHash[Content-Based Hash<br/>- Input Fingerprinting<br/>- Change Detection]
    end
    
    MemoryCache --> TTL
    S3Cache --> TTL
    BedrockCache --> TTL
    MemoryCache --> ContentHash
    S3Cache --> ContentHash
    BedrockCache --> ContentHash
```

### Scaling Strategy

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        LoadBalancer[Load Balancer]
        Instance1[Instance 1]
        Instance2[Instance 2]
        InstanceN[Instance N]
    end
    
    subgraph "Vertical Scaling"
        CPUScaling[CPU-Based Scaling<br/>- Processing Power<br/>- Image Composition]
        MemoryScaling[Memory-Based Scaling<br/>- Large Images<br/>- Batch Processing]
    end
    
    subgraph "Service Scaling"
        BedrockQuota[Bedrock Quotas<br/>- Request Limits<br/>- Rate Limiting]
        S3Throughput[S3 Throughput<br/>- Upload/Download<br/>- Parallel Operations]
    end
    
    LoadBalancer --> Instance1
    LoadBalancer --> Instance2
    LoadBalancer --> InstanceN
    
    Instance1 --> CPUScaling
    Instance1 --> MemoryScaling
    CPUScaling --> BedrockQuota
    MemoryScaling --> S3Throughput
```

## Error Handling Architecture

```mermaid
graph TB
    subgraph "Error Detection"
        InputValidation[Input Validation<br/>- Content Checks<br/>- Size Limits]
        ServiceMonitoring[Service Monitoring<br/>- Health Checks<br/>- Availability]
    end
    
    subgraph "Error Recovery"
        RetryLogic[Retry Logic<br/>- Exponential Backoff<br/>- Circuit Breaker]
        Fallbacks[Fallback Mechanisms<br/>- Placeholder Images<br/>- Simplified Layouts]
    end
    
    subgraph "Error Reporting"
        Logging[Structured Logging<br/>- Error Context<br/>- Performance Metrics]
        Alerting[Alerting System<br/>- Critical Errors<br/>- Performance Degradation]
    end
    
    InputValidation --> RetryLogic
    ServiceMonitoring --> RetryLogic
    RetryLogic --> Fallbacks
    Fallbacks --> Logging
    Logging --> Alerting
```

## Integration Patterns

### Event-Driven Architecture

```mermaid
graph LR
    subgraph "Event Sources"
        UserRequest[User Request]
        ScheduledJob[Scheduled Job]
        WebhookTrigger[Webhook Trigger]
    end
    
    subgraph "Event Processing"
        EventBridge[Amazon EventBridge<br/>- Event Routing<br/>- Rule Processing]
        SQS[Amazon SQS<br/>- Queue Management<br/>- Retry Logic]
    end
    
    subgraph "Event Handlers"
        GenerationHandler[Generation Handler<br/>- Infographic Creation<br/>- Async Processing]
        NotificationHandler[Notification Handler<br/>- Status Updates<br/>- Completion Alerts]
    end
    
    UserRequest --> EventBridge
    ScheduledJob --> EventBridge
    WebhookTrigger --> EventBridge
    EventBridge --> SQS
    SQS --> GenerationHandler
    SQS --> NotificationHandler
```

### API Integration

```mermaid
graph TB
    subgraph "API Gateway"
        RestAPI[REST API<br/>- Synchronous Requests<br/>- Direct Response]
        GraphQLAPI[GraphQL API<br/>- Flexible Queries<br/>- Real-time Updates]
    end
    
    subgraph "Authentication"
        APIKey[API Key Auth<br/>- Simple Access Control<br/>- Rate Limiting]
        JWT[JWT Tokens<br/>- Stateless Auth<br/>- User Context]
    end
    
    subgraph "Rate Limiting"
        Throttling[Request Throttling<br/>- Per-User Limits<br/>- Burst Protection]
        Quotas[Usage Quotas<br/>- Monthly Limits<br/>- Billing Integration]
    end
    
    RestAPI --> APIKey
    GraphQLAPI --> JWT
    APIKey --> Throttling
    JWT --> Throttling
    Throttling --> Quotas
```

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | AWS Strands SDK | Multi-agent orchestration |
| **Language** | Python 3.12+ | Core application logic |
| **AI/ML** | Amazon Bedrock | Content analysis and reasoning |
| **Image Generation** | Amazon Nova Canvas | AI-powered image creation |
| **Image Processing** | PIL/Pillow | Image composition and manipulation |
| **Storage** | Amazon S3 | Asset storage and hosting |
| **Monitoring** | Amazon CloudWatch | Metrics, logs, and alerting |

### Development Tools

| Category | Tool | Purpose |
|----------|------|---------|
| **Package Management** | uv | Fast Python package management |
| **Testing** | pytest | Unit and integration testing |
| **Code Quality** | black, isort, mypy | Code formatting and type checking |
| **Documentation** | Sphinx | API documentation generation |
| **Containerization** | Docker | Application packaging |
| **Infrastructure** | AWS CDK | Infrastructure as Code |

### AWS Services Used

| Service | Usage | Configuration |
|---------|-------|---------------|
| **Amazon Bedrock** | Content analysis, layout intelligence | Claude 3.5 Sonnet model |
| **Amazon Nova Canvas** | AI image generation | Text-to-image generation |
| **Amazon S3** | Asset storage, output hosting | Bucket with public read access |
| **AWS Lambda** | Serverless execution (optional) | Python 3.12 runtime |
| **Amazon CloudWatch** | Monitoring and logging | Custom metrics and dashboards |
| **AWS IAM** | Access control | Least privilege policies |

This architecture provides a scalable, maintainable, and AWS-native solution for automated infographic generation using modern AI services and best practices.