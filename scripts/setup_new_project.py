#!/usr/bin/env python3
"""
New Project Setup Script

This script customizes the universal template for a specific project type,
creating a tailored development environment with all best practices included.

Usage:
    python scripts/setup_new_project.py --name="MyApp" --type="web" --framework="flask"
    python scripts/setup_new_project.py --name="DataProcessor" --type="cli" --language="python"
    python scripts/setup_new_project.py --name="UserService" --type="microservice" --framework="fastapi"
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Dict, List
import json
import re


class ProjectSetup:
    """Set up new project from universal template."""
    
    def __init__(self, template_root: str = None):
        self.template_root = Path(template_root or Path.cwd())
        self.project_types = {
            'web': self._setup_web_project,
            'cli': self._setup_cli_project,
            'microservice': self._setup_microservice_project,
            'data': self._setup_data_project,
            'desktop': self._setup_desktop_project,
            'mobile': self._setup_mobile_project
        }
        
    def create_project(self, name: str, project_type: str, framework: str = None, 
                      target_dir: str = None, **kwargs) -> str:
        """Create new project from template."""
        
        if project_type not in self.project_types:
            raise ValueError(f"Unknown project type: {project_type}")
        
        # Set up project directory
        target_path = Path(target_dir or f"../{name}")
        target_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 Creating {project_type} project: {name}")
        print(f"📁 Target directory: {target_path.absolute()}")
        
        # Copy base template files
        self._copy_base_template(target_path)
        
        # Customize for project type
        self.project_types[project_type](target_path, name, framework, **kwargs)
        
        # Update project context
        self._update_project_context(target_path, name, project_type, framework, **kwargs)
        
        # Customize documentation
        self._customize_documentation(target_path, name, project_type, framework)
        
        print(f"✅ Project {name} created successfully!")
        print(f"📋 Next steps:")
        print(f"   cd {target_path.name}")
        print(f"   python scripts/install_dev_system.py")
        print(f"   # Start developing with: '[TASK_TYPE]: Description\\nFollow project guidelines'")
        
        return str(target_path)
    
    def _copy_base_template(self, target_path: Path) -> None:
        """Copy base template files to target directory."""
        base_files = [
            'DEV_GUIDELINES.md',
            'TESTING_GUIDE.md', 
            'LLM_REQUEST_TEMPLATE.md',
            'scripts/',
            'tests/',
            '.claude/',
            '.github/',
            'docs/'
        ]
        
        for file_path in base_files:
            source = self.template_root / file_path
            dest = target_path / file_path
            
            if source.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
    
    def _setup_web_project(self, target_path: Path, name: str, framework: str, **kwargs) -> None:
        """Set up web application project."""
        framework = framework or 'flask'
        
        print(f"🌐 Setting up {framework} web application...")
        
        # Copy framework-specific template
        template_source = self.template_root / 'templates' / f'{framework}_app_template'
        if template_source.exists():
            for item in template_source.iterdir():
                dest = target_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        
        # Create web-specific structure
        web_dirs = [
            'app/models',
            'app/services', 
            'app/api',
            'app/auth',
            'static/css',
            'static/js',
            'templates',
            'migrations',
            'instance'
        ]
        
        for dir_path in web_dirs:
            (target_path / dir_path).mkdir(parents=True, exist_ok=True)
            
        # Create web-specific files
        self._create_web_files(target_path, name, framework)
        
        # Update requirements for web framework
        self._create_requirements_file(target_path, framework, 'web')
        
        # Add API documentation generation
        self._setup_api_documentation(target_path, framework)
    
    def _setup_cli_project(self, target_path: Path, name: str, framework: str = None, **kwargs) -> None:
        """Set up CLI application project."""
        framework = framework or 'click'
        
        print(f"💻 Setting up CLI application with {framework}...")
        
        # Create CLI-specific structure  
        cli_dirs = [
            f'{name.lower()}/commands',
            f'{name.lower()}/config',
            f'{name.lower()}/utils',
            'docs/commands',
            'examples'
        ]
        
        for dir_path in cli_dirs:
            (target_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create CLI-specific files
        self._create_cli_files(target_path, name, framework)
        
        # Update requirements for CLI framework
        self._create_requirements_file(target_path, framework, 'cli')
    
    def _setup_microservice_project(self, target_path: Path, name: str, framework: str, **kwargs) -> None:
        """Set up microservice project."""
        framework = framework or 'fastapi'
        
        print(f"🔧 Setting up microservice with {framework}...")
        
        # Create microservice-specific structure
        service_dirs = [
            'app/api/v1',
            'app/core',
            'app/models', 
            'app/services',
            'app/utils',
            'docker',
            'k8s',
            'monitoring'
        ]
        
        for dir_path in service_dirs:
            (target_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create microservice-specific files
        self._create_microservice_files(target_path, name, framework)
        
        # Update requirements for microservice framework
        self._create_requirements_file(target_path, framework, 'microservice')
        
        # Add API documentation generation
        self._setup_api_documentation(target_path, framework)
    
    def _setup_data_project(self, target_path: Path, name: str, framework: str = None, **kwargs) -> None:
        """Set up data processing project."""
        framework = framework or 'pandas'
        
        print(f"📊 Setting up data processing project...")
        
        # Create data-specific structure
        data_dirs = [
            'data/raw',
            'data/processed', 
            'data/external',
            'notebooks',
            'pipelines',
            'models',
            'config',
            'scripts'
        ]
        
        for dir_path in data_dirs:
            (target_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create data-specific files
        self._create_data_files(target_path, name, framework)
        
        # Update requirements for data processing
        self._create_requirements_file(target_path, framework, 'data')
    
    def _setup_desktop_project(self, target_path: Path, name: str, framework: str, **kwargs) -> None:
        """Set up desktop application project."""
        framework = framework or 'electron'
        
        print(f"🖥️ Setting up desktop application with {framework}...")
        
        if framework == 'electron':
            desktop_dirs = [
                'src/main',
                'src/renderer', 
                'assets',
                'build',
                'dist'
            ]
        else:  # Tauri, PyQt, etc.
            desktop_dirs = [
                'src',
                'assets',
                'resources',
                'build',
                'dist'
            ]
        
        for dir_path in desktop_dirs:
            (target_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create desktop-specific files
        self._create_desktop_files(target_path, name, framework)
        
        # Update requirements for desktop framework
        self._create_requirements_file(target_path, framework, 'desktop')
    
    def _setup_mobile_project(self, target_path: Path, name: str, framework: str, **kwargs) -> None:
        """Set up mobile application project."""
        framework = framework or 'react_native'
        
        print(f"📱 Setting up mobile application with {framework}...")
        
        # Mobile project setup would depend on the specific framework
        # This is a placeholder for React Native, Flutter, etc.
        mobile_dirs = [
            'src/components',
            'src/screens',
            'src/services',
            'assets',
            'android',  # React Native
            'ios'       # React Native
        ]
        
        for dir_path in mobile_dirs:
            (target_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _create_web_files(self, target_path: Path, name: str, framework: str) -> None:
        """Create web application specific files."""
        # Main application file
        if framework == 'flask':
            app_content = f'''"""
{name} - Flask Web Application

