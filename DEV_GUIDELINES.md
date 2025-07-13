# Universal Application Development Guidelines

This document provides comprehensive guidelines for LLMs and developers when building any application using this template. Following these guidelines ensures robustness, maintains test coverage, and prevents breaking changes across all project types.

## 🎯 Core Principles

### 1. **Test-Driven Development (TDD)**
- Write tests BEFORE implementing functionality
- Every new feature must have corresponding tests
- All existing tests must continue to pass
- Aim for 95%+ test coverage
- Test categories: Unit, Integration, Security, Performance

### 2. **Security First**
- All user-facing operations require proper validation
- Validate and sanitize all inputs before processing
- Implement rate limiting for public endpoints
- Never log sensitive data (passwords, API keys, personal info)
- Use parameterized queries to prevent injection attacks

### 3. **Backward Compatibility**
- Never break existing API contracts without versioning
- Database changes must be reversible with migration scripts
- Maintain support for existing configurations
- Document any breaking changes clearly with migration paths

### 4. **Performance Standards**
- API responses: <500ms for 95th percentile
- Database queries: <100ms for common operations
- Page loads: <2000ms for web applications
- Memory usage: Monitor and prevent leaks
- CPU usage: Optimize hot paths

## 🏗️ Architecture Patterns

### Service Layer Pattern
All business logic goes in services, not in routes/controllers:

```python
# ✅ CORRECT: Business logic in service
@app.route('/api/process-data', methods=['POST'])
@authentication_required
def process_data():
    data = request.get_json()
    result = data_service.process_user_data(
        user_id=get_current_user_id(),
        data=data
    )
    return jsonify(result)

# ❌ INCORRECT: Business logic in route
@app.route('/api/process-data', methods=['POST'])
@authentication_required  
def process_data():
    data = request.get_json()
    # Don't put complex logic here
    if data['type'] == 'special':
        # Complex processing logic...
```

### Repository Pattern (for data access)
Abstract data access through repository interfaces:

```python
# ✅ CORRECT: Repository abstraction
class UserRepository:
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    def create_user(self, user_data: dict) -> User:
        pass

class DatabaseUserRepository(UserRepository):
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return db.session.query(User).filter(User.id == user_id).first()
```

### Dependency Injection
Use dependency injection for testability:

```python
# ✅ CORRECT: Dependency injection
class UserService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service
    
    def create_user(self, user_data: dict) -> User:
        user = self.user_repo.create_user(user_data)
        self.email_service.send_welcome_email(user)
        return user
```

## 📝 Mandatory Requirements

### For New API Endpoints

1. **Authentication & Authorization**:
   ```python
   @app.route('/api/protected-endpoint', methods=['POST'])
   @authentication_required  # Required for protected resources
   @rate_limit(requests_per_minute=60)  # Required for all public endpoints
   @validate_json_schema(endpoint_schema)  # Required input validation
   def protected_endpoint():
       # Implementation
   ```

2. **Input Validation**:
   ```python
   def validate_user_input(data: dict) -> dict:
       required_fields = ['email', 'name']
       for field in required_fields:
           if field not in data:
               raise ValidationError(f"Missing required field: {field}")
       
       # Sanitize inputs
       data['email'] = data['email'].lower().strip()
       data['name'] = html.escape(data['name'].strip())
       
       # Validate formats
       if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
           raise ValidationError("Invalid email format")
       
       return data
   ```

3. **Error Handling**:
   ```python
   @app.errorhandler(ValidationError)
   def handle_validation_error(e):
       return jsonify({'error': str(e), 'type': 'validation'}), 400
   
   @app.errorhandler(AuthenticationError)  
   def handle_auth_error(e):
       return jsonify({'error': 'Authentication required'}), 401
   
   @app.errorhandler(Exception)
   def handle_unexpected_error(e):
       logger.error(f"Unexpected error: {e}", exc_info=True)
       return jsonify({'error': 'Internal server error'}), 500
   ```

4. **Comprehensive Documentation**:
   ```python
   def create_user_endpoint():
       """Create a new user account.
       
       Request Body:
           email (str): User's email address (required)
           name (str): User's full name (required)
           preferences (dict): Optional user preferences
       
       Returns:
           JSON response with user details
           
       Status Codes:
           201: User created successfully
           400: Invalid input data
           409: User already exists
           429: Rate limit exceeded
       
       Raises:
           ValidationError: Invalid input parameters
           DuplicateUserError: User with email already exists
       """
   ```

### For New Database Models/Changes

1. **Migration Required**:
   ```python
   # Create migration script: migrations/001_add_user_preferences.py
   def upgrade():
       """Add user preferences table."""
       op.create_table(
           'user_preferences',
           sa.Column('id', sa.Integer, primary_key=True),
           sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
           sa.Column('preferences', sa.JSON, nullable=True),
           sa.Column('created_at', sa.DateTime, default=sa.func.now()),
           sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
       )
   
   def downgrade():
       """Remove user preferences table."""
       op.drop_table('user_preferences')
   ```

