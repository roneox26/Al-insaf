import os
os.environ['DATABASE_URL'] = 'postgresql://ngoweb_db_user:REtACHujjdzbn0DspqewJgF4evtzHaDU@dpg-d43kkqgdl3ps73a1a430-a/ngoweb_db'

from app import app, init_db

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
