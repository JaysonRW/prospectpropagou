"""
Configurações específicas para o Railway
"""
import os

class RailwayConfig:
    """Configuração para ambiente Railway"""
    
    # Configurações do Railway
    PORT = int(os.getenv('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Banco de dados PostgreSQL do Railway
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Configurações de segurança
    SECRET_KEY = os.getenv('SECRET_KEY', 'railway_prospeccao_2024')
    
    # Configurações de logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/tmp/app.log'  # Railway usa /tmp para logs
    
    # Configurações do Selenium (desabilitado no Railway por padrão)
    SELENIUM_HEADLESS = True
    SELENIUM_ENABLED = os.getenv('SELENIUM_ENABLED', 'false').lower() == 'true'
    
    # Configurações de rate limiting
    MAX_MESSAGES_PER_HOUR = int(os.getenv('MAX_MESSAGES_PER_HOUR', 5))
    MAX_SCRAPING_RESULTS = int(os.getenv('MAX_SCRAPING_RESULTS', 50))
    
    # Configurações de ambiente
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Configurações de arquivos
    EXPORT_DIR = '/tmp/export'
    LOGS_DIR = '/tmp/logs'
    
    @classmethod
    def get_database_url(cls):
        """Retorna URL do banco formatada para SQLAlchemy"""
        if cls.DATABASE_URL and cls.DATABASE_URL.startswith('postgres://'):
            # Converter postgres:// para postgresql:// (SQLAlchemy 1.4+)
            return cls.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        return cls.DATABASE_URL 