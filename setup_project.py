#!/usr/bin/env python3
"""
CivicPulse Repository Setup Script

This script creates the full project structure and all source files for CivicPulse.
Run this once to bootstrap the repository.

Usage:
    python setup.py
"""

import os
import sys
from pathlib import Path


def create_directory_structure(root_dir):
    """Create all necessary directories."""
    directories = [
        'src',
        'tests',
        '.agent/skills',
        'docs'
    ]
    
    for dir_name in directories:
        dir_path = Path(root_dir) / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")


def create_source_files(root_dir):
    """Create all source code files."""
    root_path = Path(root_dir)
    
    # src/__init__.py
    (root_path / 'src' / '__init__.py').write_text(
        '''"""CivicPulse - Election Assistant Package"""
__version__ = "1.0.0"
__author__ = "CivicPulse Team"
'''
    )
    
    # tests/__init__.py
    (root_path / 'tests' / '__init__.py').write_text(
        '''"""Tests for CivicPulse Election Assistant"""
'''
    )
    
    print("✓ Created Python package files")


def create_config_files(root_dir):
    """Create configuration files."""
    root_path = Path(root_dir)
    
    # .env.example
    (root_path / '.env.example').write_text(
        '''# Google API Configuration (optional - app works without these)
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CALENDAR_ID=your_calendar_id_here

# Environment
DEBUG=False
LOG_LEVEL=INFO
'''
    )
    
    # setup.py (for packaging)
    (root_path / 'setup.py').write_text(
        '''from setuptools import setup, find_packages

setup(
    name='civicpulse',
    version='1.0.0',
    description='Smart election assistant for voter education and readiness',
    author='CivicPulse Team',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'google-api-python-client>=2.108.0',
        'google-auth-oauthlib>=1.2.0',
        'python-dotenv>=1.0.0',
    ],
)
'''
    )
    
    print("✓ Created configuration files")


def main():
    """Main setup function."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🗳️  CivicPulse Repository Setup")
    print("=" * 50)
    
    print("\n1. Creating directory structure...")
    create_directory_structure(root_dir)
    
    print("\n2. Creating Python package files...")
    create_source_files(root_dir)
    
    print("\n3. Creating configuration files...")
    create_config_files(root_dir)
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!\n")
    print("Next steps:")
    print("  1. python -m venv venv")
    print("  2. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("  3. pip install -r requirements.txt")
    print("  4. python src/main.py\n")


if __name__ == '__main__':
    main()
