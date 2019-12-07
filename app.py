from flask import Flask,render_template,request,redirect
from init_db import app, get_db, insert_db, query_db
app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register",methods=["POST"])
def register():
    if not request.form.get("name") or not request.form.get("email") \
            or not request.form.get("password") or not request.form.get("gender"):
        return redirect("/")
    elif len(request.form.get("password")) <= 5:
        return redirect("/")
    else:
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        gender = request.form.get("gender")
        age = request.form.get("age")
        insert_db("INSERT INTO user (name, email, password, gender, age) \
                   VALUES(?, ?, ?, ?, ?)", (name, email, password, gender, age))
        user = query_db("SELECT * FROM user WHERE email = ?", (email,), True)
        return render_template("success.html")

@app.route("/view")
def view():
    users = query_db("SELECT * FROM user")
    return render_template("view.html", users=users)

@app.route("/login",methods=["POST,GET"])
def login():
    if request.method=="GET":
        return render_template("index.html")

    username = request.form["name"]
    userpassword = request.form["password"]

    db = get_db

    user = db.execute('SELECT * FROM user WHERE name = ?', (username,), True)
    user = db.execute('SELECT * FORM user WHERE password = ?', (userpassword,), True)

    session.clear()
    session['user_id'] = user['id']
    return redirect('protected.html')

@app.route("/logout",methods=["POST"])
def logout():
    session.clear()
    return("login.html")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

if __name__ == '__main__':
    app.run()
