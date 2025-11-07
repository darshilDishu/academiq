# server.py
from flask import Flask, render_template, request, redirect, session, url_for, g
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "academiq_secret")

# Database connection helper
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "academiq"),
        port=int(os.getenv("DB_PORT", 3306)),
        autocommit=False
    )
    return conn

# --- Helper: require login decorator (simple) ---
def require_login():
    if "student_id" not in session:
        return False
    return True

# --- ROUTES ---

# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE email=%s", (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user and user.get("password"):
            stored_hash = user["password"].encode()
            if bcrypt.checkpw(password.encode(), stored_hash):
                session["student_id"] = user["id"]
                return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        semester = request.form.get("semester", "").strip()
        course = request.form.get("course", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Basic validation
        if not (name and email and password):
            return render_template("register.html", error="Name, email and password required")

        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (name, roll_no, semester, course, email, password) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, roll_no, semester, course, email, hashed)
            )
            conn.commit()
        except mysql.connector.Error as e:
            conn.rollback()
            return render_template("register.html", error=f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("login"))
    return render_template("register.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))

    student_id = session["student_id"]
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
        student = cursor.fetchone()

        cursor.execute("SELECT * FROM attendance WHERE student_id=%s", (student_id,))
        attendance = cursor.fetchall()

        cursor.execute("SELECT * FROM tasks WHERE student_id=%s", (student_id,))
        tasks = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("dashboard.html", student=student, attendance=attendance, tasks=tasks)

# Attendance add
@app.route("/attendance", methods=["POST"])
def attendance():
    if not require_login():
        return redirect(url_for("login"))

    subject = request.form.get("subject", "").strip()
    try:
        total = int(request.form.get("total", 0))
        attended = int(request.form.get("attended", 0))
    except ValueError:
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (student_id, subject, total_lectures, attended_lectures) VALUES (%s,%s,%s,%s)",
            (session["student_id"], subject, total, attended)
        )
        conn.commit()
    except mysql.connector.Error:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard"))

# Library (view & add)
@app.route("/library", methods=["GET", "POST"])
def library():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == "POST":
            book = request.form.get("book_name", "").strip()
            author = request.form.get("author", "").strip()
            subject = request.form.get("subject", "").strip()
            cursor.execute(
                "INSERT INTO library (student_id, book_name, author, subject, status) VALUES (%s,%s,%s,%s,%s)",
                (session["student_id"], book, author, subject, 'available')
            )
            conn.commit()

        cursor.execute("SELECT * FROM library WHERE student_id=%s", (session["student_id"],))
        books = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("library.html", books=books)

# Borrow book
@app.route("/borrow/<int:book_id>")
def borrow(book_id):
    if not require_login():
        return redirect(url_for("login"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE library SET status='borrowed' WHERE id=%s", (book_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("library"))

# Return book
@app.route("/return/<int:book_id>")
def return_book(book_id):
    if not require_login():
        return redirect(url_for("login"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE library SET status='available' WHERE id=%s", (book_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("library"))

# Collaboration (text)
@app.route("/collab", methods=["GET", "POST"])
def collab():
    if not require_login():
        return redirect(url_for("login"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == "POST":
            message = request.form.get("message", "").strip()
            cursor.execute("INSERT INTO collaboration (student_id, content) VALUES (%s, %s)",
                           (session["student_id"], message))
            conn.commit()

        cursor.execute("""
            SELECT c.content, s.name, c.created_at
            FROM collaboration c
            JOIN students s ON c.student_id = s.id
            ORDER BY c.created_at DESC
        """)
        messages = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("collab.html", messages=messages)

# Tasks
@app.route("/add_task", methods=["POST"])
def add_task():
    if not require_login():
        return redirect(url_for("login"))
    task = request.form.get("task_name", "").strip()
    if not task:
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (student_id, task_name) VALUES (%s,%s)",
                       (session["student_id"], task))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("dashboard"))

@app.route("/complete_task/<int:task_id>")
def complete_task(task_id):
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status='done' WHERE id=%s", (task_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("dashboard"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Simple health check
@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    # When running in Docker we want to listen on all interfaces
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
