# Backend/config.py - CONFIGURACIÓN OPTIMIZADA PARA PYTHONANYWHERE
import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ========== DETECCIÓN DE ENTORNO ==========
IS_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE_SITE' in os.environ
IS_RENDER = 'RENDER' in os.environ

class Config:
    """Configuración base para la aplicación Flask"""
    
    # ========== CONFIGURACIÓN BÁSICA ==========
    APP_NAME = 'Caño Salao Turismo API'
    APP_VERSION = '1.0.0'
    API_PREFIX = '/api'
    
    # ========== CONFIGURACIÓN DE SEGURIDAD ==========
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-cano-salao-2024-turismo'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key-cano-salao-2024'
    
    # ========== CONFIGURACIÓN DE BASE DE DATOS ==========
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # CONFIGURACIÓN ESPECÍFICA PARA PYTHONANYWHERE
    if IS_PYTHONANYWHERE:
        # Ruta absoluta para PythonAnywhere - usuario Ricadjf
        instance_dir = '/home/Ricadjf/cano-salao-backend/instance'
        os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, 'cano_salao.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:////{db_path}'
        print(f"🗄️  PYTHONANYWHERE - SQLite: {db_path}")
    
    elif IS_RENDER:
        # Configuración para Render (si aún lo necesitas)
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
            print("🗄️  RENDER - Usando PostgreSQL")
        else:
            instance_dir = os.path.join(basedir, 'instance')
            os.makedirs(instance_dir, exist_ok=True)
            db_path = os.path.join(instance_dir, 'cano_salao.db')
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
            print(f"🗄️  RENDER - SQLite: {db_path}")
    
    else:
        # Desarrollo local
        instance_dir = os.path.join(basedir, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, 'cano_salao.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        print(f"🗄️  LOCAL - SQLite: {db_path}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # ========== CONFIGURACIÓN JWT ==========
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # ========== CONFIGURACIÓN CORS ==========
    # Orígenes permitidos - GitHub Pages y localhost
    CORS_ORIGINS_STRING = os.environ.get('CORS_ORIGINS', '')
    
    if CORS_ORIGINS_STRING:
        CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STRING.split(',')]
    else:
        CORS_ORIGINS = [
            'http://localhost:5500',
            'http://127.0.0.1:5500',
            'http://localhost:5000',
            'http://127.0.0.1:5000',
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'https://ricardjf.github.io',  # Específico para tu GitHub Pages
            'https://*.github.io',
        ]
    
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization', 'X-Total-Count']
    
    # ========== CONFIGURACIÓN DEL SERVIDOR ==========
    # PythonAnywhere NO usa HOST/PORT - lo maneja su sistema
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Entorno
    ENV = 'production' if IS_PYTHONANYWHERE else os.environ.get('FLASK_ENV', 'development')
    DEBUG = False if IS_PYTHONANYWHERE else os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # ========== CONFIGURACIÓN DE LOGGING ==========
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ========== LÍMITES Y CONFIGURACIONES ADICIONALES ==========
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SEND_FILE_MAX_AGE_DEFAULT = 300
    
    # ========== CONFIGURACIONES ESPECÍFICAS DEL PROYECTO ==========
    DEFAULT_ADMIN_EMAIL = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@canosalao.com')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
    
    MAX_BOOKING_DAYS_AHEAD = 90
    MIN_BOOKING_HOURS_NOTICE = 24
    MAX_PEOPLE_PER_BOOKING = 20
    
    DEFAULT_TOUR_CAPACITY = 15
    MIN_TOUR_DURATION_HOURS = 1
    MAX_TOUR_DURATION_HOURS = 8
    
    @classmethod
    def is_production(cls):
        return cls.ENV == 'production'
    
    @classmethod
    def is_development(cls):
        return cls.ENV == 'development'
    
    @classmethod
    def is_pythonanywhere(cls):
        return IS_PYTHONANYWHERE
    
    @classmethod
    def print_config_summary(cls):
        """Imprimir resumen de configuración"""
        print("\n" + "="*60)
        print("📋 RESUMEN DE CONFIGURACIÓN - Caño Salao")
        print("="*60)
        print(f"  Entorno: {cls.ENV}")
        print(f"  Plataforma: {'PythonAnywhere' if IS_PYTHONANYWHERE else 'Render' if IS_RENDER else 'Local'}")
        print(f"  Debug: {cls.DEBUG}")
        print(f"  Base de datos: {'SQLite'}")
        print(f"  Orígenes CORS: {len(cls.CORS_ORIGINS)} configurados")
        print(f"  Nombre App: {cls.APP_NAME}")
        print(f"  Versión: {cls.APP_VERSION}")
        
        if IS_PYTHONANYWHERE:
            print(f"\n🌍 URL Producción: https://ricadjf.pythonanywhere.com")
        
        if cls.is_production() and not IS_PYTHONANYWHERE:
            print("\n⚠️  VERIFICACIONES DE PRODUCCIÓN:")
            if cls.SECRET_KEY.startswith('dev-'):
                print("  ❌ SECRET_KEY insegura")
            if cls.JWT_SECRET_KEY.startswith('dev-'):
                print("  ❌ JWT_SECRET_KEY insegura")
        else:
            print(f"\n🔧 MODO DESARROLLO")
            print(f"  Admin: {cls.DEFAULT_ADMIN_EMAIL} / {cls.DEFAULT_ADMIN_PASSWORD}")
        
        print("="*60)


