"""Quick fix to add sender_id and receiver_id columns to messages table"""
import sqlite3
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join('instance', 'loan.db')

if not os.path.exists(db_path):
    print("Database not found!")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check existing columns
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add sender_id if not exists
    if 'sender_id' not in columns:
        print("Adding sender_id column...")
        cursor.execute("ALTER TABLE messages ADD COLUMN sender_id INTEGER")
        print("✓ sender_id added")
    
    # Add receiver_id if not exists
    if 'receiver_id' not in columns:
        print("Adding receiver_id column...")
        cursor.execute("ALTER TABLE messages ADD COLUMN receiver_id INTEGER")
        print("✓ receiver_id added")
    
    # Get admin ID
    cursor.execute("SELECT id FROM user WHERE role='admin' LIMIT 1")
    admin_row = cursor.fetchone()
    
    if admin_row:
        admin_id = admin_row[0]
        print(f"Admin ID: {admin_id}")
        
        # Migrate old messages (admin sent to staff_id)
        cursor.execute("SELECT id, staff_id FROM messages WHERE sender_id IS NULL")
        old_messages = cursor.fetchall()
        
        if old_messages:
            print(f"Migrating {len(old_messages)} old messages...")
            for msg_id, staff_id in old_messages:
                if staff_id:
                    cursor.execute(
                        "UPDATE messages SET sender_id=?, receiver_id=? WHERE id=?",
                        (admin_id, staff_id, msg_id)
                    )
            print(f"✓ Migrated {len(old_messages)} messages")
    
    conn.commit()
    print("\n✅ Database updated successfully!")
    print("You can now use the new messaging system.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nPress Enter to exit...")
input()
