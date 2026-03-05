import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB Configuration
MONGODB_SETTINGS = {
    'host': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/ngo_db'),
    'connect': False,
}

JSON_AS_ASCII = False
