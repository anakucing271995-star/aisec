import sys
import os
from flask import Flask, render_template, request, redirect, session

# tambah root project ke sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from daemon.alert_utils import load_alert_safe, sanitize_alert
from daemon.prompt_manager import get_active_prompt
from db import get_db
from auth import login_required, lead_required
import hashlib

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password_hash=%s", (user, pwd))
        u = cur.fetchone()
        if u:
            session["user"] = u["username"]
            session["role"] = u["role"]
            return redirect("/")
        return "Login failed"
    return render_template("login.html")

@app.route("/")
@login_required
def index():
    prompts = []
    alert_display = None

    # Ambil semua prompts
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM prompts")
    prompts = cur.fetchall()
    cur.close()
    conn.close()

    # Ambil alert terakhir
    alert_data = load_alert_safe()
    alert_display = sanitize_alert(alert_data) if alert_data else None

    return render_template("index.html", prompts=prompts, alert=alert_display)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
