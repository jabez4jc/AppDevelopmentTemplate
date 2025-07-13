"""
FastAPI Application with Automatic Documentation

Main application entry point with comprehensive API documentation.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Any, Optional
import logging
import time
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="FastAPI Application",
    description="""
    A comprehensive FastAPI application with automatic documentation.
    
    ## Features
    
    * **Automatic OpenAPI Documentation** - Interactive API docs
    * **Authentication** - Bearer token authentication
    * **Validation** - Automatic request/response validation
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
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "api-support@example.com",
        "url": "https://example.com/support"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ],
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # Alternative documentation
    openapi_url="/openapi.json"  # OpenAPI specification
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Rate limiting middleware (simple in-memory implementation)
request_counts = {}
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Simple rate limiting middleware."""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries (older than 1 hour)
    cutoff_time = current_time - 3600
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts.get(client_ip, [])
        if timestamp > cutoff_time
    ]
    
    # Check rate limit (100 requests per hour)
    if len(request_counts.get(client_ip, [])) >= 100:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Too Many Requests",
                "message": "Rate limit exceeded",
                "details": ["Limit: 100 requests per hour"],
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        )
    
    # Record this request
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip].append(current_time)
    
    return await call_next(request)

# Pydantic models with comprehensive examples
class UserCreateRequest(BaseModel):
    """User creation request model."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name",
        example="John Doe"
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="john.doe@example.com"
    )
    age: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="User's age",
        example=25
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="User preferences as key-value pairs",
        example={"theme": "dark", "notifications": True}
    )

    class Config:
        schema_extra = {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "age": 25,
                    "preferences": {
                        "theme": "dark",
                        "notifications": True
                    }
                },
                {
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com"
                }
            ]
        }

class UserResponse(BaseModel):
    """User response model."""
    id: str = Field(..., description="Unique user identifier", example="user_123")
    name: str = Field(..., description="User's full name", example="John Doe")
    email: EmailStr = Field(..., description="User's email address", example="john.doe@example.com")
    age: Optional[int] = Field(None, description="User's age", example=25)
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    created_at: str = Field(..., description="Creation timestamp", example="2023-12-01T10:00:00Z")
    updated_at: str = Field(..., description="Last update timestamp", example="2023-12-01T10:00:00Z")

class UserUpdateRequest(BaseModel):
    """User update request model."""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User's full name",
        example="John Smith"
    )
    age: Optional[int] = Field(
        None,
        ge=0,
        le=150,
        description="User's age",
        example=26
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="User preferences",
        example={"theme": "light"}
    )

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type", example="Validation Error")
    message: str = Field(..., description="Human-readable error message", example="Invalid input provided")
    details: List[str] = Field(default_factory=list, description="Additional error details")
    request_id: str = Field(..., description="Unique request identifier", example="req_123456")

# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate bearer token and return user information.
    
    In a real application, this would validate the JWT token
    and return user information from the database.
    """
    token = credentials.credentials
    
    # Simple token validation (replace with proper JWT validation)
    if not token or token == "invalid_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # In a real app, decode JWT and return user info
    return f"user_from_token_{token[:8]}"

# Health check endpoint (no authentication required)
@app.get(
    "/health",
    tags=["health"],
    response_model=Dict[str, str],
    summary="Health check",
    description="Check if the API is running and healthy",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2023-12-01T10:00:00Z",
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

# User management endpoints
@app.post(
    "/users",
    tags=["users"],
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="""
    Create a new user account with the provided information.
    
    **Required fields:**
    - name: User's full name (1-100 characters)
    - email: Valid email address
    
    **Optional fields:**
    - age: User's age (0-150)
    - preferences: Key-value pairs for user preferences
    """,
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def create_user(
    user_data: UserCreateRequest,
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Create a new user."""
    try:
        # In a real application, save to database
        from datetime import datetime
        import uuid
        
        user_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat() + "Z"
        
        # Simulate user creation
        new_user = UserResponse(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            age=user_data.age,
            preferences=user_data.preferences,
            created_at=current_time,
            updated_at=current_time
        )
        
        logger.info(f"User created: {user_id}")
        return new_user
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get(
    "/users/{user_id}",
    tags=["users"],
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their unique identifier",
    responses={
        200: {"description": "User found"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "User not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def get_user(
    user_id: str = Field(..., description="Unique user identifier"),
    request: Request = None,
    current_user: str = Depends(get_current_user)
):
    """Get user by ID."""
    # In a real application, fetch from database
    if user_id == "nonexistent":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Simulate user retrieval
    from datetime import datetime
    user = UserResponse(
        id=user_id,
        name="John Doe",
        email="john.doe@example.com",
        age=25,
        preferences={"theme": "dark"},
        created_at="2023-12-01T10:00:00Z",
        updated_at="2023-12-01T10:00:00Z"
    )
    
    return user

@app.put(
    "/users/{user_id}",
    tags=["users"],
    response_model=UserResponse,
    summary="Update user",
    description="Update an existing user's information",
    responses={
        200: {"description": "User updated successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "User not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Update user information."""
    # In a real application, update in database
    if user_id == "nonexistent":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Simulate user update
    from datetime import datetime
    updated_user = UserResponse(
        id=user_id,
        name=user_data.name or "John Doe",
        email="john.doe@example.com",  # In real app, get from database
        age=user_data.age,
        preferences=user_data.preferences,
        created_at="2023-12-01T10:00:00Z",
        updated_at=datetime.utcnow().isoformat() + "Z"
    )
    
    logger.info(f"User updated: {user_id}")
    return updated_user

@app.delete(
    "/users/{user_id}",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account permanently",
    responses={
        204: {"description": "User deleted successfully"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        404: {"model": ErrorResponse, "description": "User not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def delete_user(
    user_id: str,
    request: Request,
    current_user: str = Depends(get_current_user)
):
    """Delete user."""
    # In a real application, delete from database
    if user_id == "nonexistent":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Simulate user deletion
    logger.info(f"User deleted: {user_id}")
    return None

@app.get(
    "/users",
    tags=["users"],
    response_model=List[UserResponse],
    summary="List users",
    description="Get a list of all users with optional pagination",
    responses={
        200: {"description": "List of users"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"}
    }
)
async def list_users(
    skip: int = Field(0, ge=0, description="Number of records to skip"),
    limit: int = Field(10, ge=1, le=100, description="Maximum number of records to return"),
    request: Request = None,
    current_user: str = Depends(get_current_user)
):
    """List all users with pagination."""
    # In a real application, fetch from database with pagination
    users = [
        UserResponse(
            id=f"user_{i}",
            name=f"User {i}",
            email=f"user{i}@example.com",
            age=20 + i,
            preferences={"theme": "dark" if i % 2 == 0 else "light"},
            created_at="2023-12-01T10:00:00Z",
            updated_at="2023-12-01T10:00:00Z"
        )
        for i in range(skip, min(skip + limit, 20))  # Simulate 20 total users
    ]
    
    return users

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "details": [],
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": [],
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )