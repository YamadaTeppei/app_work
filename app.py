from flask import Flask,render_template,request,redirect
from init_db import app, get_db, insert_db, query_db
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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


if __name__ == '__main__':
    app.run()
