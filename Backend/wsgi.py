import sys
import os

path = '/home/Ricadjf/cano-salao-backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'true'
os.environ['SECRET_KEY'] = 'cano-salao-secret-key-2024-pythonanywhere'
os.environ['JWT_SECRET_KEY'] = 'cano-salao-jwt-secret-key-2024-pythonanywhere'
os.environ['CORS_ORIGINS'] = 'https://ricardjf.github.io'

try:
    from app import app as application
    print("✅ App importada correctamente")
except Exception as e:
    print(f"❌ Error: {e}")
    raise
