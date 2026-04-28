from flask_cors import CORS
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
CORS(app)


# ---------------- DATABASE ----------------

DB_PATH = os.path.join(os.getcwd(), "library.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Books Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        category TEXT,
        total_copies INTEGER,
        available_copies INTEGER
    )
    """)

    # Issues Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        book_id INTEGER,
        student_name TEXT,
        book_title TEXT,
        issue_date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()


# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    d = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, name FROM users WHERE email=? AND password=?",
        (d['email'], d['password'])
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "message": "success",
            "user": {
                "user_id": user["user_id"],
                "name": user["name"]
            }
        }

    return {"message": "fail"}


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['POST'])
def signup():
    d = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (d['email'],)
    )

    if cursor.fetchone():
        conn.close()
        return {"message": "exists"}

    cursor.execute(
        "INSERT INTO users(name,email,password) VALUES (?,?,?)",
        (d['name'], d['email'], d['password'])
    )

    conn.commit()
    conn.close()

    return {"message": "created"}


# ---------------- BOOKS ----------------
@app.route('/books')
def books():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT book_id,title,author,category AS genre
    FROM books LIMIT 50
    """)

    data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(data)


# ---------------- ADD BOOK ----------------
@app.route('/add_book', methods=['POST'])
def add_book():
    d = request.json
    conn = get_db()
    cursor = conn.cursor()

    copies = int(d.get('copies', 1))

    cursor.execute("""
    INSERT INTO books(title,author,category,total_copies,available_copies)
    VALUES (?,?,?,?,?)
    """, (
        d['title'],
        d['author'],
        d['genre'],
        copies,
        copies
    ))

    conn.commit()
    conn.close()

    return {"message": "Book added successfully"}


# ---------------- DELETE BOOK ----------------
@app.route('/delete_book/<int:id>', methods=['DELETE'])
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM books WHERE book_id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return {"message": "deleted"}


# ---------------- SEARCH ----------------
@app.route('/search/<name>')
def search(name):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT book_id,title,author,category AS genre
    FROM books
    WHERE title LIKE ?
    """, ('%' + name + '%',))

    data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(data)


# ---------------- ISSUE BOOK ----------------
@app.route('/issue', methods=['POST'])
def issue():
    d = request.json
    conn = get_db()
    cursor = conn.cursor()

    try:
        user_id = int(d['user_id'])
        book_id = int(d['book_id'])

        cursor.execute(
            "SELECT title, available_copies FROM books WHERE book_id=?",
            (book_id,)
        )

        book = cursor.fetchone()

        if not book:
            conn.close()
            return {"message": "Book not found"}

        if book["available_copies"] <= 0:
            conn.close()
            return {"message": "No copies available"}

        cursor.execute(
            "SELECT name FROM users WHERE user_id=?",
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            conn.close()
            return {"message": "User not found"}

        cursor.execute("""
        INSERT INTO issues
        (student_id, book_id, student_name, book_title, issue_date, status)
        VALUES (?, ?, ?, ?, DATE('now'), 'issued')
        """, (
            user_id,
            book_id,
            user["name"],
            book["title"]
        ))

        cursor.execute("""
        UPDATE books
        SET available_copies = available_copies - 1
        WHERE book_id=?
        """, (book_id,))

        conn.commit()
        conn.close()

        return {"message": "Book issued successfully"}

    except Exception as e:
        print("ISSUE ERROR:", e)
        conn.close()
        return {"message": "Issue failed"}


# ---------------- ISSUED LIST ----------------
@app.route('/issued')
def issued():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT issue_id,
           student_name AS name,
           book_title AS title
    FROM issues
    """)

    data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(data)


# ---------------- RETURN BOOK ----------------
@app.route('/return/<int:id>', methods=['PUT'])
def ret(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT book_id FROM issues WHERE issue_id=?",
        (id,)
    )

    book = cursor.fetchone()

    if book:
        cursor.execute(
            "DELETE FROM issues WHERE issue_id=?",
            (id,)
        )

        cursor.execute("""
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE book_id=?
        """, (book["book_id"],))

        conn.commit()

    conn.close()

    return {"message": "returned"}
@app.route("/check")
def check():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    return str(cursor.fetchone())


import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
