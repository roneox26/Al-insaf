import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# MySQL Configuration
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'ngo_db')

# Database URL - PostgreSQL (Render), MySQL or SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

# Force SQLite for local development if DATABASE_URL points to unavailable server
if DATABASE_URL and 'dpg-d43kkqgdl3ps73a1a430-a' in DATABASE_URL:
    print("Warning: PostgreSQL server unavailable, using SQLite instead")
    DATABASE_URL = None

if not DATABASE_URL:
    # Use MySQL by default, fallback to SQLite if MySQL not configured
    if MYSQL_PASSWORD:
        DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4'
    else:
        # Use instance folder for SQLite in production
        import pathlib
        instance_path = pathlib.Path(__file__).parent / 'instance'
        instance_path.mkdir(exist_ok=True)
        DATABASE_URL = f'sqlite:///{instance_path}/loan.db'

# Fix for Render PostgreSQL URL
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
}
JSON_AS_ASCII = False