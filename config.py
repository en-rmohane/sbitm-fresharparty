import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sanskriti_festive_royal_secret_key_2026_blessings')
    IS_VERCEL = IS_VERCEL
    
    # Database Configuration:
    # Supports external PostgreSQL/MySQL (e.g. Neon, Supabase, Railway) via DATABASE_URL.
    # On Vercel without DATABASE_URL, defaults to writable /tmp/sanskriti_2026.db.
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    elif IS_VERCEL:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/sanskriti_2026.db'
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "instance", "sanskriti_2026.db")}'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads configuration (uses /tmp on Vercel to respect read-only root)
    if IS_VERCEL:
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
        
    SIGNATURE_FOLDER = os.path.join(UPLOAD_FOLDER, 'signatures')
    SELFIE_FOLDER = os.path.join(UPLOAD_FOLDER, 'selfies')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # Security headers and cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 7200  # 2 hours
