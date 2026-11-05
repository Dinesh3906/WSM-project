"""
Vercel Serverless Entry Point

Wraps the Flask application as a WSGI handler for Vercel's Python runtime.
"""
import sys
import os

# Add project root to Python path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects the WSGI app to be exported as 'app'
# This is already satisfied since our Flask instance is named 'app'

