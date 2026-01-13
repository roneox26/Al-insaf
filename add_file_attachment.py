"""Add file attachment support to messages table"""
import sqlite3
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join('instance', 'loan.db')

if not os.path.exists(db_path):
    print("Database not found!")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(messages)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    if 'file_path' not in columns:
        print("Adding file_path column...")
        cursor.execute("ALTER TABLE messages ADD COLUMN file_path TEXT")
        print("+ file_path added")
    
    if 'file_type' not in columns:
        print("Adding file_type column...")
        cursor.execute("ALTER TABLE messages ADD COLUMN file_type TEXT")
        print("+ file_type added")
    
    # Create uploads/messages directory
    upload_dir = os.path.join('static', 'uploads', 'messages')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"+ Created directory: {upload_dir}")
    
    conn.commit()
    print("\n✓ File attachment support added!")
    print("\nYou can now send:")
    print("  • Images (JPG, PNG, GIF)")
    print("  • PDFs")
    print("  • Documents (DOC, DOCX)")
    print("  • Excel files (XLS, XLSX)")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nPress Enter to exit...")
input()
