"""
Flask Application with Enhanced Documentation

Main application entry point with comprehensive API documentation.
"""

from flask import Flask, request, jsonify, g
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
import logging
import time
import uuid
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Enable CORS
CORS(app)

# Create API with comprehensive documentation
api = Api(
    app,
    version='1.0.0',
    title='Flask Application API',
    description="""
    A comprehensive Flask application with automatic documentation using Flask-RESTX.
    
    ## Features
    
    * **Automatic Swagger Documentation** - Interactive API docs
    * **Authentication** - Bearer token authentication
    * **Validation** - Request/response validation
    * **Error Handling** - Comprehensive error responses
    * **Rate Limiting** - Built-in rate limiting protection
    * **Security** - Input validation and sanitization
    
    ## Authentication
    
    Most endpoints require a Bearer token in the Authorization header:
    
    ```
    Authorization: Bearer your_token_here
    ```
    
    ## Error Responses
    
    All errors follow a consistent format:
    
    ```json
    {
        "error": "Error Type",
        "message": "Human-readable description",
        "details": ["Additional information"],
        "request_id": "unique_request_id"
    }
    ```
    """,
    doc='/docs/',  # Swagger UI location
    contact='api-support@example.com',
    contact_email='api-support@example.com'
)

# Rate limiting storage (in-memory for demo)
request_counts = {}

# Middleware for request ID and rate limiting
@app.before_request
def before_request():
    """Add request ID and implement rate limiting."""
    # Add request ID for tracing
    g.request_id = str(uuid.uuid4())
    
    # Simple rate limiting
    client_ip = request.remote_addr
    current_time = time.time()
    
    # Clean old entries (older than 1 hour)
    cutoff_time = current_time - 3600
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts.get(client_ip, [])
        if timestamp > cutoff_time
    ]
    
    # Check rate limit (100 requests per hour)
    if len(request_counts.get(client_ip, [])) >= 100:
        return jsonify({
            "error": "Too Many Requests",
            "message": "Rate limit exceeded",
            "details": ["Limit: 100 requests per hour"],
            "request_id": g.request_id
        }), 429
    
    # Record this request
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip].append(current_time)

@app.after_request
def after_request(response):
    """Add response headers."""
    response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
    return response

# Authentication decorator
def authentication_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                "error": "Unauthorized",
                "message": "Authentication token required",
                "details": ["Include 'Authorization: Bearer TOKEN' header"],
                "request_id": getattr(g, 'request_id', 'unknown')
            }), 401
        
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                raise ValueError("Invalid scheme")
        except ValueError:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid authentication format",
                "details": ["Use 'Authorization: Bearer TOKEN' format"],
                "request_id": getattr(g, 'request_id', 'unknown')
            }), 401
        
        # Simple token validation (replace with proper JWT validation)
        if not token or token == "invalid_token":
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid authentication token",
                "details": ["Please provide a valid token"],
                "request_id": getattr(g, 'request_id', 'unknown')
            }), 401
        
        # Store user info in g (in real app, decode JWT)
        g.current_user = f"user_from_token_{token[:8]}"
        return f(*args, **kwargs)
    
    return decorated

# Input validation decorator
def validate_json_schema(schema):
    """Decorator to validate JSON input against schema."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    "error": "Bad Request",
                    "message": "Content-Type must be application/json",
                    "details": [],
                    "request_id": getattr(g, 'request_id', 'unknown')
                }), 400
            
            data = request.get_json()
            
            # Simple validation (in real app, use jsonschema library)
            validation_errors = validate_data(data, schema)
            if validation_errors:
                return jsonify({
                    "error": "Validation Error",
                    "message": "Input validation failed",
                    "details": validation_errors,
                    "request_id": getattr(g, 'request_id', 'unknown')
                }), 400
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def validate_data(data: Dict[str, Any], schema: Dict[str, Any]) -> list:
    """Simple data validation function."""
    errors = []
    
    # Check required fields
    for field in schema.get('required', []):
        if field not in data:
            errors.append(f"Field '{field}' is required")
        elif not data[field]:
            errors.append(f"Field '{field}' cannot be empty")
    
    # Check email format
    if 'email' in data:
        email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
        if not re.match(email_pattern, data['email']):
            errors.append("Invalid email format")
    
    # Check age range
    if 'age' in data and data['age'] is not None:
        if not isinstance(data['age'], int) or data['age'] < 0 or data['age'] > 150:
            errors.append("Age must be between 0 and 150")
    
    return errors

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data to prevent XSS and injection attacks."""
    import html
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # HTML escape to prevent XSS
            sanitized[key] = html.escape(value.strip())
        else:
            sanitized[key] = value
    
    return sanitized

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found",
        "details": [],
        "request_id": getattr(g, 'request_id', 'unknown')
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "details": [],
        "request_id": getattr(g, 'request_id', 'unknown')
    }), 500

