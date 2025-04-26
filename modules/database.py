from flask_sqlalchemy import SQLAlchemy
import os

# Create the SQLAlchemy extension
db = SQLAlchemy()

def init_app(app):
    """Initialize the Flask application with the SQLAlchemy extension"""
    # Initialize the app with the extension
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()