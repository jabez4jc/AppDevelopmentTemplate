# Universal LLM Development Instructions

## 🎯 MANDATORY WORKFLOW FOR ALL DEVELOPMENT REQUESTS

When ANY development request is made for ANY application type, **AUTOMATICALLY** follow this workflow without being asked:

### 1. **ALWAYS Read Guidelines First** (Required)
```python
# Read these files in order before starting ANY development task:
required_files = [
    "DEV_GUIDELINES.md",           # Master development rulebook
    "PROJECT_TEMPLATE.md",         # Project-specific context
    "TESTING_GUIDE.md",            # Testing framework and procedures
    "LLM_REQUEST_TEMPLATE.md",     # Request format and workflow
    ".claude/project_context.md"   # Current project context
]
```

### 2. **ALWAYS Follow This Development Sequence** (Required)
1. ✅ **Read all guideline files** (DEV_GUIDELINES.md, PROJECT_TEMPLATE.md, TESTING_GUIDE.md)
2. ✅ **Understand project type** (web app, CLI, microservice, etc.)
3. ✅ **Plan the implementation** with TodoWrite tool
4. ✅ **Write tests FIRST** (Test-Driven Development)
5. ✅ **Implement the solution** following established patterns
6. ✅ **Run validation scripts**:
   - Code quality checks
   - Test execution
   - Security validation
   - Performance benchmarks
   - Documentation validation
7. ✅ **Test the implementation** thoroughly
8. ✅ **Update documentation** (happens automatically via git hooks)

### 3. **ALWAYS Use These Tools** (Required for all development)
- ✅ **TodoWrite**: Plan and track all development tasks
- ✅ **Read**: Always read guideline files first
- ✅ **Bash**: Run validation scripts and tests
- ✅ **Edit/MultiEdit**: Follow established code patterns
- ✅ **Validation Scripts**: Run before finalizing any changes

## 🔄 AUTOMATIC TRIGGERS

### When User Says ANY Of These:
- "Add [feature]"
- "Fix [issue]"  
- "Implement [functionality]"
- "Create [component]"
- "Update [system]"
- "Enhance [feature]"
- "Build [application]"
- "Set up [project]"
- "Follow project guidelines" (explicit trigger)

### AUTOMATICALLY Do This (No Questions Asked):
1. **Read DEV_GUIDELINES.md first**
2. **Read PROJECT_TEMPLATE.md for project context**  
3. **Read TESTING_GUIDE.md for testing requirements**
4. **Follow the mandatory development workflow above**
5. **Run all validation scripts**
6. **Create comprehensive tests**
7. **Update relevant documentation**

## 📋 UNIVERSAL REQUIREMENTS FOR ALL CODE CHANGES

### For Any New Function/Method:
```python
def new_function(param: str) -> dict:
    """Comprehensive docstring with type hints.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        SpecificError: When specific condition occurs
    """
    try:
        # Input validation - REQUIRED
        if not param or not isinstance(param, str):
            raise ValueError("Invalid parameter")
        
        # Implementation with error handling
        result = process_data(param)
        
        return {'success': True, 'data': result}
    except Exception as e:
        logger.error(f"Error in new_function: {e}")
        raise
```

