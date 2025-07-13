# Universal Application Testing Guide

This document provides a comprehensive testing framework template that can be adapted for any application type. It ensures thorough testing coverage, consistent quality standards, and automated validation.

## 🎯 Testing Philosophy

### Core Principles
1. **Test-Driven Development (TDD)**: Write tests before implementation
2. **Comprehensive Coverage**: Aim for >95% code coverage across all modules
3. **Multiple Test Types**: Unit, integration, security, performance, and end-to-end tests
4. **Automated Execution**: All tests run automatically in CI/CD pipelines
5. **Fast Feedback**: Quick test execution for rapid development cycles

### Quality Standards
- **Zero broken tests** in main branch
- **Performance benchmarks** must be met
- **Security vulnerabilities** must be caught
- **Cross-platform compatibility** validated
- **Documentation accuracy** verified

## 📊 Test Categories

### 1. Unit Tests
Test individual functions, methods, and classes in isolation.

```python
# tests/test_user_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.exceptions import ValidationError

class TestUserService:
    """Unit tests for UserService class."""
    
    @pytest.fixture
    def mock_dependencies(self):
        return {
            'user_repo': Mock(),
            'email_service': Mock(),
            'validation_service': Mock()
        }
    
    @pytest.fixture
    def user_service(self, mock_dependencies):
        return UserService(**mock_dependencies)
    
    def test_create_user_success(self, user_service, mock_dependencies):
        """Test successful user creation."""
        # Arrange
        user_data = {'email': 'test@example.com', 'name': 'Test User'}
        expected_user = {'id': 1, 'email': 'test@example.com', 'name': 'Test User'}
        
        mock_dependencies['validation_service'].validate_user_data.return_value = user_data
        mock_dependencies['user_repo'].create_user.return_value = expected_user
        
        # Act
        result = user_service.create_user(user_data)
        
        # Assert
        assert result == expected_user
        mock_dependencies['validation_service'].validate_user_data.assert_called_once_with(user_data)
        mock_dependencies['user_repo'].create_user.assert_called_once_with(user_data)
        mock_dependencies['email_service'].send_welcome_email.assert_called_once_with(expected_user)
    
    def test_create_user_validation_error(self, user_service, mock_dependencies):
        """Test user creation with invalid data."""
        # Arrange
        invalid_data = {'email': 'invalid-email'}
        mock_dependencies['validation_service'].validate_user_data.side_effect = ValidationError("Invalid email")
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Invalid email"):
            user_service.create_user(invalid_data)
        
        mock_dependencies['user_repo'].create_user.assert_not_called()
        mock_dependencies['email_service'].send_welcome_email.assert_not_called()
```

### 2. Integration Tests
Test how components work together.

```python
# tests/test_user_integration.py
import pytest
from app import create_app, db
from app.models.user import User

class TestUserIntegration:
    """Integration tests for user functionality."""
    
    @pytest.fixture
    def app(self):
        app = create_app(config_name='testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_user_registration_flow(self, client):
        """Test complete user registration flow."""
        # Arrange
        user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'secure_password123'
        }
        
        # Act - Register user
        response = client.post('/api/users/register', json=user_data)
        
        # Assert - Registration successful
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['success'] is True
        assert 'user_id' in response_data
        
        # Verify user in database
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.name == 'Test User'
        
        # Act - Login with new user
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'secure_password123'
        })
        
        # Assert - Login successful
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        assert 'access_token' in login_data
```

### 3. API/Endpoint Tests
Test HTTP endpoints and API functionality.

