import os

# Flask configuration
SECRET_KEY = 'your-secret-key-goes-here'  # Change this to a random string in production
DEBUG = True

# File upload configuration
UPLOAD_FOLDER = 'uploads'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///fashion_advisor.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

