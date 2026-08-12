"""
Flask web application with user registration and login.
Backend: MySQL (via mysql-connector-python)
Passwords are hashed with Werkzeug's security helpers (never store plaintext).
"""

import re
from functools import wraps

import mysql.connector
from mysql.connector import Error as MySQLError
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)


# --------------------------------------------------------------------------
# Database helper
# --------------------------------------------------------------------------
def get_db_connection():
    """Open a new MySQL connection using settings from config.py."""
    return mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        port=app.config["MYSQL_PORT"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"],
    )


# --------------------------------------------------------------------------
# Auth helpers
# --------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def login_required(view_func):
    """Decorator: redirect to login page if user is not authenticated."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    """Main/landing page."""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # ---- Validation ----
    errors = []
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters long.")
    if not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if password != confirm_password:
        errors.append("Passwords do not match.")

    if errors:
        for e in errors:
            flash(e, "danger")
        return render_template("register.html", username=username, email=email)

    hashed_password = generate_password_hash(password)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for existing username/email
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cursor.fetchone():
            flash("Username or email is already registered.", "danger")
            return render_template("register.html", username=username, email=email)

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed_password),
        )
        conn.commit()
        cursor.close()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    except MySQLError as err:
        app.logger.error(f"Database error during registration: {err}")
        flash("A server error occurred. Please try again later.", "danger")
        return render_template("register.html", username=username, email=email)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    identifier = request.form.get("identifier", "").strip()  # username or email
    password = request.form.get("password", "")

    if not identifier or not password:
        flash("Please enter both username/email and password.", "danger")
        return render_template("login.html")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users "
            "WHERE username = %s OR email = %s",
            (identifier, identifier.lower()),
        )
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username/email or password.", "danger")
        return render_template("login.html")

    except MySQLError as err:
        app.logger.error(f"Database error during login: {err}")
        flash("A server error occurred. Please try again later.", "danger")
        return render_template("login.html")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


if __name__ == "__main__":
    app.run(debug=True)
