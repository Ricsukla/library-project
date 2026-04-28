import mysql.connector
import sqlite3

# MYSQL
mysql_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="richa",
    database="library_db1",
    port=3307
)
mysql_cursor = mysql_db.cursor(dictionary=True)

# SQLITE
sqlite_db = sqlite3.connect("library.db")
cursor = sqlite_db.cursor()

# CREATE TABLES FIRST
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

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

# USERS
mysql_cursor.execute("SELECT * FROM users")
for u in mysql_cursor.fetchall():
    cursor.execute(
        "INSERT INTO users(name,email,password) VALUES (?,?,?)",
        (u["name"], u["email"], u["password"])
    )

print("Users migrated")

# BOOKS
mysql_cursor.execute("SELECT * FROM books")
for b in mysql_cursor.fetchall():
    cursor.execute("""
    INSERT INTO books(title,author,category,total_copies,available_copies)
    VALUES (?,?,?,?,?)
    """, (
        b["title"],
        b["author"],
        b["category"],
        b["total_copies"],
        b["available_copies"]
    ))

print("Books migrated")

# ISSUES
mysql_cursor.execute("SELECT * FROM issues")
for i in mysql_cursor.fetchall():
    cursor.execute("""
    INSERT INTO issues(student_id,book_id,student_name,book_title,issue_date,status)
    VALUES (?,?,?,?,?,?)
    """, (
        i["student_id"],
        i["book_id"],
        i["student_name"],
        i["book_title"],
        i["issue_date"],
        i["status"]
    ))

print("Issues migrated")

sqlite_db.commit()
print("✅ MIGRATION COMPLETE")