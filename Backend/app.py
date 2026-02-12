# Backend/app.py - VERSIÓN COMPLETA PARA PYTHONANYWHERE (Usuario CORREGIDO: ricardjf)
import os
import sys
import logging
import functools
import re
import uuid
from datetime import timedelta, datetime
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (
    JWTManager, 
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# ========== CONFIGURACIÓN PARA PYTHONANYWHERE ==========
# Detectar si estamos en PythonAnywhere
IS_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE_SITE' in os.environ

# Configurar rutas para PythonAnywhere - USUARIO CORREGIDO: ricardjf (NO Ricadjf, NO ricadjf)
if IS_PYTHONANYWHERE:
    # ✅ USUARIO CORRECTO: ricardjf
    BASE_DIR = '/home/ricardjf/cano-salao-backend'
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # IMPORTANTE: Crear directorio instance con permisos correctos
    try:
        if not os.path.exists(INSTANCE_DIR):
            os.makedirs(INSTANCE_DIR, exist_ok=True)
            os.chmod(INSTANCE_DIR, 0o755)
            print(f"✅ Directorio instance creado: {INSTANCE_DIR}")
        else:
            print(f"✅ Directorio instance ya existe: {INSTANCE_DIR}")
            try:
                os.chmod(INSTANCE_DIR, 0o755)
            except:
                pass
            
        # Probar permisos de escritura
        test_file = os.path.join(INSTANCE_DIR, 'write_test.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Permisos de escritura OK en instance")
    except Exception as e:
        print(f"⚠️ Error con directorio instance: {e}")
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("🚀 INICIANDO CAÑO SALAO - BACKEND API COMPLETO")
print(f"📍 Entorno: {'PYTHONANYWHERE' if IS_PYTHONANYWHERE else 'DESARROLLO LOCAL'}")
print(f"👤 Usuario: ricardjf")
print("="*60)

# ========== CONFIGURACIÓN BÁSICA ==========
class Config:
    # Claves secretas - Usar variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-cano-salao-2024-extra-long-for-security-1234567890')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-cano-salao-2024-extra-long-for-security-1234567890')
    
    # ========== CONFIGURACIÓN DE BASE DE DATOS ==========
    if IS_PYTHONANYWHERE:
        # ✅ CORREGIDO: Ruta absoluta con usuario ricardjf
        SQLALCHEMY_DATABASE_URI = f'sqlite:////home/ricardjf/cano-salao-backend/instance/cano_salao.db'
        print(f"🗄️  Base de datos SQLite (PythonAnywhere): {SQLALCHEMY_DATABASE_URI}")
    else:
        # En desarrollo local
        if os.environ.get('DATABASE_URL'):
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
            print(f"🗄️  Base de datos PostgreSQL: {SQLALCHEMY_DATABASE_URI[:50]}...")
        else:
            # SQLite local
            basedir = os.path.abspath(os.path.dirname(__file__))
            DATABASE_PATH = os.path.join(basedir, 'instance', 'cano_salao.db')
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
            print(f"🗄️  Base de datos SQLite local: {SQLALCHEMY_DATABASE_URI}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== CONFIGURACIÓN JWT ==========
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=365)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = True if IS_PYTHONANYWHERE else False
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # ========== CONFIGURACIÓN CORS ==========
    # Específico para GitHub Pages de ricardjf
    CORS_ORIGINS = [
        'https://ricardjf.github.io',
        'https://www.ricardjf.github.io',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    
    # Configuración del servidor
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = False if IS_PYTHONANYWHERE else os.environ.get('FLASK_ENV', 'development') == 'development'
    ENV = 'production' if IS_PYTHONANYWHERE else os.environ.get('FLASK_ENV', 'development')

# ========== CREAR APLICACIÓN ==========
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ========== CONFIGURAR CORS ==========
    CORS(app, resources={
        r"/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
            "supports_credentials": True,
            "expose_headers": ["Authorization", "Content-Type"],
            "max_age": 3600
        }
    })
    print("✅ CORS configurado")
    print(f"🌍 Orígenes permitidos: {app.config['CORS_ORIGINS']}")
    
    # ========== INICIALIZAR JWT ==========
    jwt = JWTManager(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, dict) and 'id' in user:
            return str(user['id'])
        elif isinstance(user, (int, str)):
            return str(user)
        else:
            return str(getattr(user, 'id', ''))
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            identity = jwt_data["sub"]
            if identity:
                user = User.query.get(int(identity))
                if user:
                    return user
        except Exception as e:
            logger.warning(f"Error en user_lookup_callback: {e}")
        return None
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.info(f"Token expirado")
        return jsonify({
            'success': False,
            'error': 'token_expired',
            'message': 'Token expirado',
            'can_refresh': True
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Token inválido: {error}")
        return jsonify({
            'success': False,
            'error': 'invalid_token',
            'message': 'Token inválido'
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        logger.warning(f"Acceso no autorizado: {error}")
        return jsonify({
            'success': False,
            'error': 'unauthorized',
            'message': 'No autorizado - Token faltante'
        }), 401
    
    print("✅ JWT configurado")
    
    # ========== INICIALIZAR BASE DE DATOS ==========
    db = SQLAlchemy(app)
    
    # Inicializar migraciones
    try:
        migrate = Migrate(app, db)
        print("✅ Migraciones configuradas")
    except Exception as e:
        print(f"⚠️ Migraciones no disponibles: {e}")
    
    # ========== MODELOS ==========
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)
        rol = db.Column(db.String(20), default='user')
        activo = db.Column(db.Boolean, default=True)
        telefono = db.Column(db.String(20))
        direccion = db.Column(db.String(200))
        ciudad = db.Column(db.String(50), default='Barcelona')
        estado = db.Column(db.String(50), default='Anzoátegui')
        pais = db.Column(db.String(50), default='Venezuela')
        fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
        ultimo_acceso = db.Column(db.DateTime, onupdate=datetime.utcnow)
        last_activity = db.Column(db.DateTime)
        email_verificado = db.Column(db.Boolean, default=False)
        notificaciones_email = db.Column(db.Boolean, default=True)
        notificaciones_push = db.Column(db.Boolean, default=True)
        idioma = db.Column(db.String(10), default='es')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def set_password(self, password):
            if not password or len(password) < 6:
                raise ValueError("La contraseña debe tener al menos 6 caracteres")
            self.password = generate_password_hash(password)
        
        def check_password(self, password):
            return check_password_hash(self.password, password)
        
        def is_active(self):
            return self.activo
        
        def is_admin(self):
            return self.rol == 'admin'
        
        def to_dict(self, include_sensitive=False):
            data = {
                'id': self.id,
                'nombre': self.nombre,
                'email': self.email,
                'rol': self.rol,
                'activo': self.activo,
                'telefono': self.telefono,
                'ciudad': self.ciudad,
                'estado': self.estado,
                'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
                'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
                'email_verificado': self.email_verificado,
            }
            
            if include_sensitive:
                data.update({
                    'direccion': self.direccion,
                    'pais': self.pais,
                    'notificaciones_email': self.notificaciones_email,
                    'notificaciones_push': self.notificaciones_push,
                    'idioma': self.idioma,
                })
            
            return data
        
        def to_auth_dict(self):
            return {
                'id': self.id,
                'nombre': self.nombre,
                'email': self.email,
                'rol': self.rol,
                'activo': self.activo,
                'telefono': self.telefono,
            }
        
        @staticmethod
        def validate_email(email):
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_regex, email) is not None
        
        @staticmethod
        def validate_phone(phone):
            if not phone:
                return True
            phone_regex = r'^[\+]?[0-9\s\-\(\)]{10,20}$'
            return re.match(phone_regex, phone) is not None
        
        @classmethod
        def find_by_email(cls, email):
            return cls.query.filter_by(email=email).first()
        
        @classmethod
        def find_by_id(cls, user_id):
            return cls.query.get(user_id)
        
        def __repr__(self):
            return f'<User {self.email}>'
    
    class Tour(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100), nullable=False)
        descripcion = db.Column(db.Text)
        precio = db.Column(db.Float, nullable=False)
        capacidad = db.Column(db.Integer, default=15)
        disponible = db.Column(db.Boolean, default=True)
        duracion = db.Column(db.String(50))
        imagen_url = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'nombre': self.nombre,
                'descripcion': self.descripcion,
                'precio': self.precio,
                'capacidad': self.capacidad,
                'disponible': self.disponible,
                'duracion': self.duracion,
                'imagen_url': self.imagen_url,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    class Booking(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        codigo = db.Column(db.String(50), unique=True, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
        fecha = db.Column(db.Date, nullable=False)
        personas = db.Column(db.Integer, nullable=False)
        total = db.Column(db.Float, nullable=False)
        estado = db.Column(db.String(20), default='pending')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        user = db.relationship('User', backref='bookings')
        tour = db.relationship('Tour', backref='bookings')
        
        def to_dict(self):
            return {
                'id': self.id,
                'codigo': self.codigo,
                'user_id': self.user_id,
                'tour_id': self.tour_id,
                'fecha': self.fecha.isoformat() if self.fecha else None,
                'personas': self.personas,
                'total': self.total,
                'estado': self.estado,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    class BlogPost(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        titulo = db.Column(db.String(200), nullable=False)
        contenido = db.Column(db.Text, nullable=False)
        excerpt = db.Column(db.Text)
        categoria = db.Column(db.String(50))
        autor = db.Column(db.String(100))
        imagen_url = db.Column(db.String(500))
        publicado = db.Column(db.Boolean, default=False)
        vistas = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'titulo': self.titulo,
                'contenido': self.contenido,
                'excerpt': self.excerpt,
                'categoria': self.categoria,
                'autor': self.autor,
                'imagen_url': self.imagen_url,
                'publicado': self.publicado,
                'vistas': self.vistas,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    # ========== INICIALIZAR BASE DE DATOS CON PERMISOS CORREGIDOS ==========
    with app.app_context():
        try:
            # ===== CORREGIDO: Manejo correcto de permisos para PythonAnywhere =====
            if IS_PYTHONANYWHERE:
                # ✅ USUARIO CORRECTO: ricardjf
                instance_dir = '/home/ricardjf/cano-salao-backend/instance'
                
                # Crear directorio si no existe
                if not os.path.exists(instance_dir):
                    os.makedirs(instance_dir, exist_ok=True)
                    print(f"✅ Directorio instance creado: {instance_dir}")
                
                # Dar permisos 755 (rwxr-xr-x)
                try:
                    os.chmod(instance_dir, 0o755)
                except:
                    pass
                
                # Probar permisos de escritura
                test_file = os.path.join(instance_dir, 'write_test.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    print("✅ Permisos de escritura verificados en instance")
                except Exception as e:
                    print(f"⚠️ Error de escritura en instance: {e}")
                    
            # Crear todas las tablas
            db.create_all()
            print("✅ Base de datos inicializada")
            
            # Crear admin por defecto si no existe
            if User.query.count() == 0:
                admin = User(
                    nombre='Administrador',
                    email='admin@canosalao.com',
                    rol='admin',
                    telefono='+58 412-205-6558',
                    ciudad='Barcelona',
                    estado='Anzoátegui',
                    pais='Venezuela',
                    email_verificado=True,
                    activo=True
                )
                admin.set_password('admin123')
                admin.last_activity = datetime.utcnow()
                
                db.session.add(admin)
                
                # Crear tours de ejemplo
                tours = [
                    Tour(
                        nombre='Tour Básico por los Manglares',
                        descripcion='Recorrido guiado de 2 horas por los manglares, observando la fauna y flora local.',
                        precio=25.00,
                        capacidad=15,
                        duracion='2 horas',
                        imagen_url='https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=600',
                        disponible=True
                    ),
                    Tour(
                        nombre='Tour Completo de Aventura',
                        descripcion='Experiencia completa de 4 horas que incluye recorrido por manglares, observación de aves y paseo en bote.',
                        precio=45.00,
                        capacidad=12,
                        duracion='4 horas',
                        imagen_url='https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600',
                        disponible=True
                    ),
                    Tour(
                        nombre='Tour Fotográfico Nocturno',
                        descripcion='Tour especializado para fotografía de la vida nocturna en los manglares.',
                        precio=35.00,
                        capacidad=8,
                        duracion='3 horas',
                        imagen_url='https://images.unsplash.com/photo-1506260408121-e353d10b87c7?w=600',
                        disponible=True
                    )
                ]
                db.session.add_all(tours)
                
                # Crear artículos de blog de ejemplo
                blog_posts = [
                    BlogPost(
                        titulo='Bienvenidos a Caño Salao',
                        contenido='<h1>¡Bienvenidos a nuestro paraíso natural!</h1><p>Caño Salao es un destino turístico único en el estado Anzoátegui, Venezuela. Nuestros manglares son el hogar de una gran variedad de especies animales y vegetales.</p><p>Ofrecemos tours guiados para que puedas disfrutar de la belleza natural de manera responsable y educativa.</p>',
                        excerpt='Conoce más sobre nuestra comunidad y los tours que ofrecemos',
                        categoria='noticias',
                        autor='Equipo Caño Salao',
                        publicado=True,
                        vistas=150
                    ),
                    BlogPost(
                        titulo='Nuevo Tour Fotográfico',
                        contenido='<h2>¡Lanzamos nuestro nuevo tour fotográfico!</h2><p>Ideal para fotógrafos aficionados y profesionales que quieran capturar la belleza de nuestros manglares.</p><p>El tour incluye guías especializados en fotografía de naturaleza y equipo básico para quienes lo necesiten.</p>',
                        excerpt='Descubre nuestro nuevo tour especializado en fotografía de naturaleza',
                        categoria='tours',
                        autor='Carlos Rodríguez',
                        publicado=True,
                        vistas=89
                    ),
                    BlogPost(
                        titulo='Consejos para Visitantes',
                        contenido='<h2>Prepara tu visita a Caño Salao</h2><p>1. Usa ropa cómoda y calzado adecuado</p><p>2. Lleva protección solar y repelente de insectos</p><p>3. Trae tu cámara fotográfica</p><p>4. Mantente hidratado durante el tour</p>',
                        excerpt='Recomendaciones importantes para disfrutar al máximo tu experiencia',
                        categoria='consejos',
                        autor='María González',
                        publicado=True,
                        vistas=203
                    )
                ]
                db.session.add_all(blog_posts)
                
                # Crear algunas reservas de ejemplo
                import random
                for i in range(5):
                    booking = Booking(
                        codigo=f'RES{random.randint(1000, 9999)}',
                        user_id=1,
                        tour_id=random.randint(1, 3),
                        fecha=datetime.utcnow().date(),
                        personas=random.randint(1, 4),
                        total=random.uniform(25, 100),
                        estado=random.choice(['pending', 'confirmed', 'cancelled'])
                    )
                    db.session.add(booking)
                
                db.session.commit()
                print("✅ Datos de ejemplo creados")
                print(f"👑 Admin: admin@canosalao.com / admin123")
                print(f"📊 Usuarios: {User.query.count()}, Tours: {Tour.query.count()}, Reservas: {Booking.query.count()}")
                
        except Exception as e:
            print(f"⚠️ Error inicializando base de datos: {str(e)[:200]}")
            db.session.rollback()
    
    # ========== HELPER FUNCTIONS ==========
    def update_user_activity(user_id):
        try:
            user = User.query.get(user_id)
            if user:
                user.last_activity = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            logger.error(f"Error actualizando actividad: {e}")
    
    def validate_email_frontend(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    def validate_password_frontend(password):
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        if len(password) > 50:
            return False, "La contraseña no puede exceder 50 caracteres"
        return True, "Contraseña válida"
    
    def validate_name_frontend(name):
        if not name or len(name.strip()) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        if len(name) > 100:
            return False, "El nombre no puede exceder 100 caracteres"
        return True, "Nombre válido"
    
    # ========== DECORADOR ADMIN REQUERIDO ==========
    def admin_required(fn):
        @functools.wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_identity = get_jwt_identity()
            
            user_id = None
            if isinstance(current_identity, dict):
                user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    user_id = int(current_identity)
                except:
                    user_id = None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Token inválido'}), 401
            
            user = User.query.get(user_id)
            if not user or user.rol != 'admin':
                return jsonify({'success': False, 'error': 'Acceso solo para administradores'}), 403
            
            update_user_activity(user.id)
            return fn(*args, **kwargs)
        return wrapper
    
    # ========== RUTAS BÁSICAS ==========
    @app.route('/')
    def home():
        return jsonify({
            'success': True,
            'message': '🚤 API Caño Salao - Sistema de Turismo',
            'version': '2.0.0',
            'status': 'online',
            'environment': 'PythonAnywhere' if IS_PYTHONANYWHERE else 'Development',
            'user': 'ricardjf',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'auth': '/api/auth/*',
                'tours': '/api/tours',
                'blog': '/api/blog',
                'admin': '/api/admin/*',
                'status': '/api/status',
                'health': '/health'
            }
        })
    
    @app.route('/api/status')
    def api_status():
        try:
            return jsonify({
                'success': True,
                'status': 'online',
                'service': 'cano-salao-api',
                'environment': app.config['ENV'],
                'host': 'PythonAnywhere' if IS_PYTHONANYWHERE else 'Local',
                'timestamp': datetime.utcnow().isoformat(),
                'database': {
                    'users': User.query.count(),
                    'tours': Tour.query.count(),
                    'bookings': Booking.query.count(),
                    'blog_posts': BlogPost.query.count()
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'status': 'degraded',
                'error': str(e)
            }), 500
    
    @app.route('/health')
    def health():
        try:
            db.session.execute(text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 500
    
    # ========== RUTAS DE AUTENTICACIÓN ==========
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'success': False, 'error': 'Se requiere datos en formato JSON'}), 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'success': False, 'error': 'Email y contraseña son requeridos'}), 400
            
            if not validate_email_frontend(email):
                return jsonify({'success': False, 'error': 'Formato de email inválido'}), 400
            
            usuario = User.find_by_email(email)
            
            if not usuario:
                return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401
            
            if not usuario.is_active():
                return jsonify({'success': False, 'error': 'Tu cuenta está desactivada'}), 403
            
            if not usuario.check_password(password):
                return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401
            
            usuario.ultimo_acceso = datetime.utcnow()
            usuario.last_activity = datetime.utcnow()
            db.session.commit()
            
            identity_dict = {'id': usuario.id, 'email': usuario.email}
            
            access_token = create_access_token(
                identity=identity_dict,
                expires_delta=timedelta(days=30)
            )
            
            refresh_token = create_refresh_token(
                identity=identity_dict,
                expires_delta=timedelta(days=365)
            )
            
            logger.info(f"Login exitoso: {email}")
            
            response = jsonify({
                'success': True,
                'message': 'Inicio de sesión exitoso',
                'token': access_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': usuario.to_auth_dict(),
                'expires_in': timedelta(days=30).total_seconds(),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return response, 200
            
        except Exception as e:
            logger.error(f"Error en login: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'success': False, 'error': 'Se requiere datos en formato JSON'}), 400
            
            nombre = data.get('nombre', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            telefono = data.get('telefono', '').strip()
            
            is_name_valid, name_msg = validate_name_frontend(nombre)
            if not is_name_valid:
                return jsonify({'success': False, 'error': name_msg}), 400
            
            if not validate_email_frontend(email):
                return jsonify({'success': False, 'error': 'Formato de email inválido'}), 400
            
            is_password_valid, password_msg = validate_password_frontend(password)
            if not is_password_valid:
                return jsonify({'success': False, 'error': password_msg}), 400
            
            if User.find_by_email(email):
                return jsonify({'success': False, 'error': 'El email ya está registrado'}), 409
            
            user_count = User.query.count()
            rol = 'admin' if user_count == 0 else 'user'
            
            usuario = User(
                nombre=nombre,
                email=email,
                telefono=telefono,
                rol=rol,
                activo=True,
                fecha_registro=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            identity_dict = {'id': usuario.id, 'email': usuario.email}
            
            access_token = create_access_token(
                identity=identity_dict,
                expires_delta=timedelta(days=30)
            )
            
            refresh_token = create_refresh_token(
                identity=identity_dict,
                expires_delta=timedelta(days=365)
            )
            
            logger.info(f"Nuevo usuario registrado: {email}")
            
            return jsonify({
                'success': True,
                'message': 'Registro exitoso',
                'token': access_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': usuario.to_auth_dict(),
                'timestamp': datetime.utcnow().isoformat()
            }), 201
            
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al crear el usuario'}), 500
    
    @app.route('/api/auth/verify', methods=['GET'])
    @jwt_required()
    def verify_token():
        try:
            current_identity = get_jwt_identity()
            jwt_data = get_jwt()
            
            user_id = None
            if isinstance(current_identity, dict):
                user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    user_id = int(current_identity)
                except:
                    user_id = None
            
            if not user_id:
                return jsonify({'success': False, 'valid': False, 'error': 'Token inválido'}), 401
            
            usuario = User.find_by_id(user_id)
            if not usuario:
                return jsonify({'success': False, 'valid': False, 'error': 'Usuario no encontrado'}), 404
            
            if not usuario.is_active():
                return jsonify({'success': False, 'valid': False, 'error': 'Usuario desactivado'}), 403
            
            update_user_activity(usuario.id)
            
            expires_at = jwt_data.get('exp')
            import time
            current_time = time.time()
            time_left = expires_at - current_time if expires_at else 0
            
            return jsonify({
                'success': True,
                'valid': True,
                'user': usuario.to_auth_dict(),
                'token_info': {
                    'expires_at': expires_at,
                    'time_left_seconds': time_left,
                    'time_left_days': time_left / (24 * 3600) if time_left > 0 else 0
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Error validando token: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'valid': False, 'error': 'Error al validar token'}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        try:
            current_identity = get_jwt_identity()
            
            user_id = None
            if isinstance(current_identity, dict):
                user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    user_id = int(current_identity)
                except:
                    user_id = None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Token inválido'}), 401
            
            user = User.find_by_id(user_id)
            if not user or not user.activo:
                return jsonify({'success': False, 'error': 'Usuario no encontrado o inactivo'}), 401
            
            user.last_activity = datetime.utcnow()
            db.session.commit()
            
            new_access_token = create_access_token(
                identity=current_identity,
                expires_delta=timedelta(days=30)
            )
            
            logger.info(f"Token refrescado para usuario ID: {user_id}")
            
            return jsonify({
                'success': True,
                'token': new_access_token,
                'access_token': new_access_token,
                'user': user.to_auth_dict(),
                'message': 'Token refrescado exitosamente',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Error refrescando token: {str(e)}")
            return jsonify({'success': False, 'error': 'Error al refrescar token'}), 401
    
    @app.route('/api/auth/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        try:
            current_identity = get_jwt_identity()
            
            user_id = None
            if isinstance(current_identity, dict):
                user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    user_id = int(current_identity)
                except:
                    user_id = None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Token inválido'}), 401
            
            usuario = User.find_by_id(user_id)
            if not usuario:
                return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
            
            update_user_activity(usuario.id)
            
            return jsonify({
                'success': True,
                'profile': usuario.to_dict(include_sensitive=True),
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo perfil: {str(e)}")
            return jsonify({'success': False, 'error': 'Error al obtener perfil'}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        try:
            current_identity = get_jwt_identity()
            logger.info(f"Logout solicitado por: {current_identity}")
            
            return jsonify({
                'success': True,
                'message': 'Sesión cerrada exitosamente',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return jsonify({'success': False, 'error': 'Error al cerrar sesión'}), 500
    
    # ========== RUTAS PÚBLICAS ==========
    @app.route('/api/tours', methods=['GET'])
    def get_tours():
        try:
            tours = Tour.query.filter_by(disponible=True).order_by(Tour.precio).all()
            return jsonify([tour.to_dict() for tour in tours])
        except Exception as e:
            logger.error(f"Error obteniendo tours: {e}")
            return jsonify({'error': 'Error obteniendo tours'}), 500
    
    @app.route('/api/tours/<int:tour_id>', methods=['GET'])
    def get_tour(tour_id):
        try:
            tour = Tour.query.get(tour_id)
            if not tour:
                return jsonify({'error': 'Tour no encontrado'}), 404
            return jsonify(tour.to_dict())
        except Exception as e:
            logger.error(f"Error obteniendo tour: {e}")
            return jsonify({'error': 'Error obteniendo tour'}), 500
    
    @app.route('/api/blog', methods=['GET'])
    def get_blog_posts():
        try:
            posts = BlogPost.query.filter_by(publicado=True).order_by(BlogPost.created_at.desc()).all()
            return jsonify([post.to_dict() for post in posts])
        except Exception as e:
            logger.error(f"Error obteniendo posts: {e}")
            return jsonify({'error': 'Error obteniendo posts'}), 500
    
    @app.route('/api/blog/<int:post_id>', methods=['GET'])
    def get_blog_post(post_id):
        try:
            post = BlogPost.query.get(post_id)
            if not post:
                return jsonify({'error': 'Artículo no encontrado'}), 404
            return jsonify(post.to_dict())
        except Exception as e:
            logger.error(f"Error obteniendo artículo: {e}")
            return jsonify({'error': 'Error obteniendo artículo'}), 500
    
    # ========== RUTAS PROTEGIDAS DE USUARIO ==========
    @app.route('/api/user/profile', methods=['GET'])
    @jwt_required()
    def get_user_profile_public():
        try:
            current_identity = get_jwt_identity()
            
            user_id = None
            if isinstance(current_identity, dict):
                user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    user_id = int(current_identity)
                except:
                    user_id = None
            
            if not user_id:
                return jsonify({'error': 'Token inválido'}), 401
            
            update_user_activity(user_id)
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            return jsonify(user.to_dict())
        except Exception as e:
            logger.error(f"Error obteniendo perfil: {e}")
            return jsonify({'error': 'Error obteniendo perfil'}), 500
    
    @app.route('/api/user/bookings', methods=['GET'])
    @jwt_required()
    def get_user_bookings():
        try:
            current_identity = get_jwt_identity()
            
            user_id = None
            if isinstance(current_identity, dict):
                user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    user_id = int(current_identity)
                except:
                    user_id = None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Token inválido'}), 401
            
            update_user_activity(user_id)
            
            bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
            bookings_list = []
            
            for booking in bookings:
                booking_dict = booking.to_dict()
                if booking.tour:
                    booking_dict['tour_nombre'] = booking.tour.nombre
                else:
                    booking_dict['tour_nombre'] = 'Tour no disponible'
                
                bookings_list.append(booking_dict)
            
            return jsonify({
                'success': True,
                'bookings': bookings_list,
                'count': len(bookings_list)
            })
            
        except Exception as e:
            logger.error(f"Get user bookings error: {e}")
            return jsonify({'success': False, 'error': 'Error obteniendo reservas'}), 500
    
    # ========== RUTAS DE ADMINISTRADOR ==========
    
    # Dashboard admin
    @app.route('/api/admin/dashboard', methods=['GET'])
    @admin_required
    def admin_dashboard():
        try:
            stats = {
                'total_users': User.query.count(),
                'total_tours': Tour.query.count(),
                'total_bookings': Booking.query.count(),
                'total_blog_posts': BlogPost.query.count(),
                'pending_bookings': Booking.query.filter_by(estado='pending').count(),
                'active_tours': Tour.query.filter_by(disponible=True).count(),
                'active_users': User.query.filter_by(activo=True).count(),
                'recent_registrations': User.query.filter(
                    User.created_at > (datetime.utcnow() - timedelta(days=7))
                ).count()
            }
            
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Error dashboard admin: {e}")
            return jsonify({'error': 'Error obteniendo estadísticas'}), 500
    
    # Gestión de usuarios
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_all_users():
        try:
            users = User.query.all()
            users_list = [user.to_dict() for user in users]
            
            return jsonify({
                'success': True,
                'users': users_list,
                'count': len(users_list)
            })
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            return jsonify({'success': False, 'error': 'Error obteniendo usuarios'}), 500
    
    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    @admin_required
    def update_user(user_id):
        try:
            data = request.get_json()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
            
            if 'nombre' in data:
                user.nombre = data['nombre']
            if 'email' in data:
                user.email = data['email']
            if 'telefono' in data:
                user.telefono = data['telefono']
            if 'rol' in data:
                user.rol = data['rol']
            if 'activo' in data:
                user.activo = data['activo']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuario actualizado correctamente',
                'user': user.to_dict()
            })
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al actualizar usuario'}), 500
    
    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @admin_required
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
            
            # No permitir eliminar al propio usuario admin
            current_identity = get_jwt_identity()
            current_user_id = None
            if isinstance(current_identity, dict):
                current_user_id = current_identity.get('id')
            elif isinstance(current_identity, (int, str)):
                try:
                    current_user_id = int(current_identity)
                except:
                    current_user_id = None
            
            if current_user_id == user_id:
                return jsonify({'success': False, 'error': 'No puedes eliminar tu propia cuenta'}), 400
            
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuario eliminado correctamente'
            })
        except Exception as e:
            logger.error(f"Error eliminando usuario: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al eliminar usuario'}), 500
    
    # Gestión de tours
    @app.route('/api/admin/tours', methods=['POST'])
    @admin_required
    def create_tour():
        try:
            data = request.get_json()
            
            required_fields = ['nombre', 'descripcion', 'precio', 'capacidad', 'duracion']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400
            
            tour = Tour(
                nombre=data['nombre'],
                descripcion=data['descripcion'],
                precio=float(data['precio']),
                capacidad=int(data['capacidad']),
                duracion=data['duracion'],
                disponible=data.get('disponible', True),
                imagen_url=data.get('imagen_url')
            )
            
            db.session.add(tour)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Tour creado correctamente',
                'tour': tour.to_dict()
            }), 201
        except Exception as e:
            logger.error(f"Error creando tour: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al crear tour'}), 500
    
    @app.route('/api/admin/tours/<int:tour_id>', methods=['PUT'])
    @admin_required
    def update_tour(tour_id):
        try:
            data = request.get_json()
            tour = Tour.query.get(tour_id)
            
            if not tour:
                return jsonify({'success': False, 'error': 'Tour no encontrado'}), 404
            
            if 'nombre' in data:
                tour.nombre = data['nombre']
            if 'descripcion' in data:
                tour.descripcion = data['descripcion']
            if 'precio' in data:
                tour.precio = float(data['precio'])
            if 'capacidad' in data:
                tour.capacidad = int(data['capacidad'])
            if 'duracion' in data:
                tour.duracion = data['duracion']
            if 'disponible' in data:
                tour.disponible = data['disponible']
            if 'imagen_url' in data:
                tour.imagen_url = data['imagen_url']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Tour actualizado correctamente',
                'tour': tour.to_dict()
            })
        except Exception as e:
            logger.error(f"Error actualizando tour: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al actualizar tour'}), 500
    
    @app.route('/api/admin/tours/<int:tour_id>', methods=['DELETE'])
    @admin_required
    def delete_tour(tour_id):
        try:
            tour = Tour.query.get(tour_id)
            
            if not tour:
                return jsonify({'success': False, 'error': 'Tour no encontrado'}), 404
            
            # Verificar si hay reservas asociadas
            bookings_count = Booking.query.filter_by(tour_id=tour_id).count()
            if bookings_count > 0:
                return jsonify({
                    'success': False, 
                    'error': f'No se puede eliminar el tour porque tiene {bookings_count} reservas asociadas'
                }), 400
            
            db.session.delete(tour)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Tour eliminado correctamente'
            })
        except Exception as e:
            logger.error(f"Error eliminando tour: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al eliminar tour'}), 500
    
    # Gestión de blog
    @app.route('/api/admin/blog', methods=['POST'])
    @admin_required
    def create_blog_post():
        try:
            data = request.get_json()
            
            required_fields = ['titulo', 'contenido']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'success': False, 'error': f'El campo {field} es requerido'}), 400
            
            post = BlogPost(
                titulo=data['titulo'],
                contenido=data['contenido'],
                excerpt=data.get('excerpt', ''),
                categoria=data.get('categoria', 'noticias'),
                autor=data.get('autor', 'Administrador'),
                imagen_url=data.get('imagen_url'),
                publicado=data.get('publicado', False),
                vistas=0
            )
            
            db.session.add(post)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Artículo creado correctamente',
                'post': post.to_dict()
            }), 201
        except Exception as e:
            logger.error(f"Error creando artículo: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al crear artículo'}), 500
    
    @app.route('/api/admin/blog/<int:post_id>', methods=['PUT'])
    @admin_required
    def update_blog_post(post_id):
        try:
            data = request.get_json()
            post = BlogPost.query.get(post_id)
            
            if not post:
                return jsonify({'success': False, 'error': 'Artículo no encontrado'}), 404
            
            if 'titulo' in data:
                post.titulo = data['titulo']
            if 'contenido' in data:
                post.contenido = data['contenido']
            if 'excerpt' in data:
                post.excerpt = data['excerpt']
            if 'categoria' in data:
                post.categoria = data['categoria']
            if 'autor' in data:
                post.autor = data['autor']
            if 'imagen_url' in data:
                post.imagen_url = data['imagen_url']
            if 'publicado' in data:
                post.publicado = data['publicado']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Artículo actualizado correctamente',
                'post': post.to_dict()
            })
        except Exception as e:
            logger.error(f"Error actualizando artículo: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al actualizar artículo'}), 500
    
    @app.route('/api/admin/blog/<int:post_id>', methods=['DELETE'])
    @admin_required
    def delete_blog_post(post_id):
        try:
            post = BlogPost.query.get(post_id)
            
            if not post:
                return jsonify({'success': False, 'error': 'Artículo no encontrado'}), 404
            
            db.session.delete(post)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Artículo eliminado correctamente'
            })
        except Exception as e:
            logger.error(f"Error eliminando artículo: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al eliminar artículo'}), 500
    
    # Gestión de reservas (admin)
    @app.route('/api/admin/bookings', methods=['GET'])
    @admin_required
    def get_all_bookings():
        try:
            bookings = Booking.query.order_by(Booking.created_at.desc()).all()
            bookings_list = []
            
            for booking in bookings:
                booking_dict = booking.to_dict()
                if booking.tour:
                    booking_dict['tour_nombre'] = booking.tour.nombre
                if booking.user:
                    booking_dict['user_nombre'] = booking.user.nombre
                    booking_dict['user_email'] = booking.user.email
                
                bookings_list.append(booking_dict)
            
            return jsonify({
                'success': True,
                'bookings': bookings_list,
                'count': len(bookings_list)
            })
        except Exception as e:
            logger.error(f"Error obteniendo reservas: {e}")
            return jsonify({'success': False, 'error': 'Error obteniendo reservas'}), 500
    
    @app.route('/api/admin/bookings/<int:booking_id>', methods=['PUT'])
    @admin_required
    def update_booking(booking_id):
        try:
            data = request.get_json()
            booking = Booking.query.get(booking_id)
            
            if not booking:
                return jsonify({'success': False, 'error': 'Reserva no encontrada'}), 404
            
            if 'estado' in data:
                booking.estado = data['estado']
            if 'fecha' in data:
                booking.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            if 'personas' in data:
                booking.personas = int(data['personas'])
            if 'total' in data:
                booking.total = float(data['total'])
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Reserva actualizada correctamente',
                'booking': booking.to_dict()
            })
        except Exception as e:
            logger.error(f"Error actualizando reserva: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al actualizar reserva'}), 500
    
    @app.route('/api/admin/bookings/<int:booking_id>', methods=['DELETE'])
    @admin_required
    def delete_booking(booking_id):
        try:
            booking = Booking.query.get(booking_id)
            
            if not booking:
                return jsonify({'success': False, 'error': 'Reserva no encontrada'}), 404
            
            db.session.delete(booking)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Reserva eliminada correctamente'
            })
        except Exception as e:
            logger.error(f"Error eliminando reserva: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Error al eliminar reserva'}), 500
    
    # ========== MIDDLEWARE Y MANEJADORES DE ERROR ==========
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin in app.config['CORS_ORIGINS']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        return response
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'not_found',
            'message': 'Endpoint no encontrado',
            'path': request.path,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server error: {error}')
        return jsonify({
            'success': False,
            'error': 'internal_server_error',
            'message': 'Error interno del servidor',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'unauthorized',
            'message': 'No autorizado',
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'forbidden',
            'message': 'Acceso prohibido',
            'timestamp': datetime.utcnow().isoformat()
        }), 403
    
    # ========== IMPRIMIR RESUMEN ==========
    print("\n" + "="*60)
    print("✅ APLICACIÓN CREADA EXITOSAMENTE")
    print(f"📍 Entorno: {'PythonAnywhere (ricardjf)' if IS_PYTHONANYWHERE else 'Desarrollo Local'}")
    if IS_PYTHONANYWHERE:
        print(f"📡 URL: https://ricardjf.pythonanywhere.com")
    else:
        print(f"📡 URL: http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"🗄️  Base de datos: {app.config['SQLALCHEMY_DATABASE_URI'][:70]}...")
    print(f"🔐 Admin: admin@canosalao.com / admin123")
    print(f"🌍 CORS Origins: {len(app.config['CORS_ORIGINS'])} configurados")
    print("="*60)
    print("📋 Endpoints disponibles:")
    print("  • GET  /                    - Página de inicio")
    print("  • GET  /health              - Health check")
    print("  • POST /api/auth/login      - Iniciar sesión")
    print("  • POST /api/auth/register   - Registrarse")
    print("  • GET  /api/auth/verify     - Verificar token")
    print("  • POST /api/auth/refresh    - Refrescar token")
    print("  • GET  /api/tours           - Listar tours")
    print("  • GET  /api/blog            - Listar posts del blog")
    print("="*60)
    
    return app

# ========== CREAR APLICACIÓN ==========
app = create_app()

# ========== SOLO PARA DESARROLLO LOCAL ==========
if __name__ == '__main__':
    # Solo se ejecuta en desarrollo local
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Iniciando servidor en puerto {port}...")
    app.run(
        host=app.config['HOST'],
        port=port,
        debug=app.config['DEBUG']
    )
