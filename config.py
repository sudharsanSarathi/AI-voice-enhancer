import os
from pathlib import Path

class Config:
    # Server configuration
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = Path('uploads')
    PROCESSED_FOLDER = Path('processed')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'mp3', 'wav', 'flac', 'ogg', 'aac', 'aiff'
    }
    
    # ClearerVoice model configuration
    MODEL_CONFIGS = {
        'light': {
            'model_name': 'FRCRN_SE_16K',
            'description': 'Fast, lightweight processing',
            'intensity_range': (1, 3)
        },
        'medium': {
            'model_name': 'MossFormer2_SE_48K',
            'description': 'Balanced quality and speed',
            'intensity_range': (4, 7)
        },
        'strong': {
            'model_name': 'MossFormerGAN_SE_16K',
            'description': 'Best quality, more aggressive',
            'intensity_range': (8, 10)
        }
    }
    
    # Security configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create directories if they don't exist
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.PROCESSED_FOLDER.mkdir(exist_ok=True)
        
        # Set Flask configuration
        app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
        app.config['SECRET_KEY'] = Config.SECRET_KEY

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    UPLOAD_FOLDER = Path('test_uploads')
    PROCESSED_FOLDER = Path('test_processed')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}