# Configuración de producción - PythonAnywhere
class PythonAnywhereConfig(Config):
    """Configuración optimizada para PythonAnywhere"""
    
    ENV = 'production'
    DEBUG = False
    
    # CORS específico para GitHub Pages
    @property
    def CORS_ORIGINS(self):
        return [
            'https://ricardjf.github.io',
            'https://www.ricardjf.github.io',
            'https://*.github.io',
        ]
    
    @classmethod
    def validate_config(cls):
        """Validar configuración para PythonAnywhere"""
        errors = []
        
        if not cls.SECRET_KEY or cls.SECRET_KEY.startswith('dev-'):
            errors.append("SECRET_KEY insegura - configúrala en Environment Variables")
        
        if not cls.JWT_SECRET_KEY or cls.JWT_SECRET_KEY.startswith('dev-'):
            errors.append("JWT_SECRET_KEY insegura - configúrala en Environment Variables")
        
        if errors:
            print("\n⚠️  ADVERTENCIAS DE CONFIGURACIÓN:")
            for error in errors:
                print(f"  • {error}")
            print("  El sistema funcionará, pero configura las variables en PythonAnywhere > Web > Environment variables\n")


# Configuración de desarrollo
class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    @property
    def CORS_ORIGINS(self):
        return super().CORS_ORIGINS + [
            'http://localhost:8080',
            'http://127.0.0.1:8080',
        ]


# Configuración de testing
class TestingConfig(Config):
    """Configuración para pruebas"""
    
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Diccionario de configuraciones
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': PythonAnywhereConfig,  # Ahora apunta a PythonAnywhereConfig
    'pythonanywhere': PythonAnywhereConfig,
    'render': DevelopmentConfig,  # Fallback a development
    'default': DevelopmentConfig,
}


def get_config():
    """Obtener configuración basada en el entorno"""
    
    # Detectar entorno automáticamente
    if IS_PYTHONANYWHERE:
        env = 'pythonanywhere'
        print("🌍 Entorno detectado: PYTHONANYWHERE")
        config_class = PythonAnywhereConfig
    elif IS_RENDER:
        env = 'render'
        print("🌍 Entorno detectado: RENDER")
        config_class = DevelopmentConfig  # No recomendado, pero funciona
    else:
        env = os.environ.get('FLASK_ENV', 'development').lower()
        print(f"🌍 Entorno detectado: LOCAL ({env})")
        config_class = config_by_name.get(env, DevelopmentConfig)
    
    # Crear instancia
    if isinstance(config_class, type):
        config_instance = config_class()
    else:
        config_instance = config_class
    
    # Validar configuración
    if IS_PYTHONANYWHERE:
        PythonAnywhereConfig.validate_config()
    
    return config_instance


# Configuración actual
current_config = get_config()

# Imprimir resumen
current_config.print_config_summary()