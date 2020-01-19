from flask import Flask,render_template,request,redirect, session, url_for
from init_db import app, get_db, modify_db, query_db
app = Flask(__name__)
# topページ
@app.route("/")
def top(titles=None, search=None):
    if titles:
        page = "検索結果:" + search
        return redirect(url_for("index", titles=titles, page=page))
    else:
        page = "TOPページ"
        titles = query_db("title", "SELECT * FROM title")
        if "userid" not in session:
            return render_template("index.html", titles=titles, page=page)
        return render_template("index.html",online="online", titles=titles, page=page)

# ユーザー新規登録ページ
@app.route("/register/",methods=["GET", "POST"])
def register():
    if "userid" in session:
        return redirect(url_for("profile", userid=session["userid"], online="online", profile="active"))
    if request.method == "GET":
        return render_template("register.html", register="active")
    elif request.method == "POST":
        if "@" not in request.form.get("email"):
            return redirect(url_for("register", register="active"))
        if len(request.form.get("password")) <= 5:
            return redirect(url_for("register", register="active"))
        session["username"] = request.form.get("name")
        session["useremail"] = request.form.get("email")
        session["usergender"] = request.form.get("gender")

        modify_db("user", "INSERT INTO user (name, email, password, gender, age) \
                   VALUES(?, ?, ?, ?, ?)",
                   (session["username"],session["useremail"],request.form.get("password"),session["usergender"],request.form.get("age")))
        user = query_db("user", "SELECT * FROM user WHERE email = ?", (session["useremail"],), True)
        session["userid"] = user["id"]
        return redirect(url_for("profile", userid=session["userid"], online="online", profile="active"))
# ユーザー一覧ページ
@app.route("/view")
def view():
    if "userid" not in session:
        return redirect(url_for("login", login="active"))
    users = query_db("user", "SELECT * FROM user")
    return render_template("view.html", users=users)
# ログインページ
@app.route("/login",methods=["GET", "POST"])
def login():
    if "userid" in session:
        return redirect(url_for("profile", userid=session["userid"], online="online", profile="active"))
    if request.method == "GET":
        return render_template("login.html", login="active")
    elif request.method == "POST":
        if "@" not in request.form.get("email"):
            return redirect(url_for("login", login="active"))
        if len(request.form.get("password")) <= 5:
            return redirect(url_for("login", login="active"))
        session["username"] = request.form.get("name")
        session["useremail"] = request.form.get("email")
        user = query_db("user", "SELECT * FROM user WHERE email = ?", (session["useremail"],), True)
        if user == None:
            return redirect(url_for("login", login="active"))
        if user["password"] != request.form.get("password"):
            return redirect(url_for("login", login="active"))
        session["userid"] = user["id"]

        return redirect(url_for("profile", userid=session["userid"], online="online", profile="active"))
# ログアウト機能
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("top"))
# プロフィールページ
@app.route("/<int:userid>/")
def profile(userid):
    if "userid" not in session:
        return redirect(url_for("login", login="active"))
    user = query_db("user", "SELECT * FROM user WHERE id = ?", (userid,), True)
    if int(userid) != session["userid"]:
        return render_template("Profile.html", user=user, f=0, online="online", profile="active")
    else:
        return render_template("Profile.html", user=user, f=1, online="online", profile="active")
# プロフィール変更ページ
@app.route("/<int:userid>/update", methods=["GET", "POST"])
def update(userid):
    if "userid" not in session:
        return redirect(url_for("login", login="active"))
    elif int(userid) != session["userid"]:
        return redirect(url_for("profile", userid=session["userid"], online="online", profile="active"))
    else:
        user = query_db("user", "SELECT * FROM user WHERE id = ?", (userid,), True)
        if request.method == "POST":
            if "@" not in request.form.get("email"):
                return redirect(url_for("update", userid=session["userid"], online="online"))
                session["username"] = request.form.get("name")
            session["useremail"] = request.form.get("email")
            if user["password"] != request.form.get("password"):
                return redirect(url_for("update", userid=session["userid"], online="online"))
            modify_db("user", "UPDATE user \
                         SET name=?, email=?, password=? WHERE id=?",
                           (session['username'], session['useremail'],request.form.get("password"), session['userid']))
            return redirect(url_for('profile', userid=session["userid"], online="online", profile="active"))
        elif request.method == "GET":
            return render_template("Update.html", user=user, online="online")

# タイトル新規作成ページ
@app.route("/<int:userid>/newtitle", methods=["GET", "POST"])
def newtitle(userid):
    if "userid" not in session:
        return redirect(url_for("login", login="active"))
    else:
        if request.method == "GET":
            return render_template("newtitle.html", online="online", newtitle="active")
        if request.method == "POST":
            modify_db("title", "INSERT INTO title  (name, user_id) VALUES(?, ?)", (request.form.get("title"), session['userid']))
            return redirect(url_for("top"))
# タイトルページ
@app.route("/<int:title_id>/title", methods=["GET", "POST"])
def title(title_id):
    if "userid" in session:
        online = "online"
    if request.method == "GET":
        comments = query_db("comment", "SELECT * FROM comment WHERE title_id = ?", (title_id,))
        title = query_db("title", "SELECT * FROM title WHERE id = ?", (title_id,), True)
        return render_template("title.html",title=title, comments=comments, online=online)
    else:
        if "userid" not in session:
            return redirect(url_for("login", login="active"))
        else:
            modify_db("comment", "INSERT INTO comment (text_, user_id, title_id) VALUES(?, ?, ?)",
                    (request.form.get("comment"), session["userid"], title_id))
            return redirect(url_for("title", title_id=title_id, online=online))

# 検索ページ
@app.route("/search", methods=["GET", "POST"])
def search():
    if "userid" in session:
        online = "online"
    if request.method == "GET":
        return render_template("search.html", online=online, search="active")
    else:
        search = request.form.get("search")
        titles = query_db("title", "SELECT * FROM title WHERE name = ?", (search,), True)
        return redirect(url_for("top", titles=titles, search=search))

if __name__ == '__main__':
    app.secret_key = "jijjkla"
    app.run()
