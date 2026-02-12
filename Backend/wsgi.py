# wsgi.py - Archivo WSGI para PythonAnywhere
import sys
import os

# Agregar el path de tu aplicación
path = '/home/Ricadjf/cano-salao-backend'
if path not in sys.path:
    sys.path.append(path)

# Configurar variables de entorno para producción
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'true'

# IMPORTANTE: Configura estas variables en PythonAnywhere Web > Environment variables
# SECRET_KEY=tu-clave-secreta-aqui
# JWT_SECRET_KEY=tu-jwt-secreta-aqui
# CORS_ORIGINS=https://ricardjf.github.io

# Importar la aplicación Flask
try:
    from app import app as application
    print("✅ Aplicación Flask importada correctamente")
except Exception as e:
    print(f"❌ Error importando aplicación: {e}")
    raise