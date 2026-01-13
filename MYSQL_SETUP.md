# MySQL Database Setup Guide

## 📋 Prerequisites

1. Install MySQL Server
2. Install Python MySQL driver

## 🔧 Installation Steps

### 1. Install MySQL Dependencies

```bash
pip install PyMySQL cryptography
```

### 2. Create MySQL Database

Open MySQL command line or phpMyAdmin and run:

```sql
CREATE DATABASE ngo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure Database Connection

Create a `.env` file in the project root:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DB=ngo_db
```

Or set environment variables directly in your system.

### 4. Migrate Data from SQLite to MySQL

Run the migration script:

```bash
python migrate_to_mysql.py
```

### 5. Run the Application

```bash
python run.py
```

## 🔄 Manual Configuration

If you don't want to use environment variables, edit `config.py`:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'ngo_db'
```

## 📊 Database Connection Strings

### MySQL (Default)
```
mysql+pymysql://root:password@localhost/ngo_db?charset=utf8mb4
```

### SQLite (Fallback)
```
sqlite:///loan.db
```

## ⚠️ Important Notes

1. **Backup your SQLite database** before migration
2. MySQL password is required for MySQL connection
3. If MySQL password is empty, system will use SQLite
4. Make sure MySQL server is running
5. Grant proper permissions to MySQL user

## 🔐 MySQL User Permissions

```sql
GRANT ALL PRIVILEGES ON ngo_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

## 🐛 Troubleshooting

### Connection Error
- Check if MySQL server is running
- Verify username and password
- Check if database exists

### Character Encoding Issues
- Use utf8mb4 charset for Bengali support
- Set collation to utf8mb4_unicode_ci

### Port Issues
- Default MySQL port: 3306
- Add port to connection string if different:
  ```
  mysql+pymysql://user:pass@localhost:3307/ngo_db
  ```

## 📱 For Production (cPanel/Hosting)

1. Create MySQL database from cPanel
2. Note down:
   - Database name
   - Database user
   - Database password
   - Host (usually localhost)
3. Update `.env` file with these credentials
4. Run migration script
5. Deploy application

## ✅ Verify Connection

Run this to test connection:

```bash
python test_mysql_connection.py
```
