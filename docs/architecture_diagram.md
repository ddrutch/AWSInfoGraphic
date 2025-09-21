# AWS Infographic Generator - Architecture Diagrams

This document contains comprehensive architecture diagrams for the AWS Infographic Generator system.

## System Overview Diagram

```mermaid
graph TB
    %% User Interface Layer
    subgraph "User Interface Layer"
        User[👤 User]
        CLI[🖥️ CLI Interface]
        API[🌐 REST API]
        WebUI[🌍 Web Interface]
    end
    
    %% Application Layer
    subgraph "Application Layer"
        Orchestrator[🎯 InfographicOrchestrator<br/>Main Workflow Controller]
        
        subgraph "Specialized Agents"
            ContentAgent[📝 ContentAnalyzer<br/>Text Analysis & Structure]
            ImageAgent[🖼️ ImageSourcer<br/>Image Generation & Sourcing]
            LayoutAgent[🎨 DesignLayout<br/>Visual Layout Design]
            TextAgent[✍️ TextFormatter<br/>Typography & Styling]
            ComposerAgent[🖌️ ImageComposer<br/>Final Image Creation]
        end
        
        subgraph "Tool Layer"
            ContentTools[📊 Content Tools]
            ImageTools[🛠️ Image Tools]
            LayoutTools[📐 Layout Tools]
            TextTools[🔤 Text Tools]
            S3Tools[📦 S3 Tools]
            BedrockTools[🔧 Bedrock Tools]
        end
    end
    
    %% AWS Services Layer
    subgraph "AWS Services"
        subgraph "AI/ML Services"
            Bedrock[🧠 Amazon Bedrock<br/>Claude 3.5 Sonnet]
            NovaCanvas[🎨 Amazon Nova Canvas<br/>Image Generation]
        end
        
        subgraph "Storage Services"
            S3[📦 Amazon S3<br/>Asset Storage & Hosting]
        end
        
        subgraph "Monitoring Services"
            CloudWatch[📊 Amazon CloudWatch<br/>Metrics & Logs]
            XRay[🔍 AWS X-Ray<br/>Distributed Tracing]
        end
    end
    
    %% Data Processing Layer
    subgraph "Data Processing"
        PIL[🖼️ PIL/Pillow<br/>Image Processing]
        Cache[💾 In-Memory Cache<br/>Performance Optimization]
    end
    
    %% Output Layer
    subgraph "Output Formats"
        WhatsApp[📱 WhatsApp<br/>1080x1080]
        Twitter[🐦 Twitter<br/>1200x675]
        Discord[💬 Discord<br/>1920x1080]
        General[🌐 General<br/>1920x1080]
    end
    
    %% Connections
    User --> CLI
    User --> API
    User --> WebUI
    
    CLI --> Orchestrator
    API --> Orchestrator
    WebUI --> Orchestrator
    
    Orchestrator --> ContentAgent
    Orchestrator --> ImageAgent
    Orchestrator --> LayoutAgent
    Orchestrator --> TextAgent
    Orchestrator --> ComposerAgent
    
    ContentAgent --> ContentTools
    ImageAgent --> ImageTools
    LayoutAgent --> LayoutTools
    TextAgent --> TextTools
    ComposerAgent --> S3Tools
    
    ContentTools --> BedrockTools
    ImageTools --> BedrockTools
    S3Tools --> BedrockTools
    
    BedrockTools --> Bedrock
    ImageTools --> NovaCanvas
    S3Tools --> S3
    
    ComposerAgent --> PIL
    ImageAgent --> Cache
    
    Orchestrator --> CloudWatch
    Orchestrator --> XRay
    
    ComposerAgent --> WhatsApp
    ComposerAgent --> Twitter
    ComposerAgent --> Discord
    ComposerAgent --> General
    
    %% Styling
    classDef userLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef appLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef agentLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef toolLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef awsLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dataLayer fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef outputLayer fill:#f5f5f5,stroke:#424242,stroke-width:2px
    
    class User,CLI,API,WebUI userLayer
    class Orchestrator appLayer
    class ContentAgent,ImageAgent,LayoutAgent,TextAgent,ComposerAgent agentLayer
    class ContentTools,ImageTools,LayoutTools,TextTools,S3Tools,BedrockTools toolLayer
    class Bedrock,NovaCanvas,S3,CloudWatch,XRay awsLayer
    class PIL,Cache dataLayer
    class WhatsApp,Twitter,Discord,General outputLayer
```