### For Web API Endpoints:
```python
@app.route('/api/endpoint', methods=['POST'])
@authentication_required  # REQUIRED for protected resources
@rate_limit(requests_per_minute=60)  # REQUIRED for all public endpoints
@validate_json_schema(schema)  # REQUIRED input validation
def api_endpoint():
    """Complete docstring with API documentation."""
    try:
        # Input validation and sanitization
        data = sanitize_input(request.get_json())
        
        # Business logic in service layer
        result = service.process_request(data)
        
        return jsonify({'success': True, 'data': result})
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

### For CLI Commands:
```python
@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def process_command(input_file: str, output: str, verbose: bool):
    """Process input file and generate output.
    
    Args:
        input_file: Path to input file
        output: Optional output file path
        verbose: Enable verbose logging
    """
    try:
        # Input validation
        if not Path(input_file).exists():
            click.echo(f"Error: Input file not found: {input_file}", err=True)
            raise click.Abort()
        
        # Processing logic
        result = processor.process_file(input_file, verbose=verbose)
        
        # Output handling
        if output:
            with open(output, 'w') as f:
                f.write(result)
            click.echo(f"Output written to {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
```

## 🧪 MANDATORY TESTING REQUIREMENTS

### ALWAYS Create These Tests (Minimum):
1. **Unit tests** for all new functions/methods
2. **Integration tests** for component interactions  
3. **API tests** for web endpoints (if applicable)
4. **CLI tests** for command-line interfaces (if applicable)
5. **Security tests** for authentication/validation
6. **Performance tests** for response times

### Test Template Structure:
```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    """Test suite for new feature."""
    
    @pytest.fixture
    def setup_data(self):
        """Set up test data."""
        return {'test': 'data'}
    
    def test_positive_case(self, setup_data):
        """Test successful operation."""
        # Arrange
        expected_result = {'success': True}
        
        # Act
        result = new_feature.process(setup_data)
        
        # Assert
        assert result == expected_result
    
    def test_negative_case(self):
        """Test error handling."""
        with pytest.raises(ValidationError):
            new_feature.process(invalid_data)
    
    def test_edge_case(self):
        """Test edge case scenarios."""
        # Test with boundary conditions
        pass
    
    def test_performance(self):
        """Test performance requirements."""
        import time
        
        start_time = time.time()
        result = new_feature.process(large_dataset)
        duration = time.time() - start_time
        
        assert duration < 1.0  # Performance requirement
        assert result is not None
```

### ALWAYS Run These Before Finishing:
```bash
# Test execution
python tests/test_suite_runner.py --category all --coverage

# Code quality validation
python scripts/validate_code_quality.py

# Security validation
python scripts/validate_security.py

# Documentation validation
python scripts/validate_documentation.py
```

## 🔒 MANDATORY SECURITY REQUIREMENTS

### ALWAYS Include (No Exceptions):
- ✅ **Input validation** for all user inputs
- ✅ **Input sanitization** to prevent XSS/injection
- ✅ **Authentication checks** for protected resources
- ✅ **Authorization validation** for user permissions
- ✅ **Rate limiting** for public endpoints
- ✅ **Error handling** that doesn't expose sensitive data
- ✅ **Logging** that doesn't include sensitive information

### Security Validation Template:
```python
def validate_and_sanitize_input(data: dict) -> dict:
    """Validate and sanitize all user inputs."""
    import html
    import re
    
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # HTML escape to prevent XSS
            value = html.escape(value.strip())
            
            # Field-specific validation
            if key == 'email':
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value.lower()):
                    raise ValidationError(f"Invalid email format")
                value = value.lower()
            elif key.endswith('_id'):
                try:
                    value = int(value)
                    if value <= 0:
                        raise ValidationError(f"Invalid ID: {key}")
                except ValueError:
                    raise ValidationError(f"Invalid ID format: {key}")
        
        sanitized[key] = value
    
    return sanitized
```

## 🎯 APPLICATION TYPE SPECIFIC PATTERNS

### Web Applications (Flask/FastAPI/Django):
- Use service layer pattern for business logic
- Implement proper middleware for authentication
- Use database migrations for schema changes
- Include API documentation (OpenAPI/Swagger)
- Implement proper error handlers

### CLI Applications:
- Use Click or argparse for command structure
- Implement proper help documentation
- Include progress indicators for long operations
- Handle interrupts gracefully (Ctrl+C)
- Provide clear error messages

### Microservices:
- Implement health check endpoints
- Use proper service discovery patterns
- Include metrics and observability
- Implement circuit breaker patterns
- Use containerization (Docker)

### Data Processing Applications:
- Implement proper data validation
- Use streaming for large datasets
- Include data quality checks
- Implement proper error recovery
- Use appropriate data storage patterns

## 🔄 FRAMEWORK-SPECIFIC REQUIREMENTS

### Flask Applications:
```python
# Required structure
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Blueprint organization
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({'error': str(e)}), 400
```

### FastAPI Applications:
```python
# Required structure
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="Application API", version="1.0.0")

class RequestModel(BaseModel):
    """Request validation model."""
    field: str
    
@app.post("/api/endpoint")
async def endpoint(data: RequestModel, user = Depends(get_current_user)):
    """API endpoint with automatic documentation."""
    try:
        result = await service.process(data.dict())
        return {"success": True, "data": result}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Django Applications:
```python
# Required structure
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["POST"])
@login_required
@csrf_exempt
def api_endpoint(request):
    """Django API endpoint."""
    try:
        data = json.loads(request.body)
        validated_data = validate_input(data)
        result = service.process(validated_data)
        return JsonResponse({'success': True, 'data': result})
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
```

## 📊 PERFORMANCE REQUIREMENTS (Always Enforce)

### Response Time Limits by Application Type:
- **Web API endpoints**: < 500ms for 95th percentile
- **CLI commands**: < 2s for typical operations
- **Database queries**: < 100ms for common operations
- **File processing**: Progress indicators for >3s operations
- **Real-time features**: < 100ms latency

### Performance Testing Template:
```python
def test_performance_requirement(self):
    """Test that feature meets performance requirements."""
    import time
    
    # Test multiple iterations for statistical significance
    times = []
    for _ in range(10):
        start_time = time.time()
        result = feature_function()
        duration = time.time() - start_time
        times.append(duration)
        assert result is not None
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    assert avg_time < 0.5, f"Average time {avg_time:.3f}s exceeds 500ms limit"
    assert max_time < 1.0, f"Max time {max_time:.3f}s exceeds 1s limit"
```

## 🚫 COMMON PITFALLS TO AVOID (Always Check)

### ❌ NEVER Do These:
- Put business logic in controllers/routes
- Skip input validation
- Ignore error handling
- Skip writing tests
- Skip running validation scripts
- Break backward compatibility
- Store plaintext secrets
- Commit sensitive data
- Use global variables for state
- Skip documentation

### ✅ ALWAYS Do These:
- Follow separation of concerns
- Validate and sanitize all inputs
- Handle all errors gracefully
- Write comprehensive tests first
- Run all validation scripts
- Maintain backward compatibility  
- Encrypt sensitive data
- Use proper logging
- Follow dependency injection patterns
- Update documentation automatically

## 🎯 PROJECT SETUP AUTOMATION

### For New Projects:
```python
# Automatically detect project type and apply appropriate patterns
def setup_project_structure(project_type: str, framework: str = None):
    """Set up project structure based on type and framework."""
    
    if project_type == 'web':
        setup_web_project(framework)
    elif project_type == 'cli':
        setup_cli_project()
    elif project_type == 'microservice':
        setup_microservice_project(framework)
    elif project_type == 'data':
        setup_data_project()
    
    # Always include these
    setup_testing_framework()
    setup_documentation_system()
    setup_git_hooks()
    setup_ci_cd()
```

## 🎭 MAGIC KEYWORDS AND AUTOMATIC BEHAVIOR

### When user includes ANY of these in their request, AUTOMATICALLY follow the full workflow:

**Direct Triggers:**
- "Follow project guidelines"
- "Use the development template"
- "Apply best practices"
- "Follow the established patterns"
- "Update documentation"

**Implicit Triggers (ANY development request):**
- "Create/Add/Build/Implement/Develop [anything]"
- "Fix/Resolve/Debug [anything]"
- "Enhance/Improve/Optimize [anything]"
- "Set up/Configure/Initialize [anything]"

## 🏆 SUCCESS CRITERIA

Every development task must achieve:
- ✅ All existing tests continue to pass
- ✅ New comprehensive tests cover new functionality
- ✅ >95% code coverage maintained
- ✅ All validation scripts pass
- ✅ Performance requirements met
- ✅ Security requirements met
- ✅ Documentation automatically updated
- ✅ No breaking changes introduced
- ✅ Code follows established patterns
- ✅ Error handling is comprehensive

## 💫 THE ULTIMATE GOAL

**Make professional-grade development so systematic and automated that users get perfect, production-ready implementations every time, with all testing, documentation, and quality assurance handled automatically, regardless of application type or complexity.**

**The workflow should happen AUTOMATICALLY for any development request, even if the user doesn't explicitly ask for it. The goal is to make enterprise-quality development the default behavior for ANY type of application.**

---

**Remember**: This workflow should adapt to the specific application type while maintaining universal quality standards. Whether it's a web app, CLI tool, microservice, or data processing application, the same rigorous standards apply automatically.