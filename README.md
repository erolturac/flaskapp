# Flask + MySQL Registration & Login Demo

A minimal, production-lean Flask web app with user registration and login,
backed by MySQL. Passwords are hashed with Werkzeug's `generate_password_hash`
(PBKDF2) — never stored in plaintext.

## Project structure

```
flaskapp/
├── app.py              # Routes: /, /register, /login, /logout, /dashboard
├── config.py           # App + MySQL config (reads from env vars)
├── schema.sql           # MySQL table creation script
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   └── dashboard.html
└── static/
    └── style.css
```

## 1. Set up MySQL

Make sure a MySQL server is running, then create the database and table:

```bash
mysql -u root -p < schema.sql
```

This creates a `flask_auth_demo` database with a `users` table
(`id`, `username`, `email`, `password_hash`, `created_at`).

## 2. Install dependencies

It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configure environment variables

The app reads its config from environment variables (see `config.py` for
defaults). Set at minimum:

```bash
export SECRET_KEY="a-long-random-string"
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your-mysql-password
export MYSQL_DB=flask_auth_demo
```

(On Windows, use `set VAR=value` in cmd or `$env:VAR="value"` in PowerShell.)

## 4. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser. From the home page you can
register a new account and then log in.

## Notes / production considerations

- `app.run(debug=True)` is for local development only — disable debug mode
  and use a production WSGI server (e.g. gunicorn) in production.
- Set `SESSION_COOKIE_SECURE=True` (env var) once you're serving over HTTPS.
- Consider adding rate limiting on `/login` to slow down brute-force attempts.
- Consider adding email verification and password-reset flows for a real
  production app.
- This demo uses a fresh MySQL connection per request for simplicity; for
  higher traffic, switch to a connection pool
  (`mysql.connector.pooling.MySQLConnectionPool`).
