from flask import Flask, g
import sqlite3
from os import path

app = Flask(__name__)

def init_db(data):
    with app.app_context():
        db = get_db(data)
        with app.open_resource('models/'+data+'.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db(data):
    g._database = sqlite3.connect('models/'+data+'.db')
    db = g._database
    db.row_factory = sqlite3.Row     # results of queries are of nametuple type
    return db

def modify_db(data, query, args=()):
    db = get_db(data)
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    return None

def query_db(data, query, args=(), one=False):
    cur = get_db(data).execute(query, args)
    data = cur.fetchall()
    cur.close()
    return (data[0] if data else None) if one else data

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db != None:
        db.close()

if __name__ == '__main__':
    if not path.exists("models/user.db"):
        print('Initializing "user.db"...')
        init_db("user")
        print('Done.')
    if not path.exists("models/title.db"):
        print('Initializing "title.db"...')
        init_db("title")
        print('Done.')
    if not path.exists("models/comment.db"):
        print('Initializing "comment.db"...')
        init_db("comment")
        print('Done.')