2. **Model Validation**:
   ```python
   class User(db.Model):
       __tablename__ = 'users'
       
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(255), unique=True, nullable=False)
       name = db.Column(db.String(255), nullable=False)
       
       def validate_data(self):
           """Validate model data before save."""
           if not self.email:
               raise ValidationError("Email is required")
           if not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
               raise ValidationError("Invalid email format")
           if len(self.name) < 2:
               raise ValidationError("Name must be at least 2 characters")
       
       def to_dict(self):
           """Convert model to dictionary (excluding sensitive fields)."""
           return {
               'id': self.id,
               'email': self.email,
               'name': self.name
           }
   ```

### For New Services

1. **Service Structure**:
   ```python
   class DataProcessingService:
       """Service for handling data processing operations."""
       
       def __init__(self, repository: DataRepository, validator: DataValidator):
           self.repository = repository
           self.validator = validator
           self.logger = logging.getLogger(__name__)
       
       def process_data(self, user_id: int, data: dict) -> dict:
           """Process user data with validation and error handling."""
           try:
               # Validate input
               validated_data = self.validator.validate(data)
               
               # Process data
               result = self._perform_processing(validated_data)
               
               # Store result
               self.repository.save_result(user_id, result)
               
               return {'success': True, 'data': result}
           except ValidationError as e:
               self.logger.warning(f"Validation error for user {user_id}: {e}")
               raise
           except Exception as e:
               self.logger.error(f"Processing error for user {user_id}: {e}")
               raise ProcessingError("Data processing failed")
       
       def _perform_processing(self, data: dict) -> dict:
           """Private method for actual data processing."""
           # Implementation details
           return processed_data
   ```

## 🧪 Testing Requirements

### Test Structure for New Features

1. **Create Corresponding Test File**:
   ```python
   # tests/test_user_service.py
   import pytest
   from unittest.mock import Mock, patch
   from app.services.user_service import UserService
   from app.models.user import User
   from app.exceptions import ValidationError
   
   class TestUserService:
       """Test cases for UserService."""
       
       @pytest.fixture
       def mock_repository(self):
           return Mock()
       
       @pytest.fixture
       def user_service(self, mock_repository):
           return UserService(user_repository=mock_repository)
       
       def test_create_user_success(self, user_service, mock_repository):
           """Test successful user creation."""
           # Arrange
           user_data = {'email': 'test@example.com', 'name': 'Test User'}
           expected_user = User(id=1, email='test@example.com', name='Test User')
           mock_repository.create_user.return_value = expected_user
           
           # Act
           result = user_service.create_user(user_data)
           
           # Assert
           assert result.email == 'test@example.com'
           mock_repository.create_user.assert_called_once_with(user_data)
       
       def test_create_user_validation_error(self, user_service):
           """Test user creation with invalid data."""
           # Arrange
           invalid_data = {'email': 'invalid-email', 'name': ''}
           
           # Act & Assert
           with pytest.raises(ValidationError):
               user_service.create_user(invalid_data)
   ```

2. **Test Categories Required**:
   - **Unit Tests**: Test individual functions/methods
   - **Integration Tests**: Test component interactions
   - **API Tests**: Test endpoint functionality
   - **Security Tests**: Test authentication/authorization
   - **Performance Tests**: Test response times and resource usage

3. **Performance Tests**:
   ```python
   def test_api_response_time(self):
       """Test that API responses meet performance requirements."""
       import time
       
       start_time = time.time()
       response = self.client.get('/api/users')
       response_time = time.time() - start_time
       
       assert response.status_code == 200
       assert response_time < 0.5  # Must be under 500ms
   ```

## 🔒 Security Guidelines

### Input Sanitization
```python
import html
import re
from urllib.parse import quote

def sanitize_input(data: dict) -> dict:
    """Sanitize all user inputs."""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # HTML escape to prevent XSS
            value = html.escape(value.strip())
            
            # Additional sanitization based on field type
            if key == 'email':
                value = value.lower()
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
                    raise ValidationError(f"Invalid email format: {key}")
            elif key.endswith('_url'):
                # Validate URLs
                if not re.match(r'^https?://', value):
                    raise ValidationError(f"Invalid URL format: {key}")
        
        elif isinstance(value, (int, float)):
            # Validate numeric ranges
            if key.endswith('_count') and value < 0:
                raise ValidationError(f"Count cannot be negative: {key}")
        
        sanitized[key] = value
    
    return sanitized
```

### Authentication and Authorization
```python
from functools import wraps
from flask import session, request

def authentication_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def authorization_required(required_role: str):
    """Decorator to require specific authorization."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('user_role')
            if user_role != required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### Secure Data Storage
```python
import bcrypt
from cryptography.fernet import Fernet

