import sys
import os

# ✅ RUTA CORREGIDA - usuario ricardjf
path = '/home/ricardjf/cano-salao-backend'
if path not in sys.path:
    sys.path.append(path)

# Configurar variables de entorno
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'true'

# ⚠️ IMPORTANTE: Configurar estas variables en PythonAnywhere Web > Environment variables
# SECRET_KEY = tu-clave-secreta
# JWT_SECRET_KEY = tu-jwt-secreta
# CORS_ORIGINS = https://ricardjf.github.io

try:
    from app import app as application
    print("✅ Aplicación Flask importada correctamente")
except Exception as e:
    print(f"❌ Error importando aplicación: {e}")
    raise