## Data Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant CA as ContentAnalyzer
    participant IS as ImageSourcer
    participant DL as DesignLayout
    participant TF as TextFormatter
    participant IC as ImageComposer
    participant B as Amazon Bedrock
    participant NC as Nova Canvas
    participant S3 as Amazon S3
    participant CW as CloudWatch
    
    Note over U,CW: Infographic Generation Workflow
    
    U->>O: Generate infographic request
    O->>CW: Log request start
    
    Note over O,CA: Phase 1: Content Analysis
    O->>CA: Analyze content structure
    CA->>B: Extract key points & topics
    B-->>CA: Structured content analysis
    CA-->>O: ContentAnalysis result
    O->>CW: Log content analysis metrics
    
    Note over O,IS: Phase 2: Image Sourcing
    O->>IS: Source/generate images
    IS->>NC: Generate relevant images
    NC-->>IS: Generated image data
    IS->>S3: Cache generated images
    S3-->>IS: Image URLs
    IS-->>O: ImageAsset list
    O->>CW: Log image generation metrics
    
    Note over O,DL: Phase 3: Layout Design
    O->>DL: Create visual layout
    DL->>B: Optimize layout for platform
    B-->>DL: Layout recommendations
    DL-->>O: LayoutSpecification
    O->>CW: Log layout creation metrics
    
    Note over O,TF: Phase 4: Text Formatting
    O->>TF: Format text elements
    TF-->>O: FormattedText list
    O->>CW: Log text formatting metrics
    
    Note over O,IC: Phase 5: Image Composition
    O->>IC: Compose final infographic
    IC->>S3: Download cached images
    S3-->>IC: Image data
    IC->>IC: Composite using PIL/Pillow
    IC->>S3: Upload final infographic
    S3-->>IC: Public URL
    IC-->>O: InfographicResult
    O->>CW: Log final generation metrics
    
    O-->>U: Generated infographic URL
    
    Note over U,CW: End-to-End Generation Complete
```

## AWS Services Integration Architecture

```mermaid
graph TB
    subgraph "Application Tier"
        App[AWS Infographic Generator<br/>Python Application]
    end
    
    subgraph "AWS AI/ML Services"
        Bedrock[Amazon Bedrock<br/>Foundation Models]
        BedrockModels[Claude 3.5 Sonnet<br/>Nova Canvas]
        
        Bedrock --> BedrockModels
    end
    
    subgraph "AWS Storage Services"
        S3[Amazon S3<br/>Object Storage]
        S3Buckets[Asset Cache Bucket<br/>Output Bucket<br/>Temp Bucket]
        
        S3 --> S3Buckets
    end
    
    subgraph "AWS Compute Services"
        Lambda[AWS Lambda<br/>Serverless Functions]
        ECS[Amazon ECS<br/>Container Service]
        EC2[Amazon EC2<br/>Virtual Machines]
    end
    
    subgraph "AWS Monitoring & Logging"
        CloudWatch[Amazon CloudWatch<br/>Metrics & Logs]
        XRay[AWS X-Ray<br/>Distributed Tracing]
        CloudTrail[AWS CloudTrail<br/>API Audit Logs]
    end
    
    subgraph "AWS Security Services"
        IAM[AWS IAM<br/>Identity & Access Management]
        KMS[AWS KMS<br/>Key Management Service]
        VPC[Amazon VPC<br/>Network Isolation]
    end
    
    subgraph "AWS Developer Tools"
        CodeBuild[AWS CodeBuild<br/>Build Service]
        CodeDeploy[AWS CodeDeploy<br/>Deployment Service]
        ECR[Amazon ECR<br/>Container Registry]
    end
    
    %% Application connections
    App --> Bedrock
    App --> S3
    App --> CloudWatch
    App --> XRay
    
    %% Compute options
    App -.-> Lambda
    App -.-> ECS
    App -.-> EC2
    
    %% Security integration
    App --> IAM
    S3 --> KMS
    App --> VPC
    
    %% Monitoring integration
    Lambda --> CloudWatch
    ECS --> CloudWatch
    EC2 --> CloudWatch
    
    %% Audit logging
    Bedrock --> CloudTrail
    S3 --> CloudTrail
    IAM --> CloudTrail
    
    %% Development pipeline
    CodeBuild --> ECR
    ECR --> ECS
    CodeDeploy --> ECS
    CodeDeploy --> Lambda
    
    %% Styling
    classDef appTier fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef aiServices fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef storageServices fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef computeServices fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef monitoringServices fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef securityServices fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef devServices fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class App appTier
    class Bedrock,BedrockModels aiServices
    class S3,S3Buckets storageServices
    class Lambda,ECS,EC2 computeServices
    class CloudWatch,XRay,CloudTrail monitoringServices
    class IAM,KMS,VPC securityServices
    class CodeBuild,CodeDeploy,ECR devServices
```

## Security Architecture Diagram

```mermaid
graph TB
    subgraph "External Access"
        Internet[🌐 Internet]
        Users[👥 Users]
    end
    
    subgraph "AWS Security Perimeter"
        subgraph "Network Security"
            WAF[🛡️ AWS WAF<br/>Web Application Firewall]
            ALB[⚖️ Application Load Balancer<br/>SSL Termination]
            VPC[🏠 Amazon VPC<br/>Network Isolation]
            
            subgraph "Private Subnets"
                ECS[📦 ECS Tasks<br/>Application Containers]
                Lambda[⚡ Lambda Functions<br/>Serverless Compute]
            end
            
            subgraph "Security Groups"
                SGALB[🔒 ALB Security Group<br/>HTTPS Only]
                SGECS[🔒 ECS Security Group<br/>Internal Traffic]
            end
        end
        
        subgraph "Identity & Access Management"
            IAM[👤 AWS IAM<br/>Identity Management]
            
            subgraph "IAM Roles"
                ECSRole[🎭 ECS Task Role<br/>Bedrock + S3 Access]
                LambdaRole[🎭 Lambda Execution Role<br/>Limited Permissions]
            end
            
            subgraph "IAM Policies"
                BedrockPolicy[📋 Bedrock Access Policy<br/>Model Invocation Only]
                S3Policy[📋 S3 Access Policy<br/>Bucket-Specific Access]
            end
        end
        
        subgraph "Data Protection"
            KMS[🔐 AWS KMS<br/>Encryption Key Management]
            
            subgraph "Encryption"
                S3Encryption[🔒 S3 Server-Side Encryption<br/>AES-256 / KMS]
                TransitEncryption[🔒 TLS 1.2+ Encryption<br/>Data in Transit]
            end
        end
        
        subgraph "Monitoring & Compliance"
            CloudTrail[📊 AWS CloudTrail<br/>API Audit Logging]
            Config[⚙️ AWS Config<br/>Compliance Monitoring]
            GuardDuty[🛡️ Amazon GuardDuty<br/>Threat Detection]
            
            subgraph "Logging"
                CloudWatchLogs[📝 CloudWatch Logs<br/>Application Logs]
                VPCFlowLogs[🌊 VPC Flow Logs<br/>Network Traffic]
            end
        end
    end
    
    subgraph "AWS Services"
        Bedrock[🧠 Amazon Bedrock<br/>Foundation Models]
        S3[📦 Amazon S3<br/>Encrypted Storage]
        CloudWatch[📊 Amazon CloudWatch<br/>Metrics & Monitoring]
    end
    
    %% External connections
    Users --> Internet
    Internet --> WAF
    
    %% Network flow
    WAF --> ALB
    ALB --> VPC
    VPC --> ECS
    VPC --> Lambda
    
    %% Security group associations
    ALB -.-> SGALB
    ECS -.-> SGECS
    
    %% IAM associations
    ECS --> ECSRole
    Lambda --> LambdaRole
    ECSRole --> BedrockPolicy
    ECSRole --> S3Policy
    LambdaRole --> S3Policy
    
    %% Service access
    ECS --> Bedrock
    ECS --> S3
    Lambda --> S3
    ECS --> CloudWatch
    Lambda --> CloudWatch
    
    %% Encryption
    S3 --> S3Encryption
    S3Encryption --> KMS
    ALB --> TransitEncryption
    
    %% Monitoring
    ECS --> CloudWatchLogs
    VPC --> VPCFlowLogs
    Bedrock --> CloudTrail
    S3 --> CloudTrail
    IAM --> CloudTrail
    VPC --> Config
    VPC --> GuardDuty
    
    %% Styling
    classDef external fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    classDef network fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef security fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef encryption fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef monitoring fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef services fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class Internet,Users external
    class WAF,ALB,VPC,ECS,Lambda,SGALB,SGECS network
    class IAM,ECSRole,LambdaRole,BedrockPolicy,S3Policy security
    class KMS,S3Encryption,TransitEncryption encryption
    class CloudTrail,Config,GuardDuty,CloudWatchLogs,VPCFlowLogs monitoring
    class Bedrock,S3,CloudWatch services
```

## Deployment Architecture Options

### Option 1: Serverless Deployment

```mermaid
graph TB
    subgraph "Serverless Architecture"
        subgraph "API Gateway"
            APIGW[🌐 Amazon API Gateway<br/>REST API Endpoints]
        end
        
        subgraph "Compute Layer"
            LambdaOrchestrator[⚡ Lambda Function<br/>Orchestrator]
            LambdaContent[⚡ Lambda Function<br/>Content Analyzer]
            LambdaImage[⚡ Lambda Function<br/>Image Sourcer]
            LambdaLayout[⚡ Lambda Function<br/>Layout Designer]
            LambdaComposer[⚡ Lambda Function<br/>Image Composer]
        end
        
        subgraph "Event Processing"
            SQS[📬 Amazon SQS<br/>Task Queue]
            EventBridge[🎯 Amazon EventBridge<br/>Event Routing]
        end
        
        subgraph "Storage & Services"
            S3[📦 Amazon S3<br/>Asset Storage]
            Bedrock[🧠 Amazon Bedrock<br/>AI Models]
            DynamoDB[🗄️ Amazon DynamoDB<br/>State Management]
        end
        
        subgraph "Monitoring"
            CloudWatch[📊 CloudWatch<br/>Logs & Metrics]
            XRay[🔍 X-Ray<br/>Tracing]
        end
    end
    
    %% API flow
    APIGW --> LambdaOrchestrator
    
    %% Event-driven processing
    LambdaOrchestrator --> EventBridge
    EventBridge --> SQS
    SQS --> LambdaContent
    SQS --> LambdaImage
    SQS --> LambdaLayout
    SQS --> LambdaComposer
    
    %% Service connections
    LambdaContent --> Bedrock
    LambdaImage --> Bedrock
    LambdaLayout --> Bedrock
    LambdaComposer --> S3
    LambdaOrchestrator --> DynamoDB
    
    %% Monitoring
    LambdaOrchestrator --> CloudWatch
    LambdaContent --> XRay
    LambdaImage --> XRay
    LambdaLayout --> XRay
    LambdaComposer --> XRay
    
    classDef serverless fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class APIGW,LambdaOrchestrator,LambdaContent,LambdaImage,LambdaLayout,LambdaComposer,SQS,EventBridge serverless
```

### Option 2: Container Deployment

```mermaid
graph TB
    subgraph "Container Architecture"
        subgraph "Load Balancing"
            ALB[⚖️ Application Load Balancer<br/>Traffic Distribution]
        end
        
        subgraph "ECS Cluster"
            subgraph "ECS Services"
                OrchService[📦 Orchestrator Service<br/>2 Tasks]
                ContentService[📦 Content Service<br/>3 Tasks]
                ImageService[📦 Image Service<br/>2 Tasks]
                LayoutService[📦 Layout Service<br/>2 Tasks]
                ComposerService[📦 Composer Service<br/>1 Task]
            end
            
            subgraph "Auto Scaling"
                ASG[📈 Auto Scaling Group<br/>CPU/Memory Based]
            end
        end
        
        subgraph "Service Discovery"
            ServiceDiscovery[🔍 AWS Cloud Map<br/>Service Registry]
        end
        
        subgraph "Container Registry"
            ECR[📦 Amazon ECR<br/>Container Images]
        end
        
        subgraph "Storage & Services"
            S3[📦 Amazon S3<br/>Asset Storage]
            Bedrock[🧠 Amazon Bedrock<br/>AI Models]
            ElastiCache[⚡ Amazon ElastiCache<br/>Redis Cache]
        end
        
        subgraph "Monitoring"
            CloudWatch[📊 CloudWatch<br/>Container Insights]
            XRay[🔍 X-Ray<br/>Distributed Tracing]
        end
    end
    
    %% Load balancing
    ALB --> OrchService
    
    %% Service communication
    OrchService --> ContentService
    OrchService --> ImageService
    OrchService --> LayoutService
    OrchService --> ComposerService
    
    %% Service discovery
    OrchService -.-> ServiceDiscovery
    ContentService -.-> ServiceDiscovery
    ImageService -.-> ServiceDiscovery
    LayoutService -.-> ServiceDiscovery
    ComposerService -.-> ServiceDiscovery
    
    %% Auto scaling
    OrchService --> ASG
    ContentService --> ASG
    ImageService --> ASG
    LayoutService --> ASG
    ComposerService --> ASG
    
    %% Container registry
    OrchService -.-> ECR
    ContentService -.-> ECR
    ImageService -.-> ECR
    LayoutService -.-> ECR
    ComposerService -.-> ECR
    
    %% Service connections
    ContentService --> Bedrock
    ImageService --> Bedrock
    LayoutService --> Bedrock
    ComposerService --> S3
    ImageService --> ElastiCache
    
    %% Monitoring
    OrchService --> CloudWatch
    ContentService --> XRay
    ImageService --> XRay
    LayoutService --> XRay
    ComposerService --> XRay
    
    classDef container fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    class ALB,OrchService,ContentService,ImageService,LayoutService,ComposerService,ASG,ServiceDiscovery,ECR container
```

## Performance and Scaling Architecture

```mermaid
graph TB
    subgraph "Performance Optimization"
        subgraph "Caching Layers"
            CDN[🌐 Amazon CloudFront<br/>Global CDN]
            ElastiCache[⚡ Amazon ElastiCache<br/>Redis Cache]
            S3Cache[📦 S3 Cache Bucket<br/>Generated Assets]
            MemoryCache[💾 In-Memory Cache<br/>Application Level]
        end
        
        subgraph "Load Distribution"
            ALB[⚖️ Application Load Balancer<br/>Multi-AZ Distribution]
            
            subgraph "Auto Scaling Groups"
                ASGOrch[📈 Orchestrator ASG<br/>2-10 instances]
                ASGWorkers[📈 Worker ASG<br/>5-20 instances]
            end
        end
        
        subgraph "Processing Optimization"
            SQS[📬 Amazon SQS<br/>Task Distribution]
            
            subgraph "Worker Types"
                ContentWorkers[👷 Content Workers<br/>CPU Optimized]
                ImageWorkers[👷 Image Workers<br/>Memory Optimized]
                ComposerWorkers[👷 Composer Workers<br/>GPU Optimized]
            end
        end
        
        subgraph "Data Optimization"
            S3IA[📦 S3 Intelligent Tiering<br/>Cost Optimization]
            S3Transfer[🚀 S3 Transfer Acceleration<br/>Global Upload Speed]
            
            subgraph "Database Optimization"
                DynamoDAX[⚡ DynamoDB + DAX<br/>Microsecond Latency]
                RDSReadReplicas[🗄️ RDS Read Replicas<br/>Read Scaling]
            end
        end
        
        subgraph "Monitoring & Optimization"
            CloudWatch[📊 CloudWatch<br/>Performance Metrics]
            
            subgraph "Performance Insights"
                AppInsights[📈 Application Insights<br/>Performance Analysis]
                CostOptimizer[💰 Cost Optimizer<br/>Resource Right-sizing]
            end
        end
    end
    
    %% Traffic flow
    CDN --> ALB
    ALB --> ASGOrch
    ASGOrch --> SQS
    
    %% Worker distribution
    SQS --> ContentWorkers
    SQS --> ImageWorkers
    SQS --> ComposerWorkers
    
    %% Caching hierarchy
    ContentWorkers --> MemoryCache
    ImageWorkers --> ElastiCache
    ComposerWorkers --> S3Cache
    S3Cache --> CDN
    
    %% Auto scaling
    ASGOrch --> ASGWorkers
    ContentWorkers -.-> ASGWorkers
    ImageWorkers -.-> ASGWorkers
    ComposerWorkers -.-> ASGWorkers
    
    %% Data access optimization
    ContentWorkers --> DynamoDAX
    ImageWorkers --> S3Transfer
    ComposerWorkers --> S3IA
    ASGOrch --> RDSReadReplicas
    
    %% Monitoring
    ASGOrch --> CloudWatch
    ContentWorkers --> AppInsights
    ImageWorkers --> AppInsights
    ComposerWorkers --> CostOptimizer
    
    classDef performance fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef scaling fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef optimization fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef monitoring fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    
    class CDN,ElastiCache,S3Cache,MemoryCache performance
    class ALB,ASGOrch,ASGWorkers,SQS,ContentWorkers,ImageWorkers,ComposerWorkers scaling
    class S3IA,S3Transfer,DynamoDAX,RDSReadReplicas optimization
    class CloudWatch,AppInsights,CostOptimizer monitoring
```

These architecture diagrams provide comprehensive visual documentation of the AWS Infographic Generator system, covering system overview, data flow, AWS services integration, security, deployment options, and performance optimization strategies.