# API Models for documentation
user_model = api.model('User', {
    'id': fields.String(required=True, description='Unique user identifier', example='user_123'),
    'name': fields.String(required=True, description='User full name', example='John Doe'),
    'email': fields.String(required=True, description='User email address', example='john.doe@example.com'),
    'age': fields.Integer(description='User age', example=25),
    'preferences': fields.Raw(description='User preferences as key-value pairs', example={'theme': 'dark'}),
    'created_at': fields.String(required=True, description='Creation timestamp', example='2023-12-01T10:00:00Z'),
    'updated_at': fields.String(required=True, description='Last update timestamp', example='2023-12-01T10:00:00Z')
})

user_create_model = api.model('UserCreate', {
    'name': fields.String(required=True, description='User full name', example='John Doe'),
    'email': fields.String(required=True, description='User email address', example='john.doe@example.com'),
    'age': fields.Integer(description='User age (0-150)', example=25),
    'preferences': fields.Raw(description='User preferences', example={'theme': 'dark', 'notifications': True})
})

user_update_model = api.model('UserUpdate', {
    'name': fields.String(description='User full name', example='John Smith'),
    'age': fields.Integer(description='User age (0-150)', example=26),
    'preferences': fields.Raw(description='User preferences', example={'theme': 'light'})
})

error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error type', example='Validation Error'),
    'message': fields.String(required=True, description='Human-readable error message', example='Invalid input provided'),
    'details': fields.List(fields.String, description='Additional error details'),
    'request_id': fields.String(required=True, description='Unique request identifier', example='req_123456')
})

health_model = api.model('Health', {
    'status': fields.String(required=True, description='Health status', example='healthy'),
    'timestamp': fields.String(required=True, description='Current timestamp', example='2023-12-01T10:00:00Z'),
    'version': fields.String(required=True, description='API version', example='1.0.0')
})

# Namespaces for organization
health_ns = Namespace('health', description='Health check operations')
users_ns = Namespace('users', description='User management operations')

api.add_namespace(health_ns)
api.add_namespace(users_ns, path='/users')

# Health check endpoint
@health_ns.route('/')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.marshal_with(health_model)
    @api.response(200, 'API is healthy')
    def get(self):
        """
        Health check endpoint
        
        Check if the API is running and healthy.
        No authentication required.
        """
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0'
        }

# User management endpoints
@users_ns.route('/')
class UserList(Resource):
    @api.doc('create_user')
    @api.expect(user_create_model)
    @api.marshal_with(user_model, code=201)
    @api.response(201, 'User created successfully')
    @api.response(400, 'Validation error', error_model)
    @api.response(401, 'Authentication required', error_model)
    @api.response(429, 'Rate limit exceeded', error_model)
    @authentication_required
    @validate_json_schema({
        'required': ['name', 'email']
    })
    def post(self):
        """
        Create a new user
        
        Create a new user account with the provided information.
        
        **Required fields:**
        - name: User's full name (1-100 characters)
        - email: Valid email address
        
        **Optional fields:**
        - age: User's age (0-150)
        - preferences: Key-value pairs for user preferences
        """
        try:
            data = sanitize_input(request.get_json())
            
            # Simulate user creation
            user_id = str(uuid.uuid4())
            current_time = datetime.utcnow().isoformat() + 'Z'
            
            new_user = {
                'id': user_id,
                'name': data['name'],
                'email': data['email'],
                'age': data.get('age'),
                'preferences': data.get('preferences'),
                'created_at': current_time,
                'updated_at': current_time
            }
            
            logger.info(f"User created: {user_id}")
            return new_user, 201
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            api.abort(500, "Internal server error")

    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    @api.response(200, 'List of users')
    @api.response(401, 'Authentication required', error_model)
    @api.response(429, 'Rate limit exceeded', error_model)
    @api.param('skip', 'Number of records to skip', type=int, default=0)
    @api.param('limit', 'Maximum number of records to return', type=int, default=10)
    @authentication_required
    def get(self):
        """
        List all users
        
        Get a list of all users with optional pagination.
        """
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 10))
        
        # Validate pagination parameters
        if skip < 0:
            skip = 0
        if limit < 1 or limit > 100:
            limit = 10
        
        # Simulate user listing
        users = [
            {
                'id': f'user_{i}',
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'age': 20 + i,
                'preferences': {'theme': 'dark' if i % 2 == 0 else 'light'},
                'created_at': '2023-12-01T10:00:00Z',
                'updated_at': '2023-12-01T10:00:00Z'
            }
            for i in range(skip, min(skip + limit, 20))  # Simulate 20 total users
        ]
        
        return users

