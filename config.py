import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'prospeccao_curitiba_2024_change_in_production')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/prospeccao.db')
    
    # Configurações do Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Detectar se está rodando no Railway
    IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None
    
    # Configurações do Selenium
    SELENIUM_HEADLESS = os.getenv('SELENIUM_HEADLESS', 'True').lower() == 'true'
    CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', None)
    
    # Configurações de WhatsApp (se usar)
    WHATSAPP_SESSION_PATH = os.getenv('WHATSAPP_SESSION_PATH', 'whatsapp_session')
    
    # Configurações de rate limiting
    MAX_MESSAGES_PER_HOUR = int(os.getenv('MAX_MESSAGES_PER_HOUR', 10))
    MAX_SCRAPING_RESULTS = int(os.getenv('MAX_SCRAPING_RESULTS', 100))
    
    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///data/prospeccao_dev.db'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Obrigatório em produção
    
    # Usar PostgreSQL em produção se disponível
    if os.getenv('DATABASE_URL'):
        DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Configurações específicas para Railway
    if IS_RAILWAY:
        HOST = '0.0.0.0'
        PORT = int(os.getenv('PORT', 5000))
        # Converter postgres:// para postgresql:// se necessário
        if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração baseada na variável de ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
