"""
Application Configuration
=========================

Configuration settings for different environments.
"""

import os
from pathlib import Path


class Config:
    """Base configuration."""
    
    # Application
    APP_NAME = "Jiyo100Saal Functional Aging Assessment"
    APP_VERSION = "1.0.0"
    
    # Paths
    BASE_DIR = Path(__file__).parent.absolute()
    
    # Database
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{BASE_DIR / 'jiyo100saal.db'}"
    )
    
    # Database options
    SQLALCHEMY_ECHO = False  # Log SQL statements
    
    # Secret key (for sessions if using Flask)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Testing
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"  # In-memory for tests
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # In production, DATABASE_URL should be set via environment variable
    # e.g., postgresql://user:pass@host:port/dbname


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config(env: str = None) -> Config:
    """Get configuration by environment name."""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
