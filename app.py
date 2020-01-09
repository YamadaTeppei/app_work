from flask import Flask,render_template,request,redirect, session, url_for
from init_db import app, get_db, modify_db, query_db
app = Flask(__name__)
# topページ
@app.route("/")
def top():
    titles = query_db("title", "SELECT * FROM title")
    if "userid" not in session:
        return render_template("index.html", titles=titles)
    return render_template("index.html",user="online", titles=titles)

# ユーザー新規登録ページ
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

        modify_db("user", "INSERT INTO user (name, email, password, gender, age) \
                   VALUES(?, ?, ?, ?, ?)",
                   (session["username"],session["useremail"],request.form.get("password"),session["usergender"],request.form.get("age")))
        user = query_db("user", "SELECT * FROM user WHERE email = ?", (session["useremail"],), True)
        session["userid"] = user["id"]
        return redirect(url_for("profile", userid=session["userid"]))
# ユーザー一覧ページ
@app.route("/view")
def view():
    if "userid" not in session:
        return redirect(url_for("login"))
    users = query_db("user", "SELECT * FROM user")
    return render_template("view.html", users=users)
# ログインページ
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
        user = query_db("user", "SELECT * FROM user WHERE email = ?", (session["useremail"],), True)
        if user == None:
            return redirect(url_for("login"))
        if user["password"] != request.form.get("password"):
            return redirect(url_for("login"))
        session["userid"] = user["id"]

        return redirect(url_for("profile", userid=session["userid"]))
# ログアウト機能
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("top"))
# プロフィールページ
@app.route("/<int:userid>/")
def profile(userid):
    if "userid" not in session:
        return redirect(url_for("login"))
    user = query_db("user", "SELECT * FROM user WHERE id = ?", (userid,), True)
    if int(userid) != session["userid"]:
        return render_template("Profile.html", user=user, f=0)
    else:
        return render_template("Profile.html", user=user, f=1)
# プロフィール変更ページ
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

            modify_db("user", "UPDATE user \
                         SET name=?, email=?, password=? WHERE id=?",
                           (session['username'], session['useremail'],request.form.get("password"), session['userid']))
            return redirect(url_for('profile', userid=session["userid"]))
        elif request.method == "GET":
            user = query_db("user", "SELECT * FROM user WHERE id = ?", (userid,), True)
            return render_template("Update.html", user=user)
# タイトル新規作成ページ
@app.route("/<int:userid>/newtitle", methods=["GET", "POST"])
def newtitle(userid):
    if "userid" not in session:
        return redirect(url_for("login"))
    else:
        if request.method == "GET":
            return render_template("newtitle.html")
        if request.method == "POST":
            modify_db("title", "INSERT INTO title  (name, user_id) VALUES(?, ?)", (request.form.get("title"), session['userid']))
            return redirect(url_for("top"))
# タイトルページ
@app.route("/<int:title_id>/title", methods=["GET", "POST"])
def title(title_id):
    if "userid" in session:
        user = "online"
    if request.method == "GET":
        comments = query_db("comment", "SELECT * FROM comment WHERE title_id = ?", (title_id,))
        title = query_db("title", "SELECT * FROM title WHERE id = ?", (title_id,), True)
        return render_template("title.html",title=title, comments=comments, query_db=query_db, enumerate=enumerate)
    else:
        if "userid" not in session:
            return redirect(url_for("login"))
        else:
            modify_db("comment", "INSERT INTO comment (text_, user_id, title_id) VALUES(?, ?, ?)",
                    (request.form.get("comment"), session["userid"], title_id))
            return redirect(url_for("title", title_id=title_id))


if __name__ == '__main__':
    app.secret_key = "jijjkla"
    app.run()