```python
# tests/test_api_endpoints.py
import pytest
import json
from app import create_app, db

class TestAPIEndpoints:
    """Test all API endpoints."""
    
    @pytest.fixture
    def app(self):
        app = create_app(config_name='testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers for protected endpoints."""
        # Create test user and get token
        user_data = {'email': 'test@example.com', 'password': 'test_password'}
        client.post('/api/users/register', json=user_data)
        
        login_response = client.post('/api/auth/login', json=user_data)
        token = login_response.get_json()['access_token']
        
        return {'Authorization': f'Bearer {token}'}
    
    def test_health_endpoint(self, client):
        """Test application health endpoint."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_protected_endpoint_without_auth(self, client):
        """Test protected endpoint without authentication."""
        response = client.get('/api/users/profile')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_protected_endpoint_with_auth(self, client, auth_headers):
        """Test protected endpoint with valid authentication."""
        response = client.get('/api/users/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'email' in data
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting functionality."""
        # Make rapid requests to trigger rate limiting
        responses = []
        for _ in range(150):  # Assuming 100 req/min limit
            response = client.get('/api/health')
            responses.append(response.status_code)
        
        # Should eventually get rate limited
        assert 429 in responses, "Rate limiting not working"
    
    def test_api_response_times(self, client):
        """Test API response time requirements."""
        import time
        
        endpoints_to_test = [
            '/api/health',
            '/api/status'
        ]
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = client.get(endpoint)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 0.5, f"Endpoint {endpoint} took {response_time:.3f}s (>500ms limit)"
```

### 4. Database Tests
Test database operations, models, and migrations.

```python
# tests/test_database.py
import pytest
from app import create_app, db
from app.models.user import User
from sqlalchemy.exc import IntegrityError

class TestDatabase:
    """Test database operations and models."""
    
    @pytest.fixture
    def app(self):
        app = create_app(config_name='testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_user_model_creation(self, app):
        """Test user model creation and validation."""
        with app.app_context():
            # Test valid user creation
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash='hashed_password'
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            retrieved_user = User.query.filter_by(email='test@example.com').first()
            assert retrieved_user is not None
            assert retrieved_user.name == 'Test User'
    
    def test_user_model_constraints(self, app):
        """Test database constraints and validations."""
        with app.app_context():
            # Create first user
            user1 = User(email='test@example.com', name='User 1')
            db.session.add(user1)
            db.session.commit()
            
            # Try to create duplicate email (should fail)
            user2 = User(email='test@example.com', name='User 2')
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_database_relationships(self, app):
        """Test model relationships work correctly."""
        with app.app_context():
            # Create user
            user = User(email='test@example.com', name='Test User')
            db.session.add(user)
            db.session.commit()
            
            # Test relationships (adapt based on your models)
            # This is an example - customize for your app
            assert user.id is not None
            # assert user.related_objects == []  # Initially empty
    
    def test_database_performance(self, app):
        """Test database query performance."""
        import time
        
        with app.app_context():
            # Create test data
            users = []
            for i in range(100):
                user = User(email=f'user{i}@example.com', name=f'User {i}')
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Test query performance
            start_time = time.time()
            result = User.query.filter(User.name.contains('User')).all()
            query_time = time.time() - start_time
            
            assert len(result) == 100
            assert query_time < 0.1, f"Query took {query_time:.3f}s (>100ms limit)"
```

### 5. Security Tests
Test authentication, authorization, and security vulnerabilities.

