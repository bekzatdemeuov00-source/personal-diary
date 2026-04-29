from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"
DB = "diary.db"


def db():
    return sqlite3.connect(DB)


def init():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        password TEXT,
        is_private INTEGER DEFAULT 0,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init()


@app.route("/")
def index():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes ORDER BY created DESC")
    notes = cur.fetchall()
    conn.close()
    return render_template("index.html", notes=notes)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        is_private = 1 if request.form.get("is_private") else 0
        password = request.form.get("password", "")

        conn = db()
        conn.execute(
            "INSERT INTO notes(title,content,password,is_private) VALUES(?,?,?,?)",
            (title, content, password, is_private)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


@app.route("/view/<int:id>", methods=["GET", "POST"])
def view(id):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM notes WHERE id=?", (id,))
    note = cur.fetchone()

    conn.close()

    # если приватная
    if note[4] == 1:
        if request.method == "POST":
            if request.form["password"] == note[3]:
                return render_template("view.html", note=note)

        return render_template("password.html", id=id)

    return render_template("view.html", note=note)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM notes WHERE id=?", (id,))
    note = cur.fetchone()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cur.execute(
            "UPDATE notes SET title=?, content=? WHERE id=?",
            (title, content, id)
        )

        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("edit.html", note=note)


@app.route("/delete/<int:id>")
def delete(id):
    conn = db()
    conn.execute("DELETE FROM notes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)