@users_ns.route('/<string:user_id>')
@api.param('user_id', 'Unique user identifier')
class User(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    @api.response(200, 'User found')
    @api.response(401, 'Authentication required', error_model)
    @api.response(404, 'User not found', error_model)
    @api.response(429, 'Rate limit exceeded', error_model)
    @authentication_required
    def get(self, user_id):
        """
        Get user by ID
        
        Retrieve a specific user by their unique identifier.
        """
        # Simulate user not found
        if user_id == "nonexistent":
            api.abort(404, "User not found")
        
        # Simulate user retrieval
        user = {
            'id': user_id,
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'age': 25,
            'preferences': {'theme': 'dark'},
            'created_at': '2023-12-01T10:00:00Z',
            'updated_at': '2023-12-01T10:00:00Z'
        }
        
        return user

    @api.doc('update_user')
    @api.expect(user_update_model)
    @api.marshal_with(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Validation error', error_model)
    @api.response(401, 'Authentication required', error_model)
    @api.response(404, 'User not found', error_model)
    @api.response(429, 'Rate limit exceeded', error_model)
    @authentication_required
    def put(self, user_id):
        """
        Update user
        
        Update an existing user's information.
        All fields are optional - only provided fields will be updated.
        """
        # Simulate user not found
        if user_id == "nonexistent":
            api.abort(404, "User not found")
        
        try:
            data = sanitize_input(request.get_json() or {})
            
            # Validate data if provided
            validation_errors = []
            if 'email' in data:
                email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
                if not re.match(email_pattern, data['email']):
                    validation_errors.append("Invalid email format")
            
            if 'age' in data and data['age'] is not None:
                if not isinstance(data['age'], int) or data['age'] < 0 or data['age'] > 150:
                    validation_errors.append("Age must be between 0 and 150")
            
            if validation_errors:
                return jsonify({
                    "error": "Validation Error",
                    "message": "Input validation failed",
                    "details": validation_errors,
                    "request_id": getattr(g, 'request_id', 'unknown')
                }), 400
            
            # Simulate user update
            updated_user = {
                'id': user_id,
                'name': data.get('name', 'John Doe'),
                'email': 'john.doe@example.com',  # In real app, get from database
                'age': data.get('age', 25),
                'preferences': data.get('preferences', {'theme': 'dark'}),
                'created_at': '2023-12-01T10:00:00Z',
                'updated_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.info(f"User updated: {user_id}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            api.abort(500, "Internal server error")

    @api.doc('delete_user')
    @api.response(204, 'User deleted successfully')
    @api.response(401, 'Authentication required', error_model)
    @api.response(404, 'User not found', error_model)
    @api.response(429, 'Rate limit exceeded', error_model)
    @authentication_required
    def delete(self, user_id):
        """
        Delete user
        
        Delete a user account permanently.
        This action cannot be undone.
        """
        # Simulate user not found
        if user_id == "nonexistent":
            api.abort(404, "User not found")
        
        # Simulate user deletion
        logger.info(f"User deleted: {user_id}")
        return '', 204

# Development server
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )