"""
Configuration settings for the Information Retrieval System.
"""
import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory containing the corpus of text documents
DOCUMENTS_DIR = os.path.join(BASE_DIR, 'documents')

# Template and static assets directories for Flask
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Server Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
DEBUG = True

