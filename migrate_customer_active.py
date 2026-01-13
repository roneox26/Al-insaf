import sqlite3
import os

def migrate():
    db_path = os.path.join('instance', 'loan.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(customers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_active' not in columns:
            print("Adding is_active column...")
            cursor.execute('ALTER TABLE customers ADD COLUMN is_active INTEGER DEFAULT 1')
            conn.commit()
            print("Column added successfully!")
            
            # Update all existing customers to be active
            cursor.execute('UPDATE customers SET is_active = 1 WHERE is_active IS NULL')
            conn.commit()
            print("All customers set to active")
        else:
            print("is_active column already exists")
        
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate()
