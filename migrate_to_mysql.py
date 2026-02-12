"""
SQLite to MySQL Migration Script
Migrates all data from SQLite database to MySQL
"""

import os
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

# SQLite connection
SQLITE_DB = 'instance/loan.db'
sqlite_engine = create_engine(f'sqlite:///{SQLITE_DB}')

# MySQL connection - Update these values
MYSQL_USER = input("Enter MySQL username (default: root): ") or 'root'
MYSQL_PASSWORD = input("Enter MySQL password: ")
MYSQL_HOST = input("Enter MySQL host (default: localhost): ") or 'localhost'
MYSQL_DB = input("Enter MySQL database name (default: ngo_db): ") or 'ngo_db'

mysql_url = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}?charset=utf8mb4'

print(f"\n🔄 Connecting to MySQL: {MYSQL_HOST}/{MYSQL_DB}")

try:
    mysql_engine = create_engine(mysql_url, echo=False)
    
    # Test connection
    with mysql_engine.connect() as conn:
        print("✅ MySQL connection successful!")
        
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")
    print("\n💡 Make sure:")
    print("1. MySQL server is running")
    print("2. Database exists: CREATE DATABASE ngo_db;")
    print("3. User has proper permissions")
    sys.exit(1)

# Create tables in MySQL from SQLite schema
print("\n📋 Creating tables in MySQL...")
from app import db, app

with app.app_context():
    # Drop all tables in MySQL (be careful!)
    db.drop_all()
    print("🗑️  Dropped existing tables")
    
    # Create all tables
    db.create_all()
    print("✅ Created all tables")

# Migrate data
print("\n📦 Migrating data...")

sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=sqlite_engine)

mysql_metadata = MetaData()
mysql_metadata.reflect(bind=mysql_engine)

SQLiteSession = sessionmaker(bind=sqlite_engine)
MySQLSession = sessionmaker(bind=mysql_engine)

sqlite_session = SQLiteSession()
mysql_session = MySQLSession()

tables_to_migrate = [
    'user', 'customer', 'loan', 'saving', 'collection', 
    'loan_collection', 'saving_collection', 'expense', 
    'cash_balance', 'investor', 'investment', 'withdrawal',
    'fee_collection', 'message', 'note', 'scheduled_expense',
    'followup', 'collection_schedule'
]

total_records = 0

for table_name in tables_to_migrate:
    if table_name not in sqlite_metadata.tables:
        print(f"⚠️  Table '{table_name}' not found in SQLite, skipping...")
        continue
    
    try:
        sqlite_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)
        mysql_table = Table(table_name, mysql_metadata, autoload_with=mysql_engine)
        
        # Read data from SQLite
        with sqlite_engine.connect() as conn:
            select_stmt = sqlite_table.select()
            result = conn.execute(select_stmt)
            rows = result.fetchall()
            
            if rows:
                # Insert into MySQL using parameterized queries
                with mysql_engine.connect() as mysql_conn:
                    for row in rows:
                        row_dict = dict(row._mapping)
                        insert_stmt = mysql_table.insert().values(row_dict)
                        mysql_conn.execute(insert_stmt)
                    mysql_conn.commit()
                
                print(f"✅ Migrated {len(rows)} records from '{table_name}'")
                total_records += len(rows)
            else:
                print(f"ℹ️  No data in '{table_name}'")
                
    except Exception as e:
        print(f"❌ Error migrating '{table_name}': {e}")
        continue

print(f"\n🎉 Migration completed!")
print(f"📊 Total records migrated: {total_records}")
print(f"\n✅ Your application is now using MySQL database!")
print(f"🔗 Connection: {MYSQL_HOST}/{MYSQL_DB}")

# Update .env file
# Sanitize values to prevent file injection
import re

def sanitize_env_value(value):
    """Remove newlines and special characters to prevent injection"""
    # Remove newlines, carriage returns, and null bytes
    return re.sub(r'[\r\n\x00]', '', str(value))

env_content = f"""# MySQL Database Configuration
MYSQL_HOST={sanitize_env_value(MYSQL_HOST)}
MYSQL_USER={sanitize_env_value(MYSQL_USER)}
MYSQL_PASSWORD={sanitize_env_value(MYSQL_PASSWORD)}
MYSQL_DB={sanitize_env_value(MYSQL_DB)}
"""

# Validate content before writing
if '\x00' in env_content or len(env_content) > 10000:
    print("❌ Error: Invalid configuration data")
    sys.exit(1)

with open('.env', 'w', encoding='utf-8') as f:
    f.write('# MySQL Database Configuration\n')
    f.write(f'MYSQL_HOST={sanitize_env_value(MYSQL_HOST)}\n')
    f.write(f'MYSQL_USER={sanitize_env_value(MYSQL_USER)}\n')
    f.write(f'MYSQL_PASSWORD={sanitize_env_value(MYSQL_PASSWORD)}\n')
    f.write(f'MYSQL_DB={sanitize_env_value(MYSQL_DB)}\n')

print(f"\n📝 Created .env file with MySQL configuration")
print("\n⚠️  IMPORTANT: Backup your SQLite database before deleting it!")
print(f"📁 SQLite backup location: {SQLITE_DB}")
