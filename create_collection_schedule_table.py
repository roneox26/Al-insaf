import sqlite3

# Connect to database
conn = sqlite3.connect('instance/loan.db')
cursor = conn.cursor()

# Create collection_schedule table
cursor.execute('''
CREATE TABLE IF NOT EXISTS collection_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    loan_id INTEGER,
    scheduled_date DATETIME NOT NULL,
    expected_amount FLOAT DEFAULT 0,
    collection_type VARCHAR(20) DEFAULT 'loan',
    status VARCHAR(20) DEFAULT 'pending',
    collected_amount FLOAT DEFAULT 0,
    collected_date DATETIME,
    staff_id INTEGER,
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(id)
)
''')

conn.commit()
conn.close()

print("Collection Schedule table created successfully!")
print("Collection Schedule System is now ready!")
print("Access it at: /collection_schedule")
