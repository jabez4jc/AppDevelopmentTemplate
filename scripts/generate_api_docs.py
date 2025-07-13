#!/usr/bin/env python3
"""
Automatic API Documentation Generator

Generates comprehensive API documentation from code annotations and schemas.
Prevents technical debt by keeping documentation synchronized with code.
"""

import json
import yaml
import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class APIDocumentationGenerator:
    """Generate comprehensive API documentation with zero technical debt."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.framework = self.detect_framework()
        self.docs_dir = self.project_root / "docs" / "api"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
    def detect_framework(self) -> str:
        """Detect the web framework being used."""
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "requirements-dev.txt",
            self.project_root / "pyproject.toml"
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                content = req_file.read_text().lower()
                if "fastapi" in content:
                    return "fastapi"
                elif "flask-restx" in content:
                    return "flask-restx"
                elif "djangorestframework" in content:
                    return "django-drf"
                elif "flask" in content:
                    return "flask"
        
        # Check for Python files with framework imports
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "from fastapi import" in content or "import fastapi" in content:
                    return "fastapi"
                elif "from flask_restx import" in content:
                    return "flask-restx"
                elif "from rest_framework" in content:
                    return "django-drf"
                elif "from flask import" in content:
                    return "flask"
            except:
                continue
        
        return "unknown"
    
    def generate_documentation(self) -> None:
        """Generate complete API documentation suite."""
        print(f"🔍 Detected framework: {self.framework}")
        print(f"📁 Generating documentation in: {self.docs_dir}")
        
        try:
            # Generate OpenAPI specification
            openapi_spec = self.generate_openapi_spec()
            
            if not openapi_spec:
                print("❌ Could not generate OpenAPI specification")
                return
            
            # Save specifications in multiple formats
            self._save_specifications(openapi_spec)
            
            # Generate human-readable documentation
            self._generate_markdown_docs(openapi_spec)
            
            # Generate integration examples
            self._generate_integration_examples(openapi_spec)
            
            # Generate SDK templates
            self._generate_sdk_templates(openapi_spec)
            
            # Generate test templates
            self._generate_test_templates(openapi_spec)
            
            # Generate validation scripts
            self._generate_validation_scripts(openapi_spec)
            
            print("✅ API documentation generation complete!")
            self._print_summary()
            
        except Exception as e:
            print(f"❌ Error generating documentation: {e}")
            raise
    
    def generate_openapi_spec(self) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI 3.0 specification based on detected framework."""
        
        if self.framework == "fastapi":
            return self._generate_fastapi_spec()
        elif self.framework == "flask-restx":
            return self._generate_flask_restx_spec()
        elif self.framework == "django-drf":
            return self._generate_django_spec()
        elif self.framework == "flask":
            return self._generate_flask_spec()
        else:
            return self._generate_generic_spec()
    
    def _generate_fastapi_spec(self) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI spec for FastAPI applications."""
        print("🚀 Generating FastAPI OpenAPI specification...")
        
        # Find the main FastAPI app
        app_file = self._find_fastapi_app()
        if not app_file:
            print("❌ Could not find FastAPI app instance")
            return None
        
        try:
            # Import and extract OpenAPI spec
            spec_extractor = f'''
import sys
import json
sys.path.insert(0, "{self.project_root}")

try:
    from {app_file.stem} import app
    print(json.dumps(app.openapi()))
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
'''
            
            result = subprocess.run(
                [sys.executable, "-c", spec_extractor],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0 and result.stdout.strip():
                spec = json.loads(result.stdout)
                return self._enhance_openapi_spec(spec)
            else:
                print(f"❌ Error extracting FastAPI spec: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating FastAPI spec: {e}")
            return None
    
    def _find_fastapi_app(self) -> Optional[Path]:
        """Find the main FastAPI application file."""
        app_files = [
            "app.py",
            "main.py",
            "app/main.py",
            "app/app.py",
            "src/main.py",
            "src/app.py"
        ]
        
        for app_file in app_files:
            file_path = self.project_root / app_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    if "FastAPI(" in content and ("app = " in content or "application = " in content):
                        return file_path
                except:
                    continue
        
        # Search for any Python file with FastAPI app
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "FastAPI(" in content and ("app = " in content or "application = " in content):
                    return py_file
            except:
                continue
        
        return None
    
    def _generate_flask_restx_spec(self) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI spec for Flask-RESTX applications."""
        print("🌶️ Generating Flask-RESTX OpenAPI specification...")
        
        # Flask-RESTX has built-in Swagger support
        # This would extract the swagger.json from the running app
        return self._generate_generic_spec()
    
    def _generate_django_spec(self) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI spec for Django REST Framework applications."""
        print("🎸 Generating Django REST Framework OpenAPI specification...")
        
        # DRF with drf-yasg or drf-spectacular
        return self._generate_generic_spec()
    
    def _generate_flask_spec(self) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI spec for Flask applications."""
        print("🌶️ Generating Flask OpenAPI specification...")
        
        # Analyze Flask routes and generate spec
        return self._analyze_flask_routes()
    
    def _analyze_flask_routes(self) -> Dict[str, Any]:
        """Analyze Flask routes to generate OpenAPI spec."""
        spec = self._get_base_spec()
        
        # Find Flask app and analyze routes
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                routes = self._extract_flask_routes(content)
                
                for route in routes:
                    self._add_route_to_spec(spec, route)
                    
            except Exception as e:
                continue
        
        return spec
    
    def _extract_flask_routes(self, content: str) -> List[Dict[str, Any]]:
        """Extract Flask routes from Python file content."""
        routes = []
        
        # Regex patterns for Flask routes
        route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)'
        func_pattern = r'def\s+(\w+)\([^)]*\):'
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for route decorator
            route_match = re.search(route_pattern, line)
            if route_match:
                path = route_match.group(1)
                methods_str = route_match.group(2) or "'GET'"
                methods = [m.strip('\'"') for m in methods_str.split(',')]
                
                # Look for function definition on next lines
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('def'):
                    j += 1
                
                if j < len(lines):
                    func_match = re.search(func_pattern, lines[j])
                    if func_match:
                        func_name = func_match.group(1)
                        
                        # Extract docstring if available
                        docstring = self._extract_docstring(lines, j + 1)
                        
                        routes.append({
                            'path': path,
                            'methods': methods,
                            'function': func_name,
                            'docstring': docstring
                        })
            
            i += 1
        
        return routes
    
    def _extract_docstring(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract docstring from function."""
        if start_line >= len(lines):
            return None
        
        # Look for docstring
        i = start_line
        while i < len(lines) and not lines[i].strip():
            i += 1
        
        if i < len(lines):
            line = lines[i].strip()
            if line.startswith('"""') or line.startswith("'''"):
                quote = line[:3]
                docstring_lines = [line[3:]]
                
                if line.endswith(quote) and len(line) > 6:
                    # Single line docstring
                    return line[3:-3].strip()
                
                # Multi-line docstring
                i += 1
                while i < len(lines):
                    line = lines[i].strip()
                    if line.endswith(quote):
                        docstring_lines.append(line[:-3])
                        break
                    docstring_lines.append(line)
                    i += 1
                
                return '\n'.join(docstring_lines).strip()
        
        return None
    
    def _add_route_to_spec(self, spec: Dict[str, Any], route: Dict[str, Any]) -> None:
        """Add route information to OpenAPI spec."""
        path = route['path']
        
        if path not in spec['paths']:
            spec['paths'][path] = {}
        
        for method in route['methods']:
            method_lower = method.lower()
            
            operation = {
                'summary': route.get('docstring', f'{method} {path}').split('\n')[0],
                'operationId': f"{method_lower}_{route['function']}",
                'responses': {
                    '200': {
                        'description': 'Successful response',
                        'content': {
                            'application/json': {
                                'schema': {'type': 'object'}
                            }
                        }
                    }
                }
            }
            
            if route.get('docstring'):
                operation['description'] = route['docstring']
            
            # Add request body for POST/PUT/PATCH
            if method_lower in ['post', 'put', 'patch']:
                operation['requestBody'] = {
                    'content': {
                        'application/json': {
                            'schema': {'type': 'object'}
                        }
                    }
                }
            
            spec['paths'][path][method_lower] = operation
    
    def _enhance_openapi_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance OpenAPI specification with additional metadata and examples."""
        
        # Add comprehensive server information
        spec['servers'] = [
            {
                'url': 'http://localhost:8000',
                'description': 'Development server'
            },
            {
                'url': 'http://localhost:5000',
                'description': 'Alternative development server'
            },
            {
                'url': 'https://api.example.com',
                'description': 'Production server'
            }
        ]
        
        # Enhance info section
        info = spec.get('info', {})
        spec['info'] = {
            **info,
            'contact': {
                'name': 'API Support',
                'email': 'api-support@example.com',
                'url': 'https://example.com/support'
            },
            'license': {
                'name': 'MIT',
                'url': 'https://opensource.org/licenses/MIT'
            },
            'termsOfService': 'https://example.com/terms'
        }
        
        # Add security schemes if not present
        if 'components' not in spec:
            spec['components'] = {}
        
        if 'securitySchemes' not in spec['components']:
            spec['components']['securitySchemes'] = {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                },
                'apiKey': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'X-API-Key'
                }
            }
        
        # Add tags for organization
        if 'tags' not in spec:
            spec['tags'] = self._generate_tags_from_paths(spec.get('paths', {}))
        
        # Enhance paths with examples
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                self._enhance_operation(operation)
        
        return spec
    
    def _generate_tags_from_paths(self, paths: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate tags from API paths."""
        tags = set()
        
        for path in paths.keys():
            # Extract potential tag from path
            parts = path.strip('/').split('/')
            if parts and parts[0]:
                # Remove 'api' prefix if present
                tag = parts[1] if parts[0] == 'api' and len(parts) > 1 else parts[0]
                tags.add(tag)
        
        return [{'name': tag, 'description': f'{tag.title()} operations'} for tag in sorted(tags)]
    
    def _enhance_operation(self, operation: Dict[str, Any]) -> None:
        """Enhance individual operation with examples and better documentation."""
        
        # Add examples to request body
        if 'requestBody' in operation:
            for content_type, content in operation['requestBody'].get('content', {}).items():
                if 'schema' in content and 'examples' not in content:
                    content['examples'] = self._generate_examples_from_schema(content['schema'])
        
        # Add examples to responses
        for status_code, response in operation.get('responses', {}).items():
            for content_type, content in response.get('content', {}).items():
                if 'schema' in content and 'examples' not in content:
                    content['examples'] = self._generate_response_examples(status_code, content['schema'])
    
    def _generate_examples_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic examples from schema definition."""
        examples = {}
        
        if schema.get('type') == 'object':
            # Generate comprehensive example
            example_data = self._create_example_from_schema(schema)
            examples['example_1'] = {
                'summary': 'Valid request example',
                'description': 'A complete example with all available fields',
                'value': example_data
            }
            
            # Generate minimal example if required fields exist
            if 'required' in schema:
                minimal_data = self._create_minimal_example(schema)
                examples['minimal_example'] = {
                    'summary': 'Minimal request example',
                    'description': 'Example with only required fields',
                    'value': minimal_data
                }
        
        return examples
    
    def _generate_response_examples(self, status_code: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response examples based on status code."""
        examples = {}
        
        if status_code.startswith('2'):  # Success responses
            examples['success'] = {
                'summary': 'Successful response',
                'value': self._create_example_from_schema(schema)
            }
        elif status_code.startswith('4'):  # Client errors
            examples['error'] = {
                'summary': 'Error response',
                'value': {
                    'error': 'Bad Request',
                    'message': 'Invalid input provided',
                    'details': ['Field validation failed']
                }
            }
        elif status_code.startswith('5'):  # Server errors
            examples['server_error'] = {
                'summary': 'Server error response',
                'value': {
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred'
                }
            }
        
        return examples
    
    def _create_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Create realistic example data from schema."""
        if schema.get('type') == 'object':
            example = {}
            properties = schema.get('properties', {})
            
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._create_example_value(prop_name, prop_schema)
            
            return example
        elif schema.get('type') == 'array':
            item_schema = schema.get('items', {'type': 'string'})
            return [self._create_example_value('item', item_schema)]
        else:
            return self._create_example_value('value', schema)
    
    def _create_minimal_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create example with only required fields."""
        example = {}
        required_fields = schema.get('required', [])
        properties = schema.get('properties', {})
        
        for field_name in required_fields:
            if field_name in properties:
                example[field_name] = self._create_example_value(field_name, properties[field_name])
        
        return example
    
    def _create_example_value(self, field_name: str, schema: Dict[str, Any]) -> Any:
        """Create example value for a specific field based on name and schema."""
        field_type = schema.get('type', 'string')
        format_type = schema.get('format')
        
        # Use example from schema if available
        if 'example' in schema:
            return schema['example']
        
        # Type and format specific examples
        if field_type == 'string':
            if format_type == 'email':
                return 'user@example.com'
            elif format_type == 'date':
                return '2023-12-01'
            elif format_type == 'date-time':
                return '2023-12-01T10:00:00Z'
            elif format_type == 'uri':
                return 'https://example.com'
            elif 'password' in field_name.lower():
                return 'SecurePassword123!'
            elif 'email' in field_name.lower():
                return 'user@example.com'
            elif 'name' in field_name.lower():
                return 'John Doe'
            elif 'title' in field_name.lower():
                return 'Example Title'
            elif 'description' in field_name.lower():
                return 'This is an example description'
            elif field_name.endswith('_id') or field_name == 'id':
                return 'abc123'
            else:
                return f'example_{field_name}'
        
        elif field_type == 'integer':
            if 'age' in field_name.lower():
                return 25
            elif 'count' in field_name.lower():
                return 10
            elif 'port' in field_name.lower():
                return 8080
            elif field_name.endswith('_id') or field_name == 'id':
                return 123
            else:
                return 42
        
        elif field_type == 'number':
            if 'price' in field_name.lower():
                return 19.99
            elif 'percentage' in field_name.lower():
                return 75.5
            else:
                return 3.14
        
        elif field_type == 'boolean':
            return True
        
        elif field_type == 'array':
            item_schema = schema.get('items', {'type': 'string'})
            return [self._create_example_value('item', item_schema)]
        
        elif field_type == 'object':
            return self._create_example_from_schema(schema)
        
        return None
    
    def _get_base_spec(self) -> Dict[str, Any]:
        """Get base OpenAPI specification structure."""
        return {
            'openapi': '3.0.0',
            'info': {
                'title': 'API Documentation',
                'version': '1.0.0',
                'description': 'Comprehensive API documentation generated automatically'
            },
            'paths': {},
            'components': {
                'schemas': {},
                'securitySchemes': {}
            }
        }
    
    def _generate_generic_spec(self) -> Dict[str, Any]:
        """Generate basic OpenAPI spec for unknown or unsupported frameworks."""
        print("🔧 Generating generic OpenAPI specification...")
        
        spec = self._get_base_spec()
        
        # Add basic health check endpoint
        spec['paths']['/health'] = {
            'get': {
                'summary': 'Health check endpoint',
                'description': 'Check if the API is running',
                'responses': {
                    '200': {
                        'description': 'API is healthy',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'status': {'type': 'string', 'example': 'healthy'},
                                        'timestamp': {'type': 'string', 'format': 'date-time'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return spec
    
    def _save_specifications(self, spec: Dict[str, Any]) -> None:
        """Save OpenAPI specification in multiple formats."""
        
        # JSON format
        with open(self.docs_dir / 'openapi.json', 'w') as f:
            json.dump(spec, f, indent=2, sort_keys=True)
        
        # YAML format
        with open(self.docs_dir / 'openapi.yaml', 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        
        # Pretty-printed JSON for development
        with open(self.docs_dir / 'openapi-pretty.json', 'w') as f:
            json.dump(spec, f, indent=4, sort_keys=True)
        
        print(f"✅ OpenAPI specifications saved in multiple formats")
    
    def _generate_markdown_docs(self, spec: Dict[str, Any]) -> None:
        """Generate comprehensive human-readable markdown documentation."""
        
        md_content = self._generate_api_reference(spec)
        
        with open(self.docs_dir / 'API_REFERENCE.md', 'w') as f:
            f.write(md_content)
        
        # Generate separate files for different sections
        self._generate_authentication_docs(spec)
        self._generate_error_handling_docs(spec)
        self._generate_getting_started_docs(spec)
        
        print(f"✅ Markdown documentation generated")
    
    def _generate_api_reference(self, spec: Dict[str, Any]) -> str:
        """Generate comprehensive API reference documentation."""
        
        info = spec.get('info', {})
        
        md_content = f"""# {info.get('title', 'API')} Documentation

## Overview
{info.get('description', 'Comprehensive API documentation')}

**Version:** {info.get('version', '1.0.0')}

"""
        
        # Contact information
        if 'contact' in info:
            contact = info['contact']
            md_content += "## Contact Information\n"
            if 'name' in contact:
                md_content += f"**Support Team:** {contact['name']}\n"
            if 'email' in contact:
                md_content += f"**Email:** [{contact['email']}](mailto:{contact['email']})\n"
            if 'url' in contact:
                md_content += f"**Support URL:** [{contact['url']}]({contact['url']})\n"
            md_content += "\n"
        
        # Server information
        if 'servers' in spec:
            md_content += "## Base URLs\n\n"
            for server in spec['servers']:
                md_content += f"- **{server['description']}:** `{server['url']}`\n"
            md_content += "\n"
        
        # Authentication
        if 'components' in spec and 'securitySchemes' in spec['components']:
            md_content += "## Authentication\n\n"
            for scheme_name, scheme in spec['components']['securitySchemes'].items():
                md_content += f"### {scheme_name}\n\n"
                md_content += f"**Type:** {scheme['type']}\n\n"
                
                if scheme['type'] == 'http':
                    md_content += f"**Scheme:** {scheme.get('scheme', 'basic')}\n"
                    if 'bearerFormat' in scheme:
                        md_content += f"**Bearer Format:** {scheme['bearerFormat']}\n"
                elif scheme['type'] == 'apiKey':
                    md_content += f"**Location:** {scheme['in']}\n"
                    md_content += f"**Parameter Name:** {scheme['name']}\n"
                
                md_content += "\n"
        
        # Endpoints
        md_content += "## Endpoints\n\n"
        
        # Group endpoints by tags
        tagged_paths = self._group_paths_by_tags(spec)
        
        for tag, paths in tagged_paths.items():
            md_content += f"### {tag.title()}\n\n"
            
            for path, methods in paths.items():
                for method, operation in methods.items():
                    md_content += self._format_endpoint_documentation(path, method, operation)
                    md_content += "\n---\n\n"
        
        return md_content
    
    def _group_paths_by_tags(self, spec: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Group API paths by their tags."""
        tagged_paths = {}
        
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                tags = operation.get('tags', ['General'])
                
                for tag in tags:
                    if tag not in tagged_paths:
                        tagged_paths[tag] = {}
                    if path not in tagged_paths[tag]:
                        tagged_paths[tag][path] = {}
                    tagged_paths[tag][path][method] = operation
        
        return tagged_paths
    
    def _format_endpoint_documentation(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Format individual endpoint documentation."""
        
        md_content = f"#### {method.upper()} {path}\n\n"
        
        # Summary and description
        if 'summary' in operation:
            md_content += f"**{operation['summary']}**\n\n"
        
        if 'description' in operation:
            md_content += f"{operation['description']}\n\n"
        
        # Parameters
        if 'parameters' in operation:
            md_content += "**Parameters:**\n\n"
            md_content += "| Name | Location | Type | Required | Description |\n"
            md_content += "|------|----------|------|----------|-------------|\n"
            
            for param in operation['parameters']:
                required = "✅" if param.get('required', False) else "❌"
                param_type = param.get('schema', {}).get('type', 'string')
                md_content += f"| `{param['name']}` | {param['in']} | {param_type} | {required} | {param.get('description', 'No description')} |\n"
            
            md_content += "\n"
        
        # Request body
        if 'requestBody' in operation:
            md_content += "**Request Body:**\n\n"
            
            for content_type, content in operation['requestBody']['content'].items():
                md_content += f"Content-Type: `{content_type}`\n\n"
                
                # Schema information
                if 'schema' in content:
                    schema = content['schema']
                    md_content += "```json\n"
                    md_content += json.dumps(self._schema_to_example(schema), indent=2)
                    md_content += "\n```\n\n"
                
                # Examples
                if 'examples' in content:
                    md_content += "**Examples:**\n\n"
                    for example_name, example in content['examples'].items():
                        md_content += f"*{example.get('summary', example_name)}:*\n"
                        md_content += "```json\n"
                        md_content += json.dumps(example['value'], indent=2)
                        md_content += "\n```\n\n"
        
        # Responses
        if 'responses' in operation:
            md_content += "**Responses:**\n\n"
            
            for status_code, response in operation['responses'].items():
                md_content += f"**{status_code}** - {response.get('description', 'No description')}\n\n"
                
                if 'content' in response:
                    for content_type, content in response['content'].items():
                        if 'examples' in content:
                            for example_name, example in content['examples'].items():
                                md_content += f"*Example ({example.get('summary', 'Response')}):*\n"
                                md_content += "```json\n"
                                md_content += json.dumps(example['value'], indent=2)
                                md_content += "\n```\n\n"
                        elif 'schema' in content:
                            md_content += "```json\n"
                            md_content += json.dumps(self._schema_to_example(content['schema']), indent=2)
                            md_content += "\n```\n\n"
        
        return md_content
    
    def _schema_to_example(self, schema: Dict[str, Any]) -> Any:
        """Convert schema to example data."""
        return self._create_example_from_schema(schema)
    
    def _generate_authentication_docs(self, spec: Dict[str, Any]) -> None:
        """Generate detailed authentication documentation."""
        
        auth_content = """# Authentication Guide

This document provides comprehensive information about authenticating with the API.

## Overview

This API supports multiple authentication methods to ensure secure access to resources.

"""
        
        if 'components' in spec and 'securitySchemes' in spec['components']:
            auth_content += "## Available Authentication Methods\n\n"
            
            for scheme_name, scheme in spec['components']['securitySchemes'].items():
                auth_content += f"### {scheme_name}\n\n"
                
                if scheme['type'] == 'http' and scheme.get('scheme') == 'bearer':
                    auth_content += self._generate_bearer_auth_docs(scheme_name, scheme)
                elif scheme['type'] == 'apiKey':
                    auth_content += self._generate_api_key_docs(scheme_name, scheme)
                
                auth_content += "\n"
        
        with open(self.docs_dir / 'AUTHENTICATION.md', 'w') as f:
            f.write(auth_content)
    
    def _generate_bearer_auth_docs(self, scheme_name: str, scheme: Dict[str, Any]) -> str:
        """Generate Bearer token authentication documentation."""
        
        return f"""
**Type:** HTTP Bearer Token
**Format:** {scheme.get('bearerFormat', 'JWT')}

#### How to Use

1. Obtain a token by authenticating with your credentials
2. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
     https://api.example.com/endpoint
```

#### Example Code

**Python:**
```python
import requests

headers = {{
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
}}

response = requests.get('https://api.example.com/endpoint', headers=headers)
```

**JavaScript:**
```javascript
const response = await fetch('https://api.example.com/endpoint', {{
    headers: {{
        'Authorization': 'Bearer YOUR_TOKEN_HERE',
        'Content-Type': 'application/json'
    }}
}});
```

#### Token Expiration

Tokens typically expire after 24 hours. Make sure to handle token refresh in your application.
"""
    
    def _generate_api_key_docs(self, scheme_name: str, scheme: Dict[str, Any]) -> str:
        """Generate API Key authentication documentation."""
        
        return f"""
**Type:** API Key
**Location:** {scheme['in']}
**Parameter Name:** {scheme['name']}

#### How to Use

Include your API key in the {scheme['in']}:

```bash
curl -H "{scheme['name']}: YOUR_API_KEY_HERE" \\
     https://api.example.com/endpoint
```

#### Example Code

**Python:**
```python
import requests

headers = {{
    '{scheme['name']}': 'YOUR_API_KEY_HERE',
    'Content-Type': 'application/json'
}}

response = requests.get('https://api.example.com/endpoint', headers=headers)
```

**JavaScript:**
```javascript
const response = await fetch('https://api.example.com/endpoint', {{
    headers: {{
        '{scheme['name']}': 'YOUR_API_KEY_HERE',
        'Content-Type': 'application/json'
    }}
}});
```

#### Security Notes

- Keep your API key secure and never expose it in client-side code
- Rotate your API key regularly
- Use environment variables to store API keys
"""
    
    def _generate_error_handling_docs(self, spec: Dict[str, Any]) -> None:
        """Generate error handling documentation."""
        
        error_content = """# Error Handling Guide

This document explains how to handle errors when using the API.

## Standard Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error description",
  "details": ["Additional error details"],
  "timestamp": "2023-12-01T10:00:00Z",
  "request_id": "req_123456789"
}
```

## HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error occurred |

## Common Error Scenarios

### Authentication Errors

**Missing Token:**
```json
{
  "error": "Unauthorized",
  "message": "Authentication token required",
  "details": ["Include 'Authorization: Bearer TOKEN' header"]
}
```

**Invalid Token:**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token",
  "details": ["Please obtain a new authentication token"]
}
```

### Validation Errors

**Missing Required Fields:**
```json
{
  "error": "Bad Request",
  "message": "Validation failed",
  "details": [
    "Field 'name' is required",
    "Field 'email' must be a valid email address"
  ]
}
```

### Rate Limiting

**Rate Limit Exceeded:**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded",
  "details": ["Limit: 100 requests per hour", "Try again in 3600 seconds"]
}
```

## Error Handling Best Practices

### 1. Always Check Status Codes

```python
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    # Success
    result = response.json()
elif response.status_code == 400:
    # Bad request - fix your data
    error_info = response.json()
    print(f"Validation error: {error_info['message']}")
elif response.status_code == 401:
    # Unauthorized - refresh token
    refresh_authentication_token()
elif response.status_code == 429:
    # Rate limited - wait and retry
    time.sleep(60)
    # Retry request
else:
    # Other error
    print(f"Error {response.status_code}: {response.text}")
```

### 2. Implement Retry Logic

```python
import time
import random

def make_request_with_retry(url, data, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 429:
                # Rate limited - exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")
```

### 3. Log Errors for Debugging

```python
import logging

logger = logging.getLogger(__name__)

try:
    response = make_api_request(data)
except Exception as e:
    logger.error(f"API request failed: {e}", extra={
        'request_data': data,
        'response_status': getattr(e.response, 'status_code', None),
        'response_text': getattr(e.response, 'text', None)
    })
    raise
```
"""
        
        with open(self.docs_dir / 'ERROR_HANDLING.md', 'w') as f:
            f.write(error_content)
    
    def _generate_getting_started_docs(self, spec: Dict[str, Any]) -> None:
        """Generate getting started documentation."""
        
        info = spec.get('info', {})
        
        getting_started = f"""# Getting Started with {info.get('title', 'the API')}

Welcome to the {info.get('title', 'API')} documentation! This guide will help you get up and running quickly.

## Quick Start

### 1. Authentication

First, you'll need to authenticate with the API. See the [Authentication Guide](AUTHENTICATION.md) for detailed instructions.

### 2. Make Your First Request

Here's a simple example to get you started:

```bash
curl -X GET \\
  {spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']}/health \\
  -H 'Content-Type: application/json'
```

### 3. Handle the Response

A successful response will look like this:

```json
{{
  "status": "healthy",
  "timestamp": "2023-12-01T10:00:00Z"
}}
```

## SDKs and Libraries

We provide official SDKs for popular programming languages:

- [Python SDK](examples/python_client.py)
- [JavaScript SDK](examples/javascript_client.js)
- [cURL Examples](examples/curl_examples.sh)

## Common Use Cases

### Creating a Resource

```python
import requests

# Example: Create a new user
data = {{
    "name": "John Doe",
    "email": "john@example.com"
}}

response = requests.post(
    "{spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']}/users",
    json=data,
    headers={{"Authorization": "Bearer YOUR_TOKEN"}}
)

if response.status_code == 201:
    user = response.json()
    print(f"Created user: {{user['id']}}")
else:
    print(f"Error: {{response.status_code}} - {{response.text}}")
```

### Retrieving Resources

```python
# Example: Get user by ID
response = requests.get(
    "{spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']}/users/123",
    headers={{"Authorization": "Bearer YOUR_TOKEN"}}
)

if response.status_code == 200:
    user = response.json()
    print(f"User: {{user['name']}}")
```

### Updating Resources

```python
# Example: Update user
update_data = {{
    "name": "Jane Doe"
}}

response = requests.put(
    "{spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']}/users/123",
    json=update_data,
    headers={{"Authorization": "Bearer YOUR_TOKEN"}}
)

if response.status_code == 200:
    print("User updated successfully")
```

## Rate Limiting

This API implements rate limiting to ensure fair usage:

- **Rate Limit:** 1000 requests per hour per API key
- **Burst Limit:** 10 requests per second

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## Error Handling

Always check the HTTP status code and handle errors appropriately. See the [Error Handling Guide](ERROR_HANDLING.md) for detailed information.

## Testing

### Interactive API Explorer

Visit the interactive API documentation to explore and test endpoints:

- **Swagger UI:** [/docs](/docs)
- **ReDoc:** [/redoc](/redoc)

### Postman Collection

Download our Postman collection to quickly test the API:

[Download Postman Collection](postman_collection.json)

## Next Steps

1. Read the [API Reference](API_REFERENCE.md) for detailed endpoint documentation
2. Check out [Integration Examples](examples/) for your programming language
3. Review the [Authentication Guide](AUTHENTICATION.md) for security best practices
4. Explore the [Error Handling Guide](ERROR_HANDLING.md) for robust error handling

## Support

Need help? Here's how to get support:

- **Documentation:** You're reading it!
- **Examples:** Check the `examples/` directory
- **Issues:** Report bugs or request features
"""
        
        if 'contact' in info:
            contact = info['contact']
            if 'email' in contact:
                getting_started += f"- **Email Support:** [{contact['email']}](mailto:{contact['email']})\n"
            if 'url' in contact:
                getting_started += f"- **Support Portal:** [{contact['url']}]({contact['url']})\n"
        
        with open(self.docs_dir / 'GETTING_STARTED.md', 'w') as f:
            f.write(getting_started)
    
    def _generate_integration_examples(self, spec: Dict[str, Any]) -> None:
        """Generate integration examples in multiple languages."""
        
        examples_dir = self.docs_dir / 'examples'
        examples_dir.mkdir(exist_ok=True)
        
        # Generate examples for different languages
        self._generate_python_client(spec, examples_dir)
        self._generate_javascript_client(spec, examples_dir)
        self._generate_curl_examples(spec, examples_dir)
        self._generate_postman_collection(spec, examples_dir)
        
        print(f"✅ Integration examples generated")
    
    def _generate_python_client(self, spec: Dict[str, Any], examples_dir: Path) -> None:
        """Generate comprehensive Python client."""
        
        info = spec.get('info', {})
        title = info.get('title', 'API').replace(' ', '')
        
        python_client = f'''"""
{info.get('title', 'API')} Python Client

Comprehensive Python client for {info.get('title', 'the API')}.
Generated automatically from OpenAPI specification.

Installation:
    pip install requests

Usage:
    from {title.lower()}_client import {title}Client
    
    client = {title}Client(api_key="your_api_key")
    result = client.example_method()
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class {title}Error(Exception):
    """Base exception for {title} API errors."""
    pass


class {title}AuthError({title}Error):
    """Authentication related errors."""
    pass


class {title}ValidationError({title}Error):
    """Validation related errors."""
    pass


class {title}RateLimitError({title}Error):
    """Rate limiting related errors."""
    pass


class {title}Client:
    """
    Python client for {info.get('title', 'the API')}.
    
    Args:
        base_url: API base URL
        api_key: API key for authentication
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
    """
    
    def __init__(
        self,
        base_url: str = "{spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']}",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set up session
        self.session = requests.Session()
        
        # Configure authentication
        if api_key:
            self.session.headers.update({{"Authorization": f"Bearer {{api_key}}"}})
        
        # Set default headers
        self.session.headers.update({{
            "Content-Type": "application/json",
            "User-Agent": f"{title}-Python-Client/1.0.0"
        }})
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            timeout: Request timeout (overrides default)
        
        Returns:
            Dict containing response data
        
        Raises:
            {title}AuthError: Authentication failed
            {title}ValidationError: Validation failed
            {title}RateLimitError: Rate limit exceeded
            {title}Error: Other API errors
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        request_timeout = timeout or self.timeout
        
        for attempt in range(self.max_retries + 1):
            try:
                # Prepare request kwargs
                kwargs = {{
                    'timeout': request_timeout,
                    'params': params
                }}
                
                if data is not None:
                    kwargs['json'] = data
                
                # Make request
                response = self.session.request(method, url, **kwargs)
                
                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        wait_time = (2 ** attempt) + (attempt * 0.1)
                        logger.warning(f"Rate limited. Waiting {{wait_time:.1f}}s before retry {{attempt + 1}}/{{self.max_retries}}")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise {title}RateLimitError("Rate limit exceeded. No more retries.")
                
                # Handle other errors
                if response.status_code == 401:
                    raise {title}AuthError("Authentication failed. Check your API key.")
                elif response.status_code == 400:
                    error_data = response.json() if response.content else {{"error": "Bad Request"}}
                    raise {title}ValidationError(f"Validation failed: {{error_data.get('message', 'Unknown error')}}")
                elif response.status_code >= 400:
                    error_data = response.json() if response.content else {{"error": "Unknown error"}}
                    raise {title}Error(f"API error {{response.status_code}}: {{error_data.get('message', 'Unknown error')}}")
                
                # Parse successful response
                if response.content:
                    return response.json()
                else:
                    return {{"success": True}}
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed: {{e}}. Retrying in {{wait_time}}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise {title}Error(f"Request failed after {{self.max_retries}} retries: {{e}}")
        
        raise {title}Error("Unexpected error: max retries exceeded")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Dict containing health status information
        """
        return self._make_request("GET", "/health")
'''

        # Add methods for each endpoint
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                method_name = self._generate_python_method_name(path, method, operation)
                method_code = self._generate_python_method(path, method, operation, method_name)
                python_client += method_code
        
        # Add example usage
        python_client += f'''

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = {title}Client(api_key="your_api_key_here")
    
    try:
        # Test health check
        health = client.health_check()
        print(f"API Status: {{health.get('status', 'unknown')}}")
        
        # Add more example calls here based on your API
        
    except {title}AuthError as e:
        print(f"Authentication error: {{e}}")
    except {title}ValidationError as e:
        print(f"Validation error: {{e}}")
    except {title}RateLimitError as e:
        print(f"Rate limit error: {{e}}")
    except {title}Error as e:
        print(f"API error: {{e}}")
'''
        
        with open(examples_dir / 'python_client.py', 'w') as f:
            f.write(python_client)
    
    def _generate_python_method_name(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Generate Python method name from operation."""
        operation_id = operation.get('operationId')
        if operation_id:
            # Convert camelCase to snake_case
            return re.sub(r'(?<!^)(?=[A-Z])', '_', operation_id).lower()
        
        # Generate from path and method
        path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
        method_name = f"{method.lower()}_{'_'.join(path_parts)}"
        
        # Clean up method name
        method_name = re.sub(r'[^a-zA-Z0-9_]', '_', method_name)
        method_name = re.sub(r'_+', '_', method_name)
        
        return method_name.strip('_')
    
    def _generate_python_method(self, path: str, method: str, operation: Dict[str, Any], method_name: str) -> str:
        """Generate Python method code for an operation."""
        
        # Extract parameters
        path_params = re.findall(r'\{([^}]+)\}', path)
        query_params = []
        
        if 'parameters' in operation:
            for param in operation['parameters']:
                if param['in'] == 'query':
                    query_params.append(param)
        
        # Generate method signature
        params = []
        for param_name in path_params:
            params.append(f"{param_name}: str")
        
        for param in query_params:
            param_name = param['name']
            param_type = self._python_type_from_schema(param.get('schema', {}))
            if param.get('required', False):
                params.append(f"{param_name}: {param_type}")
            else:
                params.append(f"{param_name}: Optional[{param_type}] = None")
        
        # Add data parameter for POST/PUT/PATCH
        if method.lower() in ['post', 'put', 'patch']:
            params.append("data: Optional[Dict[str, Any]] = None")
        
        signature = f"def {method_name}(self, {', '.join(params)}) -> Dict[str, Any]:"
        
        # Generate docstring
        summary = operation.get('summary', f'{method.upper()} {path}')
        description = operation.get('description', '')
        
        docstring = f'''        """
        {summary}
        
        {description}
        """'''
        
        # Generate method body
        endpoint_path = path
        for param_name in path_params:
            endpoint_path = endpoint_path.replace(f'{{{param_name}}}', f'{{{{ {param_name} }}}}')
        
        method_body = f'''
        endpoint = f"{endpoint_path}"
        
        # Prepare query parameters
        params = {{}}'''
        
        for param in query_params:
            param_name = param['name']
            method_body += f'''
        if {param_name} is not None:
            params['{param_name}'] = {param_name}'''
        
        if method.lower() in ['post', 'put', 'patch']:
            method_body += f'''
        
        return self._make_request("{method.upper()}", endpoint, params=params, data=data)'''
        else:
            method_body += f'''
        
        return self._make_request("{method.upper()}", endpoint, params=params)'''
        
        return f'''
    
    {signature}
{docstring}
{method_body}
'''
    
    def _python_type_from_schema(self, schema: Dict[str, Any]) -> str:
        """Convert OpenAPI schema type to Python type hint."""
        schema_type = schema.get('type', 'string')
        
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List[Any]',
            'object': 'Dict[str, Any]'
        }
        
        return type_mapping.get(schema_type, 'Any')
    
    def _generate_javascript_client(self, spec: Dict[str, Any], examples_dir: Path) -> None:
        """Generate comprehensive JavaScript client."""
        
        info = spec.get('info', {})
        title = info.get('title', 'API').replace(' ', '')
        
        js_client = f'''/**
 * {info.get('title', 'API')} JavaScript Client
 * 
 * Comprehensive JavaScript client for {info.get('title', 'the API')}.
 * Generated automatically from OpenAPI specification.
 * 
 * Compatible with Node.js and modern browsers.
 * 
 * Installation:
 *   npm install axios  # Optional: for better HTTP client
 * 
 * Usage:
 *   const client = new {title}Client({{ apiKey: 'your_api_key' }});
 *   const result = await client.exampleMethod();
 */

class {title}Error extends Error {{
    constructor(message, status = null, response = null) {{
        super(message);
        this.name = '{title}Error';
        this.status = status;
        this.response = response;
    }}
}}

class {title}AuthError extends {title}Error {{
    constructor(message = 'Authentication failed') {{
        super(message);
        this.name = '{title}AuthError';
    }}
}}

class {title}ValidationError extends {title}Error {{
    constructor(message = 'Validation failed', details = []) {{
        super(message);
        this.name = '{title}ValidationError';
        this.details = details;
    }}
}}

class {title}RateLimitError extends {title}Error {{
    constructor(message = 'Rate limit exceeded') {{
        super(message);
        this.name = '{title}RateLimitError';
    }}
}}

class {title}Client {{
    /**
     * Create a new API client.
     * 
     * @param {{Object}} options - Configuration options
     * @param {{string}} options.baseUrl - API base URL
     * @param {{string}} options.apiKey - API key for authentication
     * @param {{number}} options.timeout - Request timeout in milliseconds
     * @param {{number}} options.maxRetries - Maximum number of retries
     */
    constructor(options = {{}}) {{
        this.baseUrl = (options.baseUrl || '{spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']}').replace(/\/$/, '');
        this.apiKey = options.apiKey;
        this.timeout = options.timeout || 30000;
        this.maxRetries = options.maxRetries || 3;
        
        // Set up default headers
        this.defaultHeaders = {{
            'Content-Type': 'application/json',
            'User-Agent': '{title}-JavaScript-Client/1.0.0'
        }};
        
        if (this.apiKey) {{
            this.defaultHeaders['Authorization'] = `Bearer ${{this.apiKey}}`;
        }}
    }}
    
    /**
     * Make HTTP request with error handling and retries.
     * 
     * @param {{string}} method - HTTP method
     * @param {{string}} endpoint - API endpoint
     * @param {{Object}} options - Request options
     * @returns {{Promise<Object>}} Response data
     */
    async makeRequest(method, endpoint, options = {{}}) {{
        const url = `${{this.baseUrl}}/${{endpoint.replace(/^\//, '')}}`;
        const {{ params, data, timeout, headers = {{}} }} = options;
        
        // Prepare request configuration
        const config = {{
            method: method.toUpperCase(),
            headers: {{ ...this.defaultHeaders, ...headers }},
        }};
        
        // Add query parameters
        if (params) {{
            const searchParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {{
                if (value !== null && value !== undefined) {{
                    searchParams.append(key, value);
                }}
            }});
            
            if (searchParams.toString()) {{
                const separator = url.includes('?') ? '&' : '?';
                url += separator + searchParams.toString();
            }}
        }}
        
        // Add request body
        if (data) {{
            config.body = JSON.stringify(data);
        }}
        
        // Implement retry logic with exponential backoff
        for (let attempt = 0; attempt <= this.maxRetries; attempt++) {{
            try {{
                // Set up timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), timeout || this.timeout);
                config.signal = controller.signal;
                
                const response = await fetch(url, config);
                clearTimeout(timeoutId);
                
                // Handle rate limiting
                if (response.status === 429) {{
                    if (attempt < this.maxRetries) {{
                        const waitTime = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
                        console.warn(`Rate limited. Waiting ${{waitTime}}ms before retry ${{attempt + 1}}/${{this.maxRetries}}`);
                        await new Promise(resolve => setTimeout(resolve, waitTime));
                        continue;
                    } else {{
                        throw new {title}RateLimitError('Rate limit exceeded. No more retries.');
                    }}
                }}
                
                // Parse response
                let responseData;
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {{
                    responseData = await response.json();
                }} else {{
                    responseData = await response.text();
                }}
                
                // Handle errors
                if (!response.ok) {{
                    if (response.status === 401) {{
                        throw new {title}AuthError('Authentication failed. Check your API key.');
                    }} else if (response.status === 400) {{
                        const message = responseData?.message || 'Validation failed';
                        const details = responseData?.details || [];
                        throw new {title}ValidationError(message, details);
                    }} else {{
                        const message = responseData?.message || `HTTP error ${{response.status}}`;
                        throw new {title}Error(message, response.status, responseData);
                    }}
                }}
                
                return responseData;
                
            }} catch (error) {{
                if (error instanceof {title}Error) {{
                    throw error;
                }}
                
                if (attempt < this.maxRetries) {{
                    const waitTime = Math.pow(2, attempt) * 1000;
                    console.warn(`Request failed: ${{error.message}}. Retrying in ${{waitTime}}ms...`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    continue;
                }} else {{
                    throw new {title}Error(`Request failed after ${{this.maxRetries}} retries: ${{error.message}}`);
                }}
            }}
        }}
        
        throw new {title}Error('Unexpected error: max retries exceeded');
    }}
    
    /**
     * Check API health status.
     * 
     * @returns {{Promise<Object>}} Health status information
     */
    async healthCheck() {{
        return await this.makeRequest('GET', '/health');
    }}
'''

        # Add methods for each endpoint
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                method_name = self._generate_js_method_name(path, method, operation)
                method_code = self._generate_js_method(path, method, operation, method_name)
                js_client += method_code
        
        # Add example usage and export
        js_client += f'''
}}

// Example usage
async function example() {{
    const client = new {title}Client({{ apiKey: 'your_api_key_here' }});
    
    try {{
        // Test health check
        const health = await client.healthCheck();
        console.log('API Status:', health.status || 'unknown');
        
        // Add more example calls here based on your API
        
    }} catch (error) {{
        if (error instanceof {title}AuthError) {{
            console.error('Authentication error:', error.message);
        }} else if (error instanceof {title}ValidationError) {{
            console.error('Validation error:', error.message);
            console.error('Details:', error.details);
        }} else if (error instanceof {title}RateLimitError) {{
            console.error('Rate limit error:', error.message);
        }} else if (error instanceof {title}Error) {{
            console.error('API error:', error.message);
        }} else {{
            console.error('Unexpected error:', error);
        }}
    }}
}}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {{
    // Node.js
    module.exports = {{ {title}Client, {title}Error, {title}AuthError, {title}ValidationError, {title}RateLimitError }};
}} else if (typeof window !== 'undefined') {{
    // Browser
    window.{title}Client = {title}Client;
    window.{title}Error = {title}Error;
    window.{title}AuthError = {title}AuthError;
    window.{title}ValidationError = {title}ValidationError;
    window.{title}RateLimitError = {title}RateLimitError;
}}
'''
        
        with open(examples_dir / 'javascript_client.js', 'w') as f:
            f.write(js_client)
    
    def _generate_js_method_name(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Generate JavaScript method name from operation."""
        operation_id = operation.get('operationId')
        if operation_id:
            # Convert to camelCase
            return operation_id[0].lower() + operation_id[1:] if operation_id else 'unknownOperation'
        
        # Generate from path and method
        path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
        method_name = method.lower() + ''.join(part.title() for part in path_parts)
        
        # Clean up method name
        method_name = re.sub(r'[^a-zA-Z0-9]', '', method_name)
        
        return method_name
    
    def _generate_js_method(self, path: str, method: str, operation: Dict[str, Any], method_name: str) -> str:
        """Generate JavaScript method code for an operation."""
        
        # Extract parameters
        path_params = re.findall(r'\{([^}]+)\}', path)
        query_params = []
        
        if 'parameters' in operation:
            for param in operation['parameters']:
                if param['in'] == 'query':
                    query_params.append(param)
        
        # Generate method signature
        params = []
        for param_name in path_params:
            params.append(param_name)
        
        if query_params or method.lower() in ['post', 'put', 'patch']:
            params.append('options = {}')
        
        signature = f"async {method_name}({', '.join(params)})"
        
        # Generate docstring
        summary = operation.get('summary', f'{method.upper()} {path}')
        description = operation.get('description', '')
        
        jsdoc = f'''    /**
     * {summary}
     * 
     * {description}'''
        
        # Add parameter documentation
        for param_name in path_params:
            jsdoc += f'''
     * @param {{string}} {param_name} - Path parameter'''
        
        if query_params or method.lower() in ['post', 'put', 'patch']:
            jsdoc += f'''
     * @param {{Object}} options - Request options'''
            
            for param in query_params:
                param_name = param['name']
                param_desc = param.get('description', 'Query parameter')
                jsdoc += f'''
     * @param {{*}} options.{param_name} - {param_desc}'''
            
            if method.lower() in ['post', 'put', 'patch']:
                jsdoc += f'''
     * @param {{Object}} options.data - Request body data'''
        
        jsdoc += f'''
     * @returns {{Promise<Object>}} Response data
     */'''
        
        # Generate method body
        endpoint_path = path
        for param_name in path_params:
            endpoint_path = endpoint_path.replace(f'{{{param_name}}}', f'${{ {param_name} }}')
        
        method_body = f'''
        const endpoint = `{endpoint_path}`;
        
        // Extract options
        const {{ data, ...requestOptions }} = options;
        
        // Prepare query parameters
        const params = {{}};'''
        
        for param in query_params:
            param_name = param['name']
            method_body += f'''
        if (options.{param_name} !== undefined) {{
            params.{param_name} = options.{param_name};
        }}'''
        
        method_body += f'''
        
        return await this.makeRequest('{method.upper()}', endpoint, {{
            params,'''
        
        if method.lower() in ['post', 'put', 'patch']:
            method_body += '''
            data,'''
        
        method_body += '''
            ...requestOptions
        });'''
        
        return f'''
    
{jsdoc}
    {signature} {{
{method_body}
    }}
'''
    
    def _generate_curl_examples(self, spec: Dict[str, Any], examples_dir: Path) -> None:
        """Generate comprehensive cURL examples."""
        
        info = spec.get('info', {})
        base_url = spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']
        
        curl_examples = f'''#!/bin/bash
# {info.get('title', 'API')} cURL Examples
# Generated automatically from OpenAPI specification

# Configuration
BASE_URL="{base_url}"
API_KEY="your_api_key_here"

# Common headers
declare -a COMMON_HEADERS=(
    -H "Content-Type: application/json"
    -H "User-Agent: curl-examples/1.0.0"
)

# Authentication headers (uncomment the method you're using)
declare -a AUTH_HEADERS=(
    -H "Authorization: Bearer $API_KEY"
    # -H "X-API-Key: $API_KEY"
)

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Helper function to make requests with error handling
make_request() {{
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    echo -e "${{BLUE}}Testing: ${{description}}${{NC}}"
    echo -e "${{YELLOW}}${{method}} ${{endpoint}}${{NC}}"
    
    local curl_cmd="curl -s -w '\\nHTTP Status: %{{http_code}}\\nTime: %{{time_total}}s\\n' \\\\"
    curl_cmd+="\\n    -X ${{method}} \\\\"
    curl_cmd+="\\n    '${{BASE_URL}}${{endpoint}}' \\\\"
    curl_cmd+="\\n    \\\"${{COMMON_HEADERS[@]}}\\\" \\\\"
    curl_cmd+="\\n    \\\"${{AUTH_HEADERS[@]}}\\\""
    
    if [[ ! -z "$data" ]]; then
        curl_cmd+=" \\\\\\n    -d '$data'"
    fi
    
    echo -e "${{curl_cmd}}"
    echo
    
    # Execute the request
    if [[ ! -z "$data" ]]; then
        response=$(curl -s -w '\\nHTTP_STATUS:%{{http_code}}\\nTIME_TOTAL:%{{time_total}}' \\
            -X "$method" \\
            "$BASE_URL$endpoint" \\
            "${{COMMON_HEADERS[@]}}" \\
            "${{AUTH_HEADERS[@]}}" \\
            -d "$data")
    else
        response=$(curl -s -w '\\nHTTP_STATUS:%{{http_code}}\\nTIME_TOTAL:%{{time_total}}' \\
            -X "$method" \\
            "$BASE_URL$endpoint" \\
            "${{COMMON_HEADERS[@]}}" \\
            "${{AUTH_HEADERS[@]}}")
    fi
    
    # Parse response
    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    time_total=$(echo "$response" | grep "TIME_TOTAL:" | cut -d: -f2)
    response_body=$(echo "$response" | sed '/HTTP_STATUS:/d' | sed '/TIME_TOTAL:/d')
    
    # Display results
    if [[ $http_status -ge 200 && $http_status -lt 300 ]]; then
        echo -e "${{GREEN}}✅ Success (${{http_status}}) - ${{time_total}}s${{NC}}"
    elif [[ $http_status -ge 400 && $http_status -lt 500 ]]; then
        echo -e "${{RED}}❌ Client Error (${{http_status}}) - ${{time_total}}s${{NC}}"
    elif [[ $http_status -ge 500 ]]; then
        echo -e "${{RED}}💥 Server Error (${{http_status}}) - ${{time_total}}s${{NC}}"
    else
        echo -e "${{YELLOW}}⚠️  Unexpected Status (${{http_status}}) - ${{time_total}}s${{NC}}"
    fi
    
    echo "Response:"
    echo "$response_body" | python -m json.tool 2>/dev/null || echo "$response_body"
    echo
    echo "---"
    echo
}}

# Check if API key is set
if [[ "$API_KEY" == "your_api_key_here" ]]; then
    echo -e "${{YELLOW}}⚠️  Warning: Please set your API key in the API_KEY variable${{NC}}"
    echo
fi

# Health check
make_request "GET" "/health" "" "API Health Check"

'''
        
        # Add examples for each endpoint
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                description = operation.get('summary', f'{method.upper()} {path}')
                
                # Generate example request data
                example_data = ""
                if method.lower() in ['post', 'put', 'patch'] and 'requestBody' in operation:
                    example_obj = self._get_example_from_request_body(operation['requestBody'])
                    if example_obj:
                        example_data = json.dumps(example_obj, separators=(',', ':'))
                
                # Replace path parameters with example values
                example_path = path
                path_params = re.findall(r'\{([^}]+)\}', path)
                for param in path_params:
                    if 'id' in param.lower():
                        example_path = example_path.replace(f'{{{param}}}', '123')
                    else:
                        example_path = example_path.replace(f'{{{param}}}', 'example_value')
                
                curl_examples += f'''# {description}
make_request "{method.upper()}" "{example_path}" '{example_data}' "{description}"

'''
        
        # Add batch testing script
        curl_examples += '''
# Run all tests
echo -e "${BLUE}Running comprehensive API tests...${NC}"
echo

# You can add specific test scenarios here
# For example:
# make_request "POST" "/users" '{"name":"Test User","email":"test@example.com"}' "Create Test User"
# make_request "GET" "/users/123" "" "Get User by ID"
# make_request "PUT" "/users/123" '{"name":"Updated User"}' "Update User"
# make_request "DELETE" "/users/123" "" "Delete User"

echo -e "${GREEN}✅ All tests completed!${NC}"
'''
        
        with open(examples_dir / 'curl_examples.sh', 'w') as f:
            f.write(curl_examples)
        
        # Make the script executable
        try:
            import stat
            st = os.stat(examples_dir / 'curl_examples.sh')
            os.chmod(examples_dir / 'curl_examples.sh', st.st_mode | stat.S_IEXEC)
        except:
            pass
    
    def _generate_postman_collection(self, spec: Dict[str, Any], examples_dir: Path) -> None:
        """Generate Postman collection for API testing."""
        
        info = spec.get('info', {})
        base_url = spec.get('servers', [{'url': 'https://api.example.com'}])[0]['url']
        
        collection = {
            "info": {
                "name": info.get('title', 'API'),
                "description": info.get('description', 'API Collection'),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{api_key}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": base_url,
                    "type": "string"
                },
                {
                    "key": "api_key",
                    "value": "your_api_key_here",
                    "type": "string"
                }
            ],
            "item": []
        }
        
        # Add requests for each endpoint
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                request_item = {
                    "name": operation.get('summary', f'{method.upper()} {path}'),
                    "request": {
                        "method": method.upper(),
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}{path}",
                            "host": ["{{base_url}}"],
                            "path": [p for p in path.split('/') if p]
                        }
                    },
                    "response": []
                }
                
                # Add request body for POST/PUT/PATCH
                if method.lower() in ['post', 'put', 'patch'] and 'requestBody' in operation:
                    example_data = self._get_example_from_request_body(operation['requestBody'])
                    if example_data:
                        request_item["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example_data, indent=2),
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        }
                
                # Add query parameters
                if 'parameters' in operation:
                    query_params = [p for p in operation['parameters'] if p['in'] == 'query']
                    if query_params:
                        request_item["request"]["url"]["query"] = []
                        for param in query_params:
                            request_item["request"]["url"]["query"].append({
                                "key": param['name'],
                                "value": f"{{{{ {param['name']} }}}}",
                                "description": param.get('description', ''),
                                "disabled": not param.get('required', False)
                            })
                
                collection["item"].append(request_item)
        
        with open(examples_dir / 'postman_collection.json', 'w') as f:
            json.dump(collection, f, indent=2)
    
    def _generate_sdk_templates(self, spec: Dict[str, Any]) -> None:
        """Generate SDK generation templates and documentation."""
        
        sdk_content = f"""# SDK Generation Guide

This directory contains templates and instructions for generating SDKs in multiple programming languages from the OpenAPI specification.

## Available SDKs

### Official SDKs
- **Python**: [python_client.py](examples/python_client.py)
- **JavaScript**: [javascript_client.js](examples/javascript_client.js)

### Community SDKs
You can generate SDKs for additional languages using the OpenAPI specification:

## OpenAPI Generator

Install the OpenAPI Generator tool:

```bash
npm install @openapitools/openapi-generator-cli -g
# or
brew install openapi-generator
```

### Generate Python SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g python \\
    -o sdks/python \\
    --additional-properties=packageName=api_client,projectName=api-client
```

### Generate JavaScript/TypeScript SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g typescript-axios \\
    -o sdks/typescript \\
    --additional-properties=npmName=api-client,npmVersion=1.0.0
```

### Generate Java SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g java \\
    -o sdks/java \\
    --additional-properties=groupId=com.example,artifactId=api-client,artifactVersion=1.0.0
```

### Generate Go SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g go \\
    -o sdks/go \\
    --additional-properties=packageName=apiclient
```

### Generate C# SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g csharp \\
    -o sdks/csharp \\
    --additional-properties=packageName=ApiClient
```

### Generate PHP SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g php \\
    -o sdks/php \\
    --additional-properties=packageName=ApiClient
```

### Generate Ruby SDK
```bash
openapi-generator-cli generate \\
    -i docs/api/openapi.json \\
    -g ruby \\
    -o sdks/ruby \\
    --additional-properties=gemName=api_client
```

## Swagger Codegen (Alternative)

You can also use Swagger Codegen:

```bash
# Install Swagger Codegen
brew install swagger-codegen

# Generate SDK
swagger-codegen generate \\
    -i docs/api/openapi.json \\
    -l python \\
    -o sdks/python-swagger
```

## Custom SDK Development

For custom SDK development, use the provided templates as starting points:

1. **Python Template**: [examples/python_client.py](examples/python_client.py)
2. **JavaScript Template**: [examples/javascript_client.js](examples/javascript_client.js)

### SDK Best Practices

1. **Error Handling**: Implement comprehensive error handling
2. **Retry Logic**: Add exponential backoff for failed requests
3. **Rate Limiting**: Respect API rate limits
4. **Authentication**: Support multiple authentication methods
5. **Logging**: Provide configurable logging
6. **Testing**: Include comprehensive tests
7. **Documentation**: Generate API documentation

### SDK Testing

Test your generated SDKs against the API:

```bash
# Python SDK test
cd sdks/python
python -m pytest tests/

# JavaScript SDK test
cd sdks/javascript
npm test

# etc.
```

## Continuous Integration

Add SDK generation to your CI/CD pipeline:

```yaml
# .github/workflows/generate-sdks.yml
name: Generate SDKs

on:
  push:
    paths:
      - 'docs/api/openapi.json'

jobs:
  generate-sdks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Install OpenAPI Generator
        run: npm install @openapitools/openapi-generator-cli -g
      
      - name: Generate Python SDK
        run: |
          openapi-generator-cli generate \\
            -i docs/api/openapi.json \\
            -g python \\
            -o sdks/python
      
      - name: Generate JavaScript SDK
        run: |
          openapi-generator-cli generate \\
            -i docs/api/openapi.json \\
            -g typescript-axios \\
            -o sdks/typescript
      
      - name: Commit generated SDKs
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add sdks/
          git commit -m "Update generated SDKs" || exit 0
          git push
```

## Distribution

### Python SDK Distribution
```bash
cd sdks/python
python setup.py sdist bdist_wheel
twine upload dist/*
```

### JavaScript SDK Distribution
```bash
cd sdks/javascript
npm publish
```

### Documentation Updates

Update SDK documentation automatically when the OpenAPI spec changes by integrating with your documentation system.
"""
        
        with open(self.docs_dir / 'SDK_GENERATION.md', 'w') as f:
            f.write(sdk_content)
    
    def _generate_test_templates(self, spec: Dict[str, Any]) -> None:
        """Generate API test templates."""
        
        test_content = f"""# API Testing Framework

Comprehensive testing templates for the API based on the OpenAPI specification.

## Test Categories

### 1. Contract Testing
Verify that the API implementation matches the OpenAPI specification.

### 2. Integration Testing
Test complete workflows and business scenarios.

### 3. Performance Testing
Ensure API meets performance requirements.

### 4. Security Testing
Validate authentication, authorization, and input security.

## Python Test Framework

### pytest Configuration

```python
# conftest.py
import pytest
import requests
from typing import Dict, Any

@pytest.fixture
def api_client():
    \"\"\"Create API client for testing.\"\"\"
    from python_client import APIClient
    return APIClient(
        base_url="http://localhost:8000",
        api_key="test_api_key"
    )

@pytest.fixture
def test_data():
    \"\"\"Provide test data for API calls.\"\"\"
    return {{
        "valid_user": {{
            "name": "Test User",
            "email": "test@example.com"
        }},
        "invalid_user": {{
            "name": "",  # Invalid: empty name
            "email": "invalid-email"  # Invalid: malformed email
        }}
    }}

class TestAPIContract:
    \"\"\"Test API contract compliance.\"\"\"
    
    def test_openapi_spec_valid(self):
        \"\"\"Verify OpenAPI specification is valid.\"\"\"
        import yaml
        import jsonschema
        
        with open('docs/api/openapi.yaml') as f:
            spec = yaml.safe_load(f)
        
        # Validate against OpenAPI 3.0 schema
        # This would require the OpenAPI 3.0 schema
        assert spec['openapi'].startswith('3.0')
        assert 'info' in spec
        assert 'paths' in spec
    
    def test_health_endpoint(self, api_client):
        \"\"\"Test health check endpoint.\"\"\"
        response = api_client.health_check()
        
        assert 'status' in response
        assert response['status'] == 'healthy'
    
    def test_authentication_required(self, api_client):
        \"\"\"Test that protected endpoints require authentication.\"\"\"
        # Create client without API key
        from python_client import APIClient, APIAuthError
        
        unauth_client = APIClient(base_url="http://localhost:8000")
        
        with pytest.raises(APIAuthError):
            unauth_client.create_user({{"name": "Test", "email": "test@example.com"}})
    
    def test_input_validation(self, api_client, test_data):
        \"\"\"Test input validation for all endpoints.\"\"\"
        from python_client import APIValidationError
        
        with pytest.raises(APIValidationError):
            api_client.create_user(test_data["invalid_user"])
    
    def test_error_response_format(self, api_client):
        \"\"\"Test that error responses follow the standard format.\"\"\"
        from python_client import APIValidationError
        
        try:
            api_client.create_user({{"invalid": "data"}})
        except APIValidationError as e:
            # Error should have message
            assert hasattr(e, 'message')
            # Additional validation for error format
            pass

class TestAPIIntegration:
    \"\"\"Test complete API workflows.\"\"\"
    
    def test_user_lifecycle(self, api_client, test_data):
        \"\"\"Test complete user lifecycle: create, read, update, delete.\"\"\"
        user_data = test_data["valid_user"]
        
        # Create user
        created_user = api_client.create_user(user_data)
        assert 'id' in created_user
        user_id = created_user['id']
        
        # Read user
        retrieved_user = api_client.get_user(user_id)
        assert retrieved_user['name'] == user_data['name']
        assert retrieved_user['email'] == user_data['email']
        
        # Update user
        update_data = {{"name": "Updated Name"}}
        updated_user = api_client.update_user(user_id, update_data)
        assert updated_user['name'] == "Updated Name"
        
        # Delete user
        api_client.delete_user(user_id)
        
        # Verify deletion
        from python_client import APIError
        with pytest.raises(APIError):
            api_client.get_user(user_id)

class TestAPIPerformance:
    \"\"\"Test API performance requirements.\"\"\"
    
    def test_response_time_health_check(self, api_client):
        \"\"\"Test health check response time.\"\"\"
        import time
        
        start_time = time.time()
        api_client.health_check()
        duration = time.time() - start_time
        
        # Should respond within 500ms
        assert duration < 0.5
    
    def test_concurrent_requests(self, api_client):
        \"\"\"Test handling of concurrent requests.\"\"\"
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                result = api_client.health_check()
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start 10 concurrent requests
        threads = []
        start_time = time.time()
        
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 10
        
        # Should complete within reasonable time
        assert duration < 5.0

class TestAPISecurity:
    \"\"\"Test API security measures.\"\"\"
    
    def test_sql_injection_protection(self, api_client):
        \"\"\"Test protection against SQL injection.\"\"\"
        malicious_input = {{
            "name": "'; DROP TABLE users; --",
            "email": "test@example.com"
        }}
        
        from python_client import APIValidationError
        
        # Should reject malicious input
        with pytest.raises(APIValidationError):
            api_client.create_user(malicious_input)
    
    def test_xss_protection(self, api_client):
        \"\"\"Test protection against XSS attacks.\"\"\"
        xss_input = {{
            "name": "<script>alert('xss')</script>",
            "email": "test@example.com"
        }}
        
        from python_client import APIValidationError
        
        # Should reject or sanitize XSS input
        with pytest.raises(APIValidationError):
            api_client.create_user(xss_input)
    
    def test_rate_limiting(self, api_client):
        \"\"\"Test rate limiting enforcement.\"\"\"
        from python_client import APIRateLimitError
        
        # Make many requests quickly
        # This test might need adjustment based on actual rate limits
        for i in range(100):
            try:
                api_client.health_check()
            except APIRateLimitError:
                # Rate limit should trigger before 100 requests
                assert i > 10  # Should allow some requests before limiting
                break
        else:
            pytest.fail("Rate limiting not enforced")

# Run tests with coverage
# pytest --cov=api_client --cov-report=html tests/
```

## JavaScript Test Framework

### Jest Configuration

```javascript
// api.test.js
const {{ APIClient, APIError, APIAuthError, APIValidationError }} = require('../examples/javascript_client');

describe('API Contract Tests', () => {{
    let client;
    
    beforeEach(() => {{
        client = new APIClient({{
            baseUrl: 'http://localhost:8000',
            apiKey: 'test_api_key'
        }});
    }});
    
    test('health check returns valid response', async () => {{
        const response = await client.healthCheck();
        
        expect(response).toHaveProperty('status');
        expect(response.status).toBe('healthy');
    }});
    
    test('authentication required for protected endpoints', async () => {{
        const unauthClient = new APIClient({{
            baseUrl: 'http://localhost:8000'
        }});
        
        await expect(
            unauthClient.createUser({{ name: 'Test', email: 'test@example.com' }})
        ).rejects.toThrow(APIAuthError);
    }});
    
    test('input validation works correctly', async () => {{
        const invalidData = {{
            name: '',  // Invalid: empty name
            email: 'invalid-email'  // Invalid: malformed email
        }};
        
        await expect(
            client.createUser(invalidData)
        ).rejects.toThrow(APIValidationError);
    }});
}});

describe('API Integration Tests', () => {{
    let client;
    
    beforeEach(() => {{
        client = new APIClient({{
            baseUrl: 'http://localhost:8000',
            apiKey: 'test_api_key'
        }});
    }});
    
    test('complete user lifecycle', async () => {{
        const userData = {{
            name: 'Test User',
            email: 'test@example.com'
        }};
        
        // Create user
        const createdUser = await client.createUser(userData);
        expect(createdUser).toHaveProperty('id');
        const userId = createdUser.id;
        
        // Read user
        const retrievedUser = await client.getUser(userId);
        expect(retrievedUser.name).toBe(userData.name);
        expect(retrievedUser.email).toBe(userData.email);
        
        // Update user
        const updateData = {{ name: 'Updated Name' }};
        const updatedUser = await client.updateUser(userId, {{ data: updateData }});
        expect(updatedUser.name).toBe('Updated Name');
        
        // Delete user
        await client.deleteUser(userId);
        
        // Verify deletion
        await expect(
            client.getUser(userId)
        ).rejects.toThrow(APIError);
    }});
}});

describe('API Performance Tests', () => {{
    let client;
    
    beforeEach(() => {{
        client = new APIClient({{
            baseUrl: 'http://localhost:8000',
            apiKey: 'test_api_key'
        }});
    }});
    
    test('health check response time', async () => {{
        const startTime = Date.now();
        await client.healthCheck();
        const duration = Date.now() - startTime;
        
        // Should respond within 500ms
        expect(duration).toBeLessThan(500);
    }});
    
    test('concurrent requests handling', async () => {{
        const promises = [];
        const startTime = Date.now();
        
        // Start 10 concurrent requests
        for (let i = 0; i < 10; i++) {{
            promises.push(client.healthCheck());
        }}
        
        const results = await Promise.all(promises);
        const duration = Date.now() - startTime;
        
        // All requests should succeed
        expect(results).toHaveLength(10);
        results.forEach(result => {{
            expect(result).toHaveProperty('status');
        }});
        
        // Should complete within reasonable time
        expect(duration).toBeLessThan(5000);
    }});
}});

// Run with: npm test
```

## Load Testing with Artillery

```yaml
# artillery-config.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 20
    - duration: 60
      arrivalRate: 10
  defaults:
    headers:
      Authorization: 'Bearer test_api_key'
      Content-Type: 'application/json'

scenarios:
  - name: 'Health Check Load Test'
    weight: 50
    flow:
      - get:
          url: '/health'
          
  - name: 'User Operations Load Test'
    weight: 30
    flow:
      - post:
          url: '/users'
          json:
            name: 'Load Test User'
            email: 'loadtest@example.com'
          capture:
            - json: '$.id'
              as: 'userId'
      - get:
          url: '/users/{{ userId }}'
      - delete:
          url: '/users/{{ userId }}'
          
  - name: 'Read-only Operations Load Test'
    weight: 20
    flow:
      - get:
          url: '/users'
      - get:
          url: '/health'
```

Run load tests:
```bash
npm install -g artillery
artillery run artillery-config.yml
```

## Contract Testing with Pact

```python
# pact_test.py
import pytest
from pact import Consumer, Provider

pact = Consumer('api_client').has_pact_with(Provider('api_server'))

def test_health_check_contract():
    expected = {{
        'status': 'healthy',
        'timestamp': '2023-12-01T10:00:00Z'
    }}
    
    (pact
     .given('API is healthy')
     .upon_receiving('a health check request')
     .with_request('GET', '/health')
     .will_respond_with(200, body=expected))
    
    with pact:
        from python_client import APIClient
        client = APIClient(base_url=pact.uri)
        response = client.health_check()
        
        assert response['status'] == 'healthy'
```

## Running Tests

### Python
```bash
# Install dependencies
pip install pytest pytest-cov requests

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api_client --cov-report=html

# Run specific test category
pytest tests/test_contract.py -v
pytest tests/test_integration.py -v
pytest tests/test_performance.py -v
pytest tests/test_security.py -v
```

### JavaScript
```bash
# Install dependencies
npm install jest axios

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test api.test.js
```

### Load Testing
```bash
# Install Artillery
npm install -g artillery

# Run load tests
artillery run artillery-config.yml

# Generate detailed report
artillery run artillery-config.yml --output report.json
artillery report report.json
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      api:
        image: your-api-image
        ports:
          - 8000:8000
        env:
          NODE_ENV: test
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Python dependencies
        run: |
          pip install pytest pytest-cov requests
          pip install -r requirements-dev.txt
      
      - name: Run Python tests
        run: pytest tests/ --cov=api_client --cov-report=xml
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Install Node.js dependencies
        run: npm install jest axios artillery
      
      - name: Run JavaScript tests
        run: npm test
      
      - name: Run load tests
        run: artillery run artillery-config.yml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```
"""
        
        with open(self.docs_dir / 'API_TESTING.md', 'w') as f:
            f.write(test_content)
    
    def _generate_validation_scripts(self, spec: Dict[str, Any]) -> None:
        """Generate documentation validation scripts."""
        
        validation_script = '''#!/usr/bin/env python3
"""
API Documentation Validation Script

Validates that API documentation is consistent and up-to-date.
"""

import json
import yaml
import requests
import sys
from pathlib import Path
from typing import Dict, Any, List
import jsonschema


class APIDocumentationValidator:
    """Validate API documentation consistency."""
    
    def __init__(self, docs_dir: str, api_base_url: str = None):
        self.docs_dir = Path(docs_dir)
        self.api_base_url = api_base_url
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating API documentation...")
        
        # Check if documentation files exist
        self.validate_file_existence()
        
        # Validate OpenAPI specification
        self.validate_openapi_spec()
        
        # Validate examples
        self.validate_examples()
        
        # Cross-reference validation
        self.validate_cross_references()
        
        # If API is running, validate against live API
        if self.api_base_url:
            self.validate_against_live_api()
        
        # Report results
        self.report_results()
        
        return len(self.errors) == 0
    
    def validate_file_existence(self):
        """Validate that all required documentation files exist."""
        required_files = [
            'openapi.json',
            'openapi.yaml',
            'API_REFERENCE.md',
            'GETTING_STARTED.md',
            'AUTHENTICATION.md',
            'ERROR_HANDLING.md',
            'examples/python_client.py',
            'examples/javascript_client.js',
            'examples/curl_examples.sh'
        ]
        
        for file_path in required_files:
            full_path = self.docs_dir / file_path
            if not full_path.exists():
                self.errors.append(f"Missing required file: {file_path}")
            else:
                print(f"✅ Found: {file_path}")
    
    def validate_openapi_spec(self):
        """Validate OpenAPI specification."""
        openapi_file = self.docs_dir / 'openapi.json'
        
        if not openapi_file.exists():
            self.errors.append("OpenAPI specification file not found")
            return
        
        try:
            with open(openapi_file) as f:
                spec = json.load(f)
            
            # Basic structure validation
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field not in spec:
                    self.errors.append(f"Missing required field in OpenAPI spec: {field}")
            
            # Version validation
            if 'openapi' in spec:
                if not spec['openapi'].startswith('3.0'):
                    self.warnings.append(f"OpenAPI version {spec['openapi']} - consider using 3.0.x")
            
            # Info section validation
            if 'info' in spec:
                info_required = ['title', 'version']
                for field in info_required:
                    if field not in spec['info']:
                        self.errors.append(f"Missing required info field: {field}")
            
            # Paths validation
            if 'paths' in spec:
                if not spec['paths']:
                    self.warnings.append("No paths defined in OpenAPI spec")
                else:
                    self.validate_paths(spec['paths'])
            
            print(f"✅ OpenAPI specification basic validation passed")
            
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in OpenAPI spec: {e}")
        except Exception as e:
            self.errors.append(f"Error validating OpenAPI spec: {e}")
    
    def validate_paths(self, paths: Dict[str, Any]):
        """Validate individual paths in OpenAPI spec."""
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                self.errors.append(f"Invalid path definition: {path}")
                continue
            
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    self.errors.append(f"Invalid operation definition: {method} {path}")
                    continue
                
                # Check for required operation fields
                if 'responses' not in operation:
                    self.errors.append(f"Missing responses for {method} {path}")
                
                # Check for description/summary
                if 'summary' not in operation and 'description' not in operation:
                    self.warnings.append(f"Missing summary/description for {method} {path}")
                
                # Validate response codes
                if 'responses' in operation:
                    success_codes = [code for code in operation['responses'].keys() 
                                   if code.startswith('2')]
                    if not success_codes:
                        self.warnings.append(f"No success response defined for {method} {path}")
    
    def validate_examples(self):
        """Validate that examples are consistent and functional."""
        examples_dir = self.docs_dir / 'examples'
        
        if not examples_dir.exists():
            self.errors.append("Examples directory not found")
            return
        
        # Validate Python client
        python_client = examples_dir / 'python_client.py'
        if python_client.exists():
            try:
                # Basic syntax check
                with open(python_client) as f:
                    content = f.read()
                
                compile(content, python_client, 'exec')
                print("✅ Python client syntax valid")
                
                # Check for required imports
                required_imports = ['requests', 'json']
                for imp in required_imports:
                    if f"import {imp}" not in content:
                        self.warnings.append(f"Python client missing import: {imp}")
                
            except SyntaxError as e:
                self.errors.append(f"Python client syntax error: {e}")
            except Exception as e:
                self.warnings.append(f"Could not validate Python client: {e}")
        
        # Validate JavaScript client
        js_client = examples_dir / 'javascript_client.js'
        if js_client.exists():
            try:
                with open(js_client) as f:
                    content = f.read()
                
                # Basic checks for JavaScript
                if 'class ' not in content:
                    self.warnings.append("JavaScript client doesn't appear to use ES6 classes")
                
                if 'fetch(' not in content and 'axios' not in content:
                    self.warnings.append("JavaScript client missing HTTP client")
                
                print("✅ JavaScript client basic validation passed")
                
            except Exception as e:
                self.warnings.append(f"Could not validate JavaScript client: {e}")
    
    def validate_cross_references(self):
        """Validate cross-references between documentation files."""
        api_ref_file = self.docs_dir / 'API_REFERENCE.md'
        
        if not api_ref_file.exists():
            return
        
        try:
            with open(api_ref_file) as f:
                content = f.read()
            
            # Check for links to other documentation
            expected_links = [
                'AUTHENTICATION.md',
                'ERROR_HANDLING.md',
                'GETTING_STARTED.md'
            ]
            
            for link in expected_links:
                if link not in content:
                    self.warnings.append(f"API_REFERENCE.md missing link to {link}")
            
            print("✅ Cross-reference validation completed")
            
        except Exception as e:
            self.warnings.append(f"Could not validate cross-references: {e}")
    
    def validate_against_live_api(self):
        """Validate documentation against live API."""
        print(f"🌐 Validating against live API: {self.api_base_url}")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Health endpoint accessible")
            else:
                self.warnings.append(f"Health endpoint returned {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            self.warnings.append(f"Could not connect to API: {e}")
        
        # Validate OpenAPI spec endpoint
        try:
            response = requests.get(f"{self.api_base_url}/openapi.json", timeout=10)
            if response.status_code == 200:
                live_spec = response.json()
                
                # Compare with local spec
                local_spec_file = self.docs_dir / 'openapi.json'
                if local_spec_file.exists():
                    with open(local_spec_file) as f:
                        local_spec = json.load(f)
                    
                    if live_spec.get('info', {}).get('version') != local_spec.get('info', {}).get('version'):
                        self.warnings.append("API version mismatch between live API and documentation")
                    
                    print("✅ OpenAPI spec comparison completed")
                
            else:
                self.warnings.append("OpenAPI spec not available from live API")
                
        except Exception as e:
            self.warnings.append(f"Could not validate against live OpenAPI spec: {e}")
    
    def report_results(self):
        """Report validation results."""
        print("\\n" + "="*50)
        print("📋 VALIDATION REPORT")
        print("="*50)
        
        if self.errors:
            print(f"\\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\\n✅ All validation checks passed!")
        elif not self.errors:
            print(f"\\n✅ Validation passed with {len(self.warnings)} warnings")
        else:
            print(f"\\n❌ Validation failed with {len(self.errors)} errors and {len(self.warnings)} warnings")
        
        print("="*50)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate API documentation")
    parser.add_argument("--docs-dir", default="docs/api", help="Documentation directory")
    parser.add_argument("--api-url", help="Live API base URL for validation")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    validator = APIDocumentationValidator(args.docs_dir, args.api_url)
    
    success = validator.validate_all()
    
    if args.strict and validator.warnings:
        print("\\n❌ Strict mode: treating warnings as errors")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
'''
        
        with open(self.docs_dir / 'validate_docs.py', 'w') as f:
            f.write(validation_script)
        
        # Make script executable
        try:
            import stat
            st = os.stat(self.docs_dir / 'validate_docs.py')
            os.chmod(self.docs_dir / 'validate_docs.py', st.st_mode | stat.S_IEXEC)
        except:
            pass
    
    def _print_summary(self) -> None:
        """Print summary of generated documentation."""
        print(f"""
📚 API Documentation Generated Successfully!

📁 Documentation Location: {self.docs_dir}

📋 Generated Files:
   🔧 Specifications:
   • openapi.json           - Machine-readable API specification
   • openapi.yaml           - YAML format specification
   • openapi-pretty.json    - Pretty-printed JSON for development

   📖 Human Documentation:
   • API_REFERENCE.md       - Comprehensive API reference
   • GETTING_STARTED.md     - Quick start guide
   • AUTHENTICATION.md      - Authentication guide
   • ERROR_HANDLING.md      - Error handling guide

   💻 Integration Examples:
   • examples/python_client.py      - Complete Python client
   • examples/javascript_client.js  - Complete JavaScript client  
   • examples/curl_examples.sh      - cURL command examples
   • examples/postman_collection.json - Postman collection

   🛠️ Development Tools:
   • SDK_GENERATION.md      - SDK generation guide
   • API_TESTING.md         - Testing framework templates
   • validate_docs.py       - Documentation validation script

🚀 Next Steps:
1. Review generated documentation for accuracy
2. Test integration examples with your API
3. Set up automated documentation validation
4. Generate SDKs for your preferred languages
5. Add documentation validation to your CI/CD pipeline

💡 Pro Tips:
• Run 'python docs/api/validate_docs.py' to validate documentation
• Use the provided examples as starting points for client development
• Set up automatic documentation generation in your CI/CD pipeline
• Consider generating SDKs for multiple programming languages

📞 Integration Commands:
• Swagger UI: Available at /docs endpoint (if using FastAPI)
• Validation: python docs/api/validate_docs.py --api-url http://localhost:8000
• SDK Generation: See SDK_GENERATION.md for detailed instructions
""")


def main():
    """Main function to run the documentation generator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate comprehensive API documentation from code"
    )
    parser.add_argument(
        "--project-root", 
        default=".", 
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--output-dir", 
        default="docs/api", 
        help="Output directory for documentation (default: docs/api)"
    )
    parser.add_argument(
        "--framework",
        choices=["fastapi", "flask", "flask-restx", "django-drf", "auto"],
        default="auto",
        help="Web framework to target (default: auto-detect)"
    )
    parser.add_argument(
        "--api-url",
        help="Live API URL for validation (optional)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation after generation"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate documentation
        generator = APIDocumentationGenerator(args.project_root)
        
        # Override framework detection if specified
        if args.framework != "auto":
            generator.framework = args.framework
        
        generator.generate_documentation()
        
        # Run validation if requested
        if args.validate:
            print("\\n🔍 Running documentation validation...")
            
            validation_script = generator.docs_dir / 'validate_docs.py'
            if validation_script.exists():
                import subprocess
                cmd = [sys.executable, str(validation_script)]
                if args.api_url:
                    cmd.extend(['--api-url', args.api_url])
                
                result = subprocess.run(cmd)
                if result.returncode != 0:
                    print("❌ Documentation validation failed")
                    sys.exit(1)
                else:
                    print("✅ Documentation validation passed")
        
        print("\\n🎉 API documentation generation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error generating API documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()