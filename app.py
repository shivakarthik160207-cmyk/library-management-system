import os
print("Current folder:", os.getcwd())

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "library_secret_key"

def init_db():
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    username TEXT
)
""")
    
    
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username, password)
            )
            conn.commit()
        except:
            conn.close()
            return "Username already exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )

@app.route("/add_book", methods=["POST"])
def add_book():
    if "user" not in session:
        return redirect("/login")

    title = request.form["title"]

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    username = session["user"]

    cur.execute(
        "INSERT INTO books(title, username) VALUES (?, ?)",
        (title, username)
    )

    conn.commit()
    conn.close()

    return redirect("/books")

@app.route("/books")
def books():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute(
       "SELECT * FROM books WHERE username=?",
       (session["user"],)
   )
    
    all_books = cur.fetchall()

    conn.close()

    return render_template(
        "books.html",
        books=all_books
    )

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/delete_book/<int:id>")
def delete_book(id):

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM books WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/books")

@app.route("/search")
def search():
    if "user" not in session:
        return redirect("/login")
    
    q = request.args.get("q")

    conn = sqlite3.connect("library.db")
    print("Database connection opened")
    cur = conn.cursor()

    cur.execute(
       "SELECT * FROM books WHERE username=? AND title LIKE ?",
        (session["user"], "%" + q + "%")
    )


    books = cur.fetchall()
    conn.close()

    return render_template("books.html", books=books)

@app.route("/edit_book/<int:id>", methods=["GET", "POST"])
def edit_book(id):

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]

        cur.execute(
            "UPDATE books SET title=? WHERE id=?",
            (title, id)
        )

        conn.commit()
        conn.close()

        return redirect("/books")

    cur.execute(
        "SELECT * FROM books WHERE id=?",
        (id,)
    )

    book = cur.fetchone()

    conn.close()

    return render_template(
        "edit_book.html",
        book=book
    )

if __name__ == "__main__":
    app.run(debug=True)