import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get(
      'DATABASE_URL',
      'mysql+pymysql://usuario:contraseña@localhost:3306/nombre_bd'
    ) 


    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de seguridad
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # Uploads
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'products')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Admin
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@sumiked.com')

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    ENV = 'development'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}