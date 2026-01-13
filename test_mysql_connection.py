"""
Test MySQL Connection
"""

import os
from sqlalchemy import create_engine, text

print("🔍 Testing MySQL Connection...\n")

# Get MySQL credentials
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'ngo_db')

if not MYSQL_PASSWORD:
    MYSQL_PASSWORD = input("Enter MySQL password: ")

mysql_url = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4'

print(f"Host: {MYSQL_HOST}")
print(f"User: {MYSQL_USER}")
print(f"Database: {MYSQL_DB}")
print(f"\nConnecting...\n")

try:
    engine = create_engine(mysql_url, echo=False)
    
    with engine.connect() as conn:
        # Test query
        result = conn.execute(text("SELECT VERSION()"))
        version = result.fetchone()[0]
        
        print("✅ Connection Successful!")
        print(f"📊 MySQL Version: {version}")
        
        # Check database
        result = conn.execute(text("SELECT DATABASE()"))
        db_name = result.fetchone()[0]
        print(f"🗄️  Current Database: {db_name}")
        
        # List tables
        result = conn.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        
        if tables:
            print(f"\n📋 Tables in database ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("\n⚠️  No tables found. Run migration script to create tables.")
        
        print("\n✅ MySQL is ready to use!")
        
except Exception as e:
    print(f"❌ Connection Failed!")
    print(f"Error: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Check if MySQL server is running")
    print("2. Verify username and password")
    print("3. Make sure database exists:")
    print(f"   CREATE DATABASE {MYSQL_DB};")
    print("4. Check user permissions:")
    print(f"   GRANT ALL PRIVILEGES ON {MYSQL_DB}.* TO '{MYSQL_USER}'@'localhost';")