```python
# tests/test_security.py
import pytest
from app import create_app

class TestSecurity:
    """Test security features and vulnerabilities."""
    
    @pytest.fixture
    def app(self):
        return create_app(config_name='testing')
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks."""
        # Attempt SQL injection in various endpoints
        injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; DELETE FROM users WHERE 1=1; --"
        ]
        
        for injection in injection_attempts:
            # Test in different input fields
            response = client.post('/api/auth/login', json={
                'email': injection,
                'password': 'password'
            })
            
            # Should not cause internal server error (500)
            # Should return proper error response
            assert response.status_code in [400, 401, 422]
    
    def test_xss_protection(self, client):
        """Test protection against XSS attacks."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
        ]
        
        for payload in xss_payloads:
            # Test XSS in user registration
            response = client.post('/api/users/register', json={
                'email': 'test@example.com',
                'name': payload,
                'password': 'password123'
            })
            
            if response.status_code == 201:
                # If user was created, verify the payload is escaped
                profile_response = client.get('/api/users/profile')
                profile_data = profile_response.get_json()
                
                # Verify the payload is escaped/sanitized
                assert '<script>' not in profile_data.get('name', '')
                assert 'javascript:' not in profile_data.get('name', '')
    
    def test_authentication_security(self, client):
        """Test authentication security measures."""
        # Test password requirements
        weak_passwords = ['123', 'password', 'abc', '111111']
        
        for weak_password in weak_passwords:
            response = client.post('/api/users/register', json={
                'email': 'test@example.com',
                'name': 'Test User',
                'password': weak_password
            })
            
            # Should reject weak passwords
            assert response.status_code == 400
            data = response.get_json()
            assert 'password' in data.get('error', '').lower()
    
    def test_authorization_boundaries(self, client):
        """Test that users can only access their own data."""
        # Create two users
        user1_data = {'email': 'user1@example.com', 'password': 'password123'}
        user2_data = {'email': 'user2@example.com', 'password': 'password123'}
        
        client.post('/api/users/register', json=user1_data)
        client.post('/api/users/register', json=user2_data)
        
        # Login as user1
        login1_response = client.post('/api/auth/login', json=user1_data)
        token1 = login1_response.get_json()['access_token']
        headers1 = {'Authorization': f'Bearer {token1}'}
        
        # Login as user2
        login2_response = client.post('/api/auth/login', json=user2_data)
        token2 = login2_response.get_json()['access_token']
        
        # User1 should not be able to access user2's data
        response = client.get(f'/api/users/2/profile', headers=headers1)
        assert response.status_code in [403, 404]  # Forbidden or Not Found
```

### 6. Performance Tests
Test application performance and resource usage.

```python
# tests/test_performance.py
import pytest
import time
import threading
from app import create_app

class TestPerformance:
    """Test application performance characteristics."""
    
    @pytest.fixture
    def app(self):
        return create_app(config_name='testing')
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        def make_request():
            return client.get('/api/health')
        
        # Create multiple threads making concurrent requests
        threads = []
        results = []
        
        def worker():
            response = make_request()
            results.append(response.status_code)
        
        # Start 50 concurrent requests
        for _ in range(50):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 50
    
    def test_memory_usage(self, client):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make many requests to test for memory leaks
        for _ in range(1000):
            response = client.get('/api/health')
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory shouldn't grow by more than 50MB
        assert memory_growth < 50 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024:.2f}MB"
    
    def test_response_time_under_load(self, client):
        """Test response times remain acceptable under load."""
        response_times = []
        
        # Make requests and measure response time
        for _ in range(100):
            start_time = time.time()
            response = client.get('/api/health')
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Performance requirements
        assert avg_response_time < 0.1, f"Average response time: {avg_response_time:.3f}s"
        assert max_response_time < 0.5, f"Max response time: {max_response_time:.3f}s"
```

## 🧪 Test Suite Runner

Create a comprehensive test suite runner that organizes and executes all tests:

