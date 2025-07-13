# Universal LLM Request Template

## 🎯 How to Make Development Requests for Any Application

This template ensures all development requests trigger the comprehensive quality workflow, regardless of application type or complexity.

## 📋 Universal Request Format

### Basic Structure
```
[TASK TYPE]: [Brief Description]

[Detailed requirements and context]

Follow project guidelines and update all relevant documentation.
```

### Task Types (Universal)
- **FEATURE**: Add new functionality
- **FIX**: Bug fixes and issue resolution  
- **ENHANCE**: Improve existing functionality
- **REFACTOR**: Code restructuring and optimization
- **SECURITY**: Security improvements and fixes
- **TEST**: Add or improve test coverage
- **API**: New or modified API endpoints (web apps)
- **CLI**: Command-line interface additions (CLI apps)
- **SETUP**: Project initialization and configuration
- **DOCS**: Documentation improvements
- **DEPLOY**: Deployment and infrastructure
- **PERFORMANCE**: Performance optimizations

## 🔄 What Happens Automatically

When you make requests following this format, the LLM will automatically:

### 1. **Read All Guidelines** (Always)
- ✅ DEV_GUIDELINES.md (universal development standards)
- ✅ PROJECT_TEMPLATE.md (project-specific context)
- ✅ TESTING_GUIDE.md (comprehensive testing requirements)
- ✅ .claude/project_context.md (current project state)

### 2. **Follow Complete Workflow** (Always)
- ✅ Plan implementation with TodoWrite
- ✅ Write tests FIRST (Test-Driven Development)
- ✅ Implement following established patterns
- ✅ Run all validation scripts
- ✅ Test implementation thoroughly
- ✅ Update documentation automatically

### 3. **Apply Quality Standards** (Always)
- ✅ >95% test coverage
- ✅ Security validation
- ✅ Performance requirements
- ✅ Error handling
- ✅ Input validation
- ✅ Documentation updates

## 📝 Request Examples by Application Type

### Web Application Requests

#### ✅ API Development
```
API: Add user authentication endpoints

I need to implement user registration and login functionality with:
- POST /api/auth/register - User registration with email verification
- POST /api/auth/login - User login with JWT token response
- POST /api/auth/refresh - Token refresh mechanism
- POST /api/auth/logout - User logout

Requirements:
- Password strength validation
- Rate limiting for security
- Comprehensive error handling
- Integration with existing user model

Follow project guidelines and update all relevant documentation.
```

#### ✅ Frontend Feature
```
FEATURE: Real-time dashboard with WebSocket updates

Create a dashboard that displays live data updates using WebSocket connections:
- Real-time metrics display
- Auto-refreshing charts and graphs
- Connection status indicators
- Graceful fallback to polling if WebSocket fails

Technical requirements:
- Socket.IO integration
- Responsive design with Tailwind CSS
- Error handling for connection issues
- Performance optimization for frequent updates

Follow project guidelines and update all relevant documentation.
```

### CLI Application Requests

#### ✅ Command Addition
```
CLI: Add data processing command with progress tracking

Implement a new command that processes large datasets:
- Command: myapp process --input file.csv --output result.json
- Progress bar for long operations
- Validation of input file format
- Detailed error messages
- Option for verbose logging

Requirements:
- Use Click framework patterns
- Handle interruption gracefully (Ctrl+C)
- Memory-efficient processing for large files
- Comprehensive help documentation

Follow project guidelines and update all relevant documentation.
```

#### ✅ Configuration Feature
```
FEATURE: Configuration management system

Add configuration file support with:
- YAML/JSON configuration files
- Environment variable overrides
- Configuration validation
- Default configuration generation
- Config file location detection (~/.myapp/config.yaml)

Features needed:
- config init command to create default config
- config validate command to check configuration
- config show command to display current settings
- Integration with existing CLI commands

Follow project guidelines and update all relevant documentation.
```

### Microservice Requests

#### ✅ Service Development
```
FEATURE: User notification microservice

Create a standalone microservice for handling notifications:
- RESTful API for sending notifications
- Support for email, SMS, and push notifications
- Queue-based processing for reliability
- Health check and metrics endpoints

Technical requirements:
- FastAPI or Flask framework
- Redis/RabbitMQ for message queuing
- Docker containerization
- OpenAPI documentation
- Circuit breaker patterns for external services

Follow project guidelines and update all relevant documentation.
```

#### ✅ Integration Enhancement
```
ENHANCE: Add service discovery and load balancing

Implement service discovery for microservice communication:
- Service registration and discovery
- Health monitoring and auto-removal of unhealthy services
- Load balancing between service instances
- Circuit breaker for fault tolerance

Requirements:
- Consul or etcd for service discovery
- Health check endpoints for all services
- Automatic failover mechanisms
- Monitoring and alerting integration

Follow project guidelines and update all relevant documentation.
```

### Data Processing Requests

#### ✅ ETL Pipeline
```
FEATURE: Data ingestion pipeline with validation

Build a robust data processing pipeline:
- Ingest data from multiple sources (API, files, databases)
- Data validation and quality checks
- Transformation and normalization
- Error handling and retry mechanisms
- Progress tracking and logging

Technical requirements:
- Support for CSV, JSON, Parquet formats
- Schema validation for incoming data
- Incremental processing capabilities
- Dead letter queue for failed records
- Monitoring and alerting for pipeline health

Follow project guidelines and update all relevant documentation.
```

