from flask import Flask,render_template,request,redirect, session, url_for
from init_db import app, get_db, insert_db, modify_db, query_db
from text_db import app, text_get, text_insert, text_modify, text_query
app = Flask(__name__)

@app.route("/")
def top():
    texts = text_query("SELECT * FROM text")
    if "userid" in session:
        return render_template("index.html",user="online", texts=texts)
    return render_template("index.html", texts=texts)


@app.route("/register/",methods=["GET", "POST"])
def register():
    if "userid" in session:
        return redirect(url_for("profile", userid=session["userid"]))
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        if "@" not in request.form.get("email"):
            return redirect(url_for("register"))
        if len(request.form.get("password")) <= 5:
            return redirect(url_for("register"))
        session["username"] = request.form.get("name")
        session["useremail"] = request.form.get("email")
        session["usergender"] = request.form.get("gender")

        insert_db("INSERT INTO user (name, email, password, gender, age) \
                   VALUES(?, ?, ?, ?, ?)",
                   (session["username"],session["useremail"],request.form.get("password"),session["usergender"],request.form.get("age")))
        user = query_db("SELECT * FROM user WHERE email = ?", (session["useremail"],), True)
        session["userid"] = user["id"]
        return render_template("Profile.html", user=user)

@app.route("/view")
def view():
    if "userid" not in session:
        return redirect(url_for("login"))
    users = query_db("SELECT * FROM user")
    return render_template("view.html", users=users)

@app.route("/login",methods=["GET", "POST"])
def login():
    if "userid" in session:
        return redirect(url_for("profile", userid=session["userid"]))
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if "@" not in request.form.get("email"):
            return redirect(url_for("login"))
        if len(request.form.get("password")) <= 5:
            return redirect(url_for("login"))
        session["username"] = request.form.get("name")
        session["useremail"] = request.form.get("email")
        user = query_db("SELECT * FROM user WHERE email = ?", (session["useremail"],), True)
        if user == None:
            return redirect(url_for("login"))
        if user["password"] != request.form.get("password"):
            return redirect(url_for("login"))
        session["userid"] = user["id"]

        return redirect(url_for("profile", userid=session["userid"]))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("top"))

@app.route("/<int:userid>/")
def profile(userid):
    if "userid" not in session:
        return redirect(url_for("login"))

    user = query_db("SELECT * FROM user WHERE id = ?", (userid,), True)
    if int(userid) != session["userid"]:
        return render_template("Profile.html", user=user, f=0)
    else:
        return render_template("Profile.html", user=user, f=1)

@app.route("/<int:userid>/update", methods=["GET", "POST"])
def update(userid):
    if "userid" not in session:
        return redirect(url_for("login"))
    elif int(userid) != session["userid"]:
        return redirect(url_for("profile", userid=session["userid"]))
    else:
        if request.method == "POST":
            if "@" not in request.form.get("email"):
                return redirect(url_for("update"))

            session["username"] = request.form.get("name")
            session["useremail"] = request.form.get("email")

            if len(request.form.get("password")) <= 5:
                return redirect(url_for("update"))

            modify_db("UPDATE user \
                         SET name=?, email=?, password=? WHERE id=?",
                           (session['username'], session['useremail'],request.form.get("password"), session['userid']))
            return redirect(url_for('profile', userid=session["userid"]))
        elif request.method == "GET":
            user = query_db("SELECT * FROM user WHERE id = ?", (userid,), True)
            return render_template("Update.html", user=user)

if __name__ == '__main__':
    app.secret_key = "jijjkla"
    app.run()