def hash_password(password: str) -> str:
    """Hash password securely."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data."""
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt sensitive data."""
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

## 📊 Database Guidelines

### Query Optimization
```python
# ✅ CORRECT: Efficient queries with proper joins and indexing
def get_user_with_preferences(user_id: int):
    return db.session.query(User).options(
        joinedload(User.preferences),
        joinedload(User.settings)
    ).filter(User.id == user_id).first()

# ❌ INCORRECT: N+1 query problem
def get_user_with_preferences_bad(user_id: int):
    user = User.query.get(user_id)
    preferences = user.preferences  # Causes additional query
    settings = user.settings        # Causes additional query
    return user
```

### Transaction Management
```python
def transfer_data(source_id: int, target_id: int, amount: int):
    """Example of proper transaction handling."""
    try:
        with db.session.begin():
            # All operations within this block are transactional
            source = Account.query.with_for_update().get(source_id)
            target = Account.query.with_for_update().get(target_id)
            
            if source.balance < amount:
                raise InsufficientFundsError("Not enough balance")
            
            source.balance -= amount
            target.balance += amount
            
            # Transaction commits automatically if no exception
            
    except Exception as e:
        # Transaction rolls back automatically on exception
        logger.error(f"Transfer failed: {e}")
        raise
```

## 🔄 Automated Validation

### Pre-commit Hooks
Every application should include automated validation:

1. **Code Quality**: Formatting, linting, type checking
2. **Security**: Vulnerability scanning, secret detection
3. **Testing**: Critical tests must pass
4. **Coverage**: Test coverage validation
5. **Documentation**: Documentation validation and updates

### Running Validations Manually
```bash
# Run all validations (customize for your app)
python scripts/validate_test_coverage.py
python scripts/validate_security.py
python scripts/validate_documentation.py
python scripts/validate_performance.py

# Auto-fix issues where possible
python scripts/fix_code_quality.py
python scripts/update_documentation.py
```

## 📋 Development Checklist

### Before Starting New Feature
- [ ] Review existing similar functionality
- [ ] Check if tests already exist for related features
- [ ] Plan database changes (if any)
- [ ] Design API endpoints (if any)
- [ ] Write test cases first (TDD)

### During Development
- [ ] Follow established architecture patterns
- [ ] Implement comprehensive error handling
- [ ] Add input validation for all inputs
- [ ] Include proper logging with appropriate levels
- [ ] Write comprehensive docstrings

### Before Committing
- [ ] All new tests pass
- [ ] All existing tests still pass
- [ ] Code coverage above 95%
- [ ] No security vulnerabilities introduced
- [ ] Performance requirements met
- [ ] Documentation updated (automatic via hooks)

## 🚨 Common Pitfalls to Avoid

### 1. **Breaking Existing Functionality**
```python
# ❌ WRONG: Changing existing function signature
def process_data(data):  # Removed optional parameter
    pass

# ✅ CORRECT: Maintain backward compatibility
def process_data(data, options=None):  # Keep optional parameter
    if options is None:
        options = {}
    pass
```

### 2. **Ignoring Error Handling**
```python
# ❌ WRONG: No error handling
def fetch_external_data():
    response = requests.get('https://api.example.com/data')
    return response.json()['data']

# ✅ CORRECT: Comprehensive error handling
def fetch_external_data():
    try:
        response = requests.get('https://api.example.com/data', timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'data' not in data:
            raise DataFormatError("Invalid response format")
        
        return data['data']
        
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise ExternalServiceError("Failed to fetch external data")
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid response format: {e}")
        raise DataFormatError("Invalid response from external service")
```

### 3. **Skipping Input Validation**
```python
# ❌ WRONG: No input validation
@app.route('/api/update-user', methods=['POST'])
def update_user():
    data = request.get_json()
    user_id = data['user_id']  # Could be anything!
    User.query.get(user_id).update(data)

# ✅ CORRECT: Validate all inputs
@app.route('/api/update-user', methods=['POST'])
@authentication_required
def update_user():
    data = request.get_json()
    
    # Validate request structure
    if not data or 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
    
    # Validate and sanitize inputs
    try:
        user_id = int(data['user_id'])
        if user_id <= 0:
            raise ValueError("Invalid user ID")
        
        # Additional validation...
        validated_data = sanitize_user_update_data(data)
        
    except (ValueError, ValidationError) as e:
        return jsonify({'error': str(e)}), 400
    
    # Process with validated data
    result = user_service.update_user(user_id, validated_data)
    return jsonify(result)
```

## 🎯 Success Metrics

A successful application implementation should:
- Pass all automated tests (>95% coverage)
- Meet performance benchmarks
- Pass all security validations
- Have up-to-date documentation
- Follow all architectural patterns
- Include comprehensive error handling
- Maintain backward compatibility

## 📚 Framework-Specific Guidelines

### Flask Applications
- Use Blueprints for route organization
- Implement proper error handlers
- Use Flask-Migrate for database migrations
- Follow Flask security best practices

### FastAPI Applications
- Leverage automatic OpenAPI documentation
- Use Pydantic models for validation
- Implement proper dependency injection
- Use async/await for I/O operations

### CLI Applications
- Use Click or argparse for command-line interface
- Implement proper logging and progress indicators
- Include comprehensive help documentation
- Handle interrupts and edge cases gracefully

### Microservices
- Implement health checks and metrics endpoints
- Use proper service discovery patterns
- Implement circuit breaker patterns
- Include distributed tracing

By following these guidelines, you ensure that every application built with this template maintains high standards of quality, security, and maintainability while providing excellent developer experience through automation and clear patterns.