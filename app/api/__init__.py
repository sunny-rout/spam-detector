"""
API Blueprint Module
Defines the API blueprint for route organization.
"""
from flask import Blueprint

# Create API blueprint with proper versioning
api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.api import routes