```python
# tests/test_suite_runner.py
#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner

Executes all test categories with detailed reporting and coverage analysis.
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List
import argparse

class TestSuiteRunner:
    """Comprehensive test execution framework."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path.cwd())
        self.test_categories = {
            'unit': 'tests/test_*_unit.py',
            'integration': 'tests/test_*_integration.py', 
            'api': 'tests/test_api_*.py',
            'database': 'tests/test_database.py',
            'security': 'tests/test_security.py',
            'performance': 'tests/test_performance.py'
        }
        self.results = {}
    
    def run_test_category(self, category: str, verbose: bool = False) -> Dict:
        """Run a specific test category."""
        pattern = self.test_categories.get(category)
        if not pattern:
            return {'error': f'Unknown test category: {category}'}
        
        print(f"🧪 Running {category} tests...")
        
        cmd = ['python', '-m', 'pytest', pattern, '-v' if verbose else '-q']
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'category': category,
            'duration': duration,
            'exit_code': result.returncode,
            'passed': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    def run_all_tests(self, categories: List[str] = None, verbose: bool = False) -> Dict:
        """Run all or specified test categories."""
        categories = categories or list(self.test_categories.keys())
        
        print("🚀 Starting comprehensive test suite...")
        print(f"📋 Test categories: {', '.join(categories)}")
        
        total_start_time = time.time()
        
        for category in categories:
            result = self.run_test_category(category, verbose)
            self.results[category] = result
            
            if result['passed']:
                print(f"  ✅ {category}: PASSED ({result['duration']:.2f}s)")
            else:
                print(f"  ❌ {category}: FAILED ({result['duration']:.2f}s)")
        
        total_duration = time.time() - total_start_time
        
        return {
            'total_duration': total_duration,
            'categories': self.results,
            'summary': self._generate_summary()
        }
    
    def run_with_coverage(self, categories: List[str] = None) -> Dict:
        """Run tests with coverage reporting."""
        print("📊 Running tests with coverage analysis...")
        
        categories = categories or list(self.test_categories.keys())
        patterns = [self.test_categories[cat] for cat in categories]
        
        cmd = [
            'python', '-m', 'pytest', 
            '--cov=app',  # Adjust for your package name
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=95'
        ] + patterns
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        
        return {
            'coverage_passed': result.returncode == 0,
            'coverage_output': result.stdout,
            'coverage_errors': result.stderr
        }
    
    def _generate_summary(self) -> Dict:
        """Generate test execution summary."""
        total_categories = len(self.results)
        passed_categories = sum(1 for r in self.results.values() if r['passed'])
        failed_categories = total_categories - passed_categories
        
        return {
            'total_categories': total_categories,
            'passed_categories': passed_categories,
            'failed_categories': failed_categories,
            'success_rate': (passed_categories / total_categories) * 100 if total_categories > 0 else 0
        }
    
    def generate_report(self) -> str:
        """Generate detailed test report."""
        if not self.results:
            return "No test results available."
        
        summary = self._generate_summary()
        
        report_lines = [
            "🧪 Test Suite Execution Report",
            "=" * 50,
            f"📅 Executed: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"📊 Categories: {summary['total_categories']}",
            f"✅ Passed: {summary['passed_categories']}",
            f"❌ Failed: {summary['failed_categories']}",
            f"📈 Success Rate: {summary['success_rate']:.1f}%",
            "",
            "📋 Category Details:",
            ""
        ]
        
        for category, result in self.results.items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            report_lines.append(f"  {category:12} | {status} | {result['duration']:.2f}s")
            
            if not result['passed'] and result['stderr']:
                report_lines.append(f"    Error: {result['stderr'][:100]}...")
        
        return "\n".join(report_lines)

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Test Suite Runner")
    parser.add_argument('--category', '-c', 
                       choices=['unit', 'integration', 'api', 'database', 'security', 'performance', 'all'],
                       default='all', help='Test category to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage analysis')
    parser.add_argument('--output', '-o', help='Output report to file')
    
    args = parser.parse_args()
    
    runner = TestSuiteRunner()
    
    try:
        if args.coverage:
            coverage_result = runner.run_with_coverage()
            print("📊 Coverage Analysis Complete")
            if not coverage_result['coverage_passed']:
                print("❌ Coverage requirements not met")
                sys.exit(1)
        
        categories = None if args.category == 'all' else [args.category]
        results = runner.run_all_tests(categories, args.verbose)
        
        report = runner.generate_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to {args.output}")
        
        print("\n" + report)
        
        # Exit with appropriate code
        if all(r['passed'] for r in runner.results.values()):
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## 🎯 Testing Best Practices

### Test Organization
- **Separate files** for different test types
- **Descriptive test names** that explain what is being tested
- **Arrange-Act-Assert** pattern in all tests
- **Fixtures for reusable test data** and setup
- **Parameterized tests** for testing multiple scenarios

### Test Data Management
```python
# conftest.py - Shared test fixtures
import pytest
from app import create_app, db

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(config_name='testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def sample_user():
    """Create sample user data."""
    return {
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'secure_password123'
    }
```

### Continuous Integration
```yaml
# .github/workflows/testing.yml
name: Comprehensive Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run comprehensive test suite
      run: |
        python tests/test_suite_runner.py --coverage --verbose
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v1
```

This testing framework template provides:
- **Comprehensive test coverage** across all application layers
- **Automated test execution** with detailed reporting
- **Performance and security validation** built-in
- **Easy adaptation** for different application types
- **CI/CD integration** for continuous quality assurance

Adapt the specific test implementations based on your application's technology stack and requirements.