### Mobile/Desktop Application Requests

#### ✅ Desktop Application
```
FEATURE: Cross-platform desktop application

Create a desktop application with native feel:
- Electron or Tauri framework
- Local data storage with SQLite
- File system integration
- System tray functionality
- Auto-updater mechanism

Requirements:
- Responsive UI that works on different screen sizes
- Offline functionality with sync when online
- Security for local data storage
- Performance optimization for large datasets
- Platform-specific UI guidelines compliance

Follow project guidelines and update all relevant documentation.
```

## 🪄 Magic Phrases (Automatic Triggers)

### Guaranteed Full Workflow Trigger
```
"Follow project guidelines and update all relevant documentation."
```

### Alternative Triggers (Also Work)
- "Apply best practices and maintain code quality"
- "Use the established development patterns"
- "Follow the template standards"
- "Implement with comprehensive testing"
- "Build with production-ready quality"

## 🎯 Advanced Request Patterns

### Complex Multi-Component Feature
```
FEATURE: Complete user management system

Implement a comprehensive user management system with:

Backend Components:
- User authentication and authorization
- Role-based access control (RBAC)
- User profile management
- Password reset functionality
- Account activation via email

Frontend Components:
- User registration and login forms
- User profile editing interface
- Admin panel for user management
- Password strength indicators
- Real-time form validation

Infrastructure:
- Database migrations for user tables
- Email service integration
- Security audit logging
- Rate limiting and DDoS protection

Follow project guidelines and update all relevant documentation.

This is a complex feature - please plan the implementation phases and 
confirm the architecture before starting development.
```

### Security-Critical Request
```
SECURITY: Implement comprehensive authentication security

Enhance the application's authentication system with:
- Multi-factor authentication (MFA)
- OAuth2/OIDC integration  
- Session management improvements
- Brute force protection
- Security audit logging

Security requirements:
- OWASP compliance for authentication
- Secure password storage (bcrypt/Argon2)
- JWT token security best practices
- Protection against timing attacks
- Comprehensive security testing

Follow project guidelines and update all relevant documentation.

This is security-critical - ensure comprehensive testing and security 
validation before deployment.
```

### Performance-Critical Request
```
PERFORMANCE: Optimize database queries and caching

Improve application performance through:
- Database query optimization
- Implement Redis caching layer
- Add database connection pooling
- Optimize ORM queries
- Add performance monitoring

Performance targets:
- API response times < 200ms for 95th percentile
- Database query times < 50ms average
- Cache hit ratio > 80%
- Memory usage optimization
- Concurrent user support for 1000+ users

Follow project guidelines and update all relevant documentation.

Performance is critical - include comprehensive benchmarking and 
load testing in the implementation.
```

## 🔄 Project Type Detection

The template automatically adapts based on project context:

### Web Application Context
- Focuses on API endpoints, authentication, frontend components
- Includes security considerations for web vulnerabilities
- Emphasizes responsive design and user experience

### CLI Application Context  
- Focuses on command structure, help documentation, progress indicators
- Includes considerations for different operating systems
- Emphasizes user-friendly command-line interface

### Microservice Context
- Focuses on service boundaries, API design, deployment
- Includes considerations for distributed systems patterns
- Emphasizes observability and fault tolerance

### Data Processing Context
- Focuses on data validation, transformation, performance
- Includes considerations for large datasets and streaming
- Emphasizes data quality and pipeline reliability

## 📊 Request Quality Metrics

### ✅ Good Request Characteristics
- **Clear task type** (FEATURE, FIX, ENHANCE, etc.)
- **Specific requirements** with technical details
- **Context provided** for the change
- **Success criteria** defined
- **Magic phrase included** for full workflow

### ❌ Requests to Improve
```
"Make the app better"
→ Too vague, no specific requirements

"Add some features"
→ No clear scope or specifications

"Fix bugs"
→ No specific bugs identified

"Update documentation"
→ No context about what needs updating
```

### ✅ Improved Versions
```
ENHANCE: Improve user onboarding experience
- Add interactive tutorial for new users
- Create step-by-step wizard for initial setup
- Include helpful tooltips and hints
- Add progress indicators for multi-step processes
Follow project guidelines and update all relevant documentation.
```

## 🚀 Getting Started with Any Project Type

### First Request for New Projects
```
SETUP: Initialize [project_type] application with template standards

Create a new [web app/CLI tool/microservice/data processor] with:
- Project structure following template guidelines
- Testing framework setup
- Documentation system initialization
- Git hooks and validation scripts
- CI/CD pipeline configuration

Application-specific requirements:
[Add your specific needs here]

Follow project guidelines and update all relevant documentation.
```

### Subsequent Development Requests
Use the patterns above based on your application type, always including the magic phrase to ensure comprehensive quality standards are applied automatically.

## 🎯 Success Guarantee

Using this request format guarantees:
- **Enterprise-quality code** following all best practices
- **Comprehensive testing** with >95% coverage
- **Security validation** against common vulnerabilities
- **Performance optimization** meeting specified requirements
- **Documentation updates** automatically maintained
- **Error handling** for all edge cases
- **Backward compatibility** preserved

**The template ensures that every development request, regardless of complexity or application type, results in production-ready, maintainable, and well-documented code.**