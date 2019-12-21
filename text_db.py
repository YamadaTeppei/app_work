from flask import Flask, g
import sqlite3

app = Flask(__name__)
DATABASE = 'models/text.db'

def init_db():
    with app.app_context():
        db = text_get()
        with app.open_resource('models/text.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def text_get():
    db = getattr(g, '_database', None)
    if db == None:
        g._database = sqlite3.connect(DATABASE)
        db = g._database
        db.row_factory = sqlite3.Row     # results of queries are of nametuple type
    return db

def text_modify(query, args=()):
    db = text_get()
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    return None

def text_insert(query, args=()):
    db = text_get()
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    return None

def text_query(query, args=(), one=False):
    cur = text_get().execute(query, args)
    data = cur.fetchall()
    cur.close()
    return (data[0] if data else None) if one else data

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db != None:
        db.close()

if __name__ == '__main__':
    init_db()
