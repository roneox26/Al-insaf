from app import app as application

# For backwards compatibility
app = application

if __name__ == '__main__':
    # Run auto-migration on startup
    try:
        from auto_migrate import auto_migrate
        auto_migrate()
    except Exception as e:
        print(f"Migration skipped: {e}")
    
    import os
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    application.run(host=host, port=port, debug=False)
