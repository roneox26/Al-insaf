from app import app as application

# For backwards compatibility
app = application

if __name__ == '__main__':
    import os
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    application.run(host=host, port=port, debug=False)