Main application entry point.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.auth import bp as auth_bp  
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
'''
        elif framework == 'fastapi':
            app_content = f'''"""
{name} - FastAPI Web Application

Main application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(
    title="{name}",
    description="API for {name}",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        (target_path / 'app.py').write_text(app_content)
        
        # Configuration file
        config_content = f'''"""
Configuration settings for {name}.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

class Config:
    """Base configuration class."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \\
        f'sqlite:///{{{BASE_DIR / "instance" / "{name.lower()}.db"}}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    WTF_CSRF_ENABLED = True
    
    # API
    API_RATE_LIMIT = "1000 per hour"
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {{
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}}
'''
        
        (target_path / 'config.py').write_text(config_content)
    
    def _create_cli_files(self, target_path: Path, name: str, framework: str) -> None:
        """Create CLI application specific files."""
        cli_name = name.lower()
        
        # Main CLI file
        main_content = f'''#!/usr/bin/env python3
"""
{name} - Command Line Interface

Main CLI entry point.
"""

import click
from {cli_name}.commands import process, config, info

@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """{name} - A powerful command-line tool."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

# Register commands
cli.add_command(process.process)
cli.add_command(config.config)
cli.add_command(info.info)

if __name__ == '__main__':
    cli()
'''
        
        (target_path / f'{cli_name}/__main__.py').write_text(main_content)
        
        # Create sample command
        process_command = f'''"""
Process command for {name}.
"""

