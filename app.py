from flask import Flask,render_template,request,redirect, session, url_for
from init_db import app, get_db, insert_db, query_db
app = Flask(__name__)

@app.route("/")
def top():
    return render_template("index.html")

@app.route("/register/",methods=["GET", "POST"])
def register():
    if "userid" in session:

        return redirect(url_for("Profile.html", user=user))
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
        return redirect(url_for("Profile.html", user=user))
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

        return render_template("Profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("top"))

@app.route("/<int:userid>/profile", methods=["POST"])
def profile():
    if "userid" not in session:
        return redirect(url_for("login"))
    elif "userid" in session[userid]:
        if request.method == "POST":
            return render_template("Update.html", user=user)

@app.route("/<int:userid>/update", methods=["POST"])
def update(user):
    if "userid" not in session:
        return redirect(url_for("login"))
    elif "userid" in session[userid]:
        if request.method == "POST":
            if  request.form.get("name") is None:
                pass
            else:
                session["username"] = request.form.get("name")

            if  request.form.get("email") is None:
                pass
            elif "@" not in request.form.get("email"):
                return redirect(url_for("update"))
            else:
                if useremail == request.form.get("email"):
                    return redirect(url_for("update"))
                session["useremail"] = request.form.get("email")

            if request.form.get("password") is None:
                pass
            elif len(request.form.get("password")) <= 5:
                return redirect(url_for("update"))

                modify_db("UPDATE user \
                           SET name=?, email=?, password=?, \
                           WHERE id=?",
                           (session['name'], session['email'],request.form.get("password")))
            return render_template ('profile', user=user)


if __name__ == '__main__':
    app.secret_key = "jijjkla"
    app.run()
