import os
import sys

# Get DATABASE_URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    print("Usage: set DATABASE_URL=postgresql://user:password@host/dbname")
    sys.exit(1)

os.environ['DATABASE_URL'] = DATABASE_URL

from app import app, init_db

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=False)