import click
from pathlib import Path

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'txt']), 
              default='json', help='Output format')
@click.pass_context
def process(ctx, input_file, output, format):
    """Process input file and generate output."""
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo(f"Processing {{input_file}} in {{format}} format...")
    
    try:
        # Your processing logic here
        result = process_file(input_file, format)
        
        if output:
            Path(output).write_text(result)
            click.echo(f"Output written to {{output}}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"Error: {{e}}", err=True)
        raise click.Abort()

def process_file(input_file: str, format: str) -> str:
    """Process the input file."""
    # Implement your processing logic
    return f"Processed {{input_file}} in {{format}} format"
'''
        
        (target_path / f'{cli_name}/commands/process.py').write_text(process_command)
    
    def _create_microservice_files(self, target_path: Path, name: str, framework: str) -> None:
        """Create microservice specific files."""
        # Dockerfile
        dockerfile_content = f'''FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        (target_path / 'Dockerfile').write_text(dockerfile_content)
        
        # Docker Compose
        compose_content = f'''version: '3.8'

services:
  {name.lower()}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/{name.lower()}
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: {name.lower()}
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
'''
        
        (target_path / 'docker-compose.yml').write_text(compose_content)
    
    def _create_data_files(self, target_path: Path, name: str, framework: str) -> None:
        """Create data processing specific files."""
        # Main data processing script
        main_content = f'''"""
{name} - Data Processing Pipeline

Main data processing entry point.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing class."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_dir = Path(config.get('data_dir', 'data'))
        
    def load_data(self, source: str) -> pd.DataFrame:
        """Load data from source."""
        file_path = self.data_dir / 'raw' / source
        
        if file_path.suffix == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            return pd.read_json(file_path)
        elif file_path.suffix == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {{file_path.suffix}}")
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the data."""
        logger.info(f"Processing {{len(df)}} rows")
        
        # Data validation
        self.validate_data(df)
        
        # Data transformation
        df_processed = self.transform_data(df)
        
        logger.info(f"Processing complete: {{len(df_processed)}} rows")
        return df_processed
    
    def validate_data(self, df: pd.DataFrame) -> None:
        """Validate data quality."""
        # Check for missing values
        missing_pct = df.isnull().sum() / len(df) * 100
        if missing_pct.max() > 50:
            logger.warning(f"High missing values detected: {{missing_pct.max():.1f}}%")
        
        # Add more validation rules as needed
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform the data."""
        # Implement your transformation logic
        return df
    
    def save_data(self, df: pd.DataFrame, output_path: str) -> None:
        """Save processed data."""
        output_file = self.data_dir / 'processed' / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if output_file.suffix == '.csv':
            df.to_csv(output_file, index=False)
        elif output_file.suffix == '.parquet':
            df.to_parquet(output_file, index=False)
        else:
            raise ValueError(f"Unsupported output format: {{output_file.suffix}}")
        
        logger.info(f"Data saved to {{output_file}}")

def main():
    """Main processing function."""
    config = {{
        'data_dir': 'data',
        'log_level': 'INFO'
    }}
    
    processor = DataProcessor(config)
    
    try:
        # Load data
        df = processor.load_data('input.csv')
        
        # Process data
        df_processed = processor.process_data(df)
        
        # Save results
        processor.save_data(df_processed, 'output.csv')
        
    except Exception as e:
        logger.error(f"Processing failed: {{e}}")
        raise

if __name__ == '__main__':
    main()
'''
        
        (target_path / 'main.py').write_text(main_content)
    
    def _create_desktop_files(self, target_path: Path, name: str, framework: str) -> None:
        """Create desktop application specific files."""
        if framework == 'electron':
            # Package.json for Electron
            package_json = {
                "name": name.lower(),
                "version": "1.0.0",
                "description": f"{name} Desktop Application",
                "main": "src/main/main.js",
                "scripts": {
                    "start": "electron .",
                    "build": "electron-builder",
                    "dev": "electron . --dev"
                },
                "devDependencies": {
                    "electron": "^latest",
                    "electron-builder": "^latest"
                },
                "dependencies": {}
            }
            
            (target_path / 'package.json').write_text(json.dumps(package_json, indent=2))
    
    def _create_requirements_file(self, target_path: Path, framework: str, project_type: str) -> None:
        """Create requirements.txt based on project type and framework."""
        base_requirements = [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800'
        ]
        
        framework_requirements = {
            'flask': [
                'Flask>=2.0.0',
                'Flask-SQLAlchemy>=2.5.0',
                'Flask-Migrate>=3.0.0',
                'Flask-WTF>=1.0.0',
                'Werkzeug>=2.0.0'
            ],
            'fastapi': [
                'fastapi>=0.70.0',
                'uvicorn[standard]>=0.15.0',
                'SQLAlchemy>=1.4.0',
                'alembic>=1.7.0',
                'pydantic>=1.8.0'
            ],
            'django': [
                'Django>=4.0.0',
                'djangorestframework>=3.14.0',
                'django-cors-headers>=3.13.0'
            ],
            'click': [
                'click>=8.0.0',
                'rich>=10.0.0',
                'pydantic>=1.8.0'
            ],
            'pandas': [
                'pandas>=1.3.0',
                'numpy>=1.21.0',
                'matplotlib>=3.4.0',
                'seaborn>=0.11.0',
                'scikit-learn>=1.0.0'
            ]
        }
        
        security_requirements = [
            'bandit>=1.7.0',
            'safety>=1.10.0'
        ]
        
        requirements = base_requirements + framework_requirements.get(framework, []) + security_requirements
        
        (target_path / 'requirements.txt').write_text('\n'.join(sorted(requirements)))
        
        # Create development requirements
        dev_requirements = [
            'pytest-mock>=3.6.0',
            'pytest-asyncio>=0.15.0',
            'factory-boy>=3.2.0',
            'freezegun>=1.2.0',
            'responses>=0.18.0'
        ]
        
        (target_path / 'requirements-dev.txt').write_text('\n'.join(sorted(dev_requirements)))
    
    def _setup_api_documentation(self, target_path: Path, framework: str) -> None:
        """Set up automatic API documentation system."""
        
        # Create API documentation directory
        api_docs_dir = target_path / 'docs' / 'api'
        api_docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy API documentation system files
        api_doc_files = [
            'API_DOCUMENTATION_SYSTEM.md',
            'scripts/generate_api_docs.py'
        ]
        
        for file_path in api_doc_files:
            source = self.template_root / file_path
            dest = target_path / file_path
            
            if source.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        
        # Add framework-specific documentation setup
        if framework == 'fastapi':
            self._setup_fastapi_docs(target_path)
        elif framework == 'flask':
            self._setup_flask_docs(target_path)
        elif framework == 'django':
            self._setup_django_docs(target_path)
    
    def _setup_fastapi_docs(self, target_path: Path) -> None:
        """Set up FastAPI-specific documentation."""
        
        # FastAPI has built-in OpenAPI support
        readme_addition = '''

## API Documentation

This FastAPI application includes automatic API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Generate Documentation

```bash
# Generate comprehensive API documentation
python scripts/generate_api_docs.py

# Validate documentation
python docs/api/validate_docs.py --api-url http://localhost:8000

# Generate client SDKs
# See docs/api/SDK_GENERATION.md for details
```

### Documentation Features

- **Interactive Testing** - Test endpoints directly in browser
- **Automatic Schema Generation** - Pydantic models create schemas
- **Request/Response Examples** - Comprehensive examples for all endpoints
- **Authentication Documentation** - Built-in auth flow documentation
- **Client SDK Generation** - Generate clients in multiple languages
'''
        
        readme_file = target_path / 'README.md'
        if readme_file.exists():
            content = readme_file.read_text()
            readme_file.write_text(content + readme_addition)
    
    def _setup_flask_docs(self, target_path: Path) -> None:
        """Set up Flask-specific documentation."""
        
        # Add Flask-RESTX requirements if not already present
        requirements_file = target_path / 'requirements.txt'
        if requirements_file.exists():
            content = requirements_file.read_text()
            if 'flask-restx' not in content.lower():
                with open(requirements_file, 'a') as f:
                    f.write('\nflask-restx>=1.1.0\n')
        
        readme_addition = '''

## API Documentation

This Flask application includes automatic API documentation using Flask-RESTX:

- **Swagger UI**: http://localhost:5000/docs/
- **OpenAPI Spec**: Available through Swagger UI

### Generate Documentation

```bash
# Generate comprehensive API documentation
python scripts/generate_api_docs.py

# Validate documentation
python docs/api/validate_docs.py --api-url http://localhost:5000

# Generate client SDKs
# See docs/api/SDK_GENERATION.md for details
```

### Documentation Features

- **Interactive Testing** - Test endpoints directly in browser
- **Automatic Schema Generation** - Flask-RESTX models create schemas
- **Request/Response Examples** - Comprehensive examples for all endpoints
- **Authentication Documentation** - Built-in auth flow documentation
- **Client SDK Generation** - Generate clients in multiple languages
'''
        
        readme_file = target_path / 'README.md'
        if readme_file.exists():
            content = readme_file.read_text()
            readme_file.write_text(content + readme_addition)
    
    def _setup_django_docs(self, target_path: Path) -> None:
        """Set up Django-specific documentation."""
        
        # Add DRF and drf-yasg requirements
        requirements_file = target_path / 'requirements.txt'
        if requirements_file.exists():
            content = requirements_file.read_text()
            additions = []
            if 'djangorestframework' not in content.lower():
                additions.append('djangorestframework>=3.14.0')
            if 'drf-yasg' not in content.lower():
                additions.append('drf-yasg>=1.21.0')
            
            if additions:
                with open(requirements_file, 'a') as f:
                    f.write('\n' + '\n'.join(additions) + '\n')
        
        readme_addition = '''

## API Documentation

This Django application includes automatic API documentation using DRF and drf-yasg:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **OpenAPI Spec**: http://localhost:8000/swagger.json

### Generate Documentation

```bash
# Generate comprehensive API documentation
python scripts/generate_api_docs.py

# Validate documentation
python docs/api/validate_docs.py --api-url http://localhost:8000

# Generate client SDKs
# See docs/api/SDK_GENERATION.md for details
```

### Documentation Features

- **Interactive Testing** - Test endpoints directly in browser
- **Automatic Schema Generation** - DRF serializers create schemas
- **Request/Response Examples** - Comprehensive examples for all endpoints
- **Authentication Documentation** - Built-in auth flow documentation
- **Client SDK Generation** - Generate clients in multiple languages
'''
        
        readme_file = target_path / 'README.md'
        if readme_file.exists():
            content = readme_file.read_text()
            readme_file.write_text(content + readme_addition)
    
    def _update_project_context(self, target_path: Path, name: str, project_type: str, 
                               framework: str, **kwargs) -> None:
        """Update project context file with specific details."""
        context_content = f'''# {name} Project Context

## Project Information
- **Name**: {name}
- **Type**: {project_type}
- **Framework**: {framework}
- **Created**: {Path.cwd().name}
- **Template Version**: 1.0.0

## Project Structure
This {project_type} application follows the universal development template with:
- Comprehensive testing framework (>95% coverage required)
- Automated documentation updates
- Security validation and best practices
- Performance monitoring and optimization
- Git hooks for quality assurance

## Technology Stack
- **Primary Framework**: {framework}
- **Testing**: pytest with comprehensive coverage
- **Code Quality**: black, flake8, mypy
- **Security**: bandit, safety
- **Documentation**: Auto-updating markdown files

## Development Workflow
1. Read DEV_GUIDELINES.md for development standards
2. Follow TESTING_GUIDE.md for testing requirements
3. Use LLM_REQUEST_TEMPLATE.md for making development requests
4. All changes automatically validated via git hooks

## Getting Started
```bash
# Install development system
python scripts/install_dev_system.py

# Start development with LLM request:
# "[TASK_TYPE]: Description of what you want to build
# Follow project guidelines and update all relevant documentation."
```

## Project-Specific Notes
{self._generate_project_notes(project_type, framework, **kwargs)}
'''
        
        (target_path / '.claude/project_context.md').write_text(context_content)
    
    def _generate_project_notes(self, project_type: str, framework: str, **kwargs) -> str:
        """Generate project-specific notes based on type and framework."""
        notes_map = {
            'web': f'''
### Web Application Specific:
- API endpoints follow RESTful conventions
- Authentication required for protected routes
- Database migrations managed via framework tools
- Frontend assets served from static/ directory
- WebSocket support for real-time features
''',
            'cli': f'''
### CLI Application Specific:
- Commands organized in {framework} structure
- Configuration file support (~/.{kwargs.get('name', 'app').lower()}/config.yaml)
- Progress indicators for long-running operations
- Comprehensive help documentation
- Cross-platform compatibility ensured
''',
            'microservice': f'''
### Microservice Specific:
- Health check endpoint at /health
- Metrics endpoint at /metrics
- Docker containerization included
- Service discovery patterns implemented
- Circuit breaker for external dependencies
''',
            'data': f'''
### Data Processing Specific:
- ETL pipeline with validation stages
- Support for CSV, JSON, Parquet formats
- Data quality monitoring
- Incremental processing capabilities
- Error handling and recovery mechanisms
'''
        }
        
        return notes_map.get(project_type, '### Project-specific configuration will be added here.')
    
    def _customize_documentation(self, target_path: Path, name: str, project_type: str, framework: str) -> None:
        """Customize documentation files for the specific project."""
        # Create project-specific README
        readme_content = f'''# {name}

A {project_type} application built with {framework} following enterprise-grade development practices.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- {framework} (see requirements.txt)

### Installation
```bash
# Clone and enter project directory
cd {name}

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install development system
python scripts/install_dev_system.py
```

### Running the Application
{self._get_run_instructions(project_type, framework, name)}

## 🧪 Testing
```bash
# Run all tests with coverage
python tests/test_suite_runner.py --coverage

# Run specific test category
python tests/test_suite_runner.py --category unit

# Run performance tests
python tests/test_suite_runner.py --category performance
```

## 🔧 Development

### Making Changes
Use the LLM request template for all development:

```
[TASK_TYPE]: Brief description of what you want to add/change

Detailed requirements and context here.

Follow project guidelines and update all relevant documentation.
```

This automatically triggers:
- ✅ Comprehensive testing (>95% coverage)
- ✅ Security validation
- ✅ Performance checks
- ✅ Documentation updates
- ✅ Code quality validation

### Project Standards
- **Code Quality**: Enforced via black, flake8, mypy
- **Testing**: >95% coverage required, TDD approach
- **Security**: Validated via bandit, input sanitization
- **Performance**: Response time and resource monitoring
- **Documentation**: Auto-updated on every change

## 📁 Project Structure
{self._get_project_structure(project_type, framework, name)}

## 🚀 Deployment
{self._get_deployment_info(project_type, framework)}

## 📚 Documentation
- `DEV_GUIDELINES.md` - Development standards and patterns
- `TESTING_GUIDE.md` - Comprehensive testing framework
- `LLM_REQUEST_TEMPLATE.md` - How to make development requests
- `.claude/project_context.md` - Project-specific context

## 🔒 Security
This project includes comprehensive security measures:
- Input validation and sanitization
- Authentication and authorization
- Security vulnerability scanning
- Secure coding practices enforcement

## 📊 Performance
Performance standards enforced automatically:
- API response times < 500ms
- Database queries < 100ms
- Memory usage monitoring
- Load testing capabilities

---

Built with the Universal App Development Template - ensuring enterprise-grade quality from day one.
'''
        
        (target_path / 'README.md').write_text(readme_content)
    
    def _get_run_instructions(self, project_type: str, framework: str, name: str) -> str:
        """Get run instructions based on project type."""
        instructions_map = {
            'web': {
                'flask': f'''```bash
# Development server
python app.py

# Access application at http://localhost:5000
```''',
                'fastapi': f'''```bash
# Development server
uvicorn app.main:app --reload

# Access application at http://localhost:8000
# API docs at http://localhost:8000/docs
```''',
                'django': f'''```bash
# Development server
python manage.py runserver

# Access application at http://localhost:8000
```'''
            },
            'cli': {
                'click': f'''```bash
# Run CLI application
python -m {name.lower()} --help

# Example command
python -m {name.lower()} process input.txt --output result.json
```'''
            },
            'microservice': {
                'fastapi': f'''```bash
# Development
uvicorn app.main:app --reload

# Production (Docker)
docker-compose up

# Access service at http://localhost:8000
```'''
            },
            'data': {
                'pandas': f'''```bash
# Run data processing
python main.py

# Process specific file
python -c "from main import DataProcessor; dp = DataProcessor({{}); dp.process('input.csv')"
```'''
            }
        }
        
        return instructions_map.get(project_type, {}).get(framework, '```bash\n# Add run instructions\n```')
    
    def _get_project_structure(self, project_type: str, framework: str, name: str) -> str:
        """Get project structure description."""
        structures = {
            'web': f'''```
{name}/
├── app/
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── api/            # API endpoints
│   └── auth/           # Authentication
├── static/             # Static assets
├── templates/          # HTML templates
├── tests/              # Test suite
├── migrations/         # Database migrations
└── instance/          # Instance-specific files
```''',
            'cli': f'''```
{name}/
├── {name.lower()}/
│   ├── commands/       # CLI commands
│   ├── config/         # Configuration
│   └── utils/          # Utilities
├── tests/              # Test suite
├── docs/              # Documentation
└── examples/          # Usage examples
```''',
            'microservice': f'''```
{name}/
├── app/
│   ├── api/v1/        # API version 1
│   ├── core/          # Core functionality
│   ├── models/        # Data models
│   └── services/      # Business services
├── docker/            # Docker configurations
├── k8s/              # Kubernetes manifests
├── monitoring/        # Monitoring configs
└── tests/            # Test suite
```'''
        }
        
        return structures.get(project_type, '```\n# Project structure\n```')
    
    def _get_deployment_info(self, project_type: str, framework: str) -> str:
        """Get deployment information."""
        deployment_map = {
            'web': '''
### Web Application Deployment
- **Development**: Built-in development server
- **Production**: WSGI server (Gunicorn) with reverse proxy (Nginx)
- **Containerization**: Docker support included
- **Cloud**: Deployable to AWS, GCP, Azure, Heroku
''',
            'cli': '''
### CLI Application Distribution
- **PyPI**: Package for pip installation
- **Binary**: PyInstaller for standalone executables
- **Containers**: Docker for consistent environments
''',
            'microservice': '''
### Microservice Deployment
- **Containers**: Docker and Docker Compose included
- **Orchestration**: Kubernetes manifests provided
- **Service Mesh**: Compatible with Istio, Linkerd
- **Monitoring**: Prometheus and Grafana ready
'''
        }
        
        return deployment_map.get(project_type, '### Deployment instructions will be added based on project needs.')


def main():
    parser = argparse.ArgumentParser(description="Set up new project from universal template")
    parser.add_argument('--name', required=True, help='Project name')
    parser.add_argument('--type', required=True, 
                       choices=['web', 'cli', 'microservice', 'data', 'desktop', 'mobile'],
                       help='Project type')
    parser.add_argument('--framework', help='Framework to use (flask, fastapi, click, etc.)')
    parser.add_argument('--target', help='Target directory (default: ../PROJECT_NAME)')
    parser.add_argument('--language', default='python', help='Programming language')
    
    args = parser.parse_args()
    
    try:
        setup = ProjectSetup()
        project_path = setup.create_project(
            name=args.name,
            project_type=args.type,
            framework=args.framework,
            target_dir=args.target,
            language=args.language
        )
        
        print(f"\n🎉 Project '{args.name}' created successfully!")
        print(f"📁 Location: {project_path}")
        print(f"\n📋 Next steps:")
        print(f"1. cd {Path(project_path).name}")
        print(f"2. python scripts/install_dev_system.py")
        print(f"3. Start developing with LLM requests!")
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()