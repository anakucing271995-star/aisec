import sys
import os
import hashlib
from flask import Flask, render_template, request, redirect, session

# --- Tambahkan parent folder ke sys.path agar bisa import daemon/ dan prompt_manager.py ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from daemon.alert_utils import load_alert_safe, sanitize_alert
from prompt_manager import get_active_prompt
from db import get_db
from auth import login_required, lead_required

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # fallback jika .env kosong

# ==========================
# LOGIN ROUTE
# ==========================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password_hash = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username=%s AND password_hash=%s", 
                    (username, password_hash))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/")
        return "Login failed"
    return render_template("login.html")

# ==========================
# INDEX ROUTE
# ==========================
@app.route("/")
@login_required
def index():
    # Load active prompt
    active_prompt = get_active_prompt()

    # Load latest alert
    alert_data = load_alert_safe()
    alert_display = None
    if alert_data:
        # alert.json sekarang berbentuk list
        if isinstance(alert_data, list):
            last_alert = alert_data[-1]  # ambil alert terakhir
            alert_display = sanitize_alert(last_alert, pii_enabled=active_prompt["pii_masking"] if active_prompt else True)
        elif isinstance(alert_data, dict):
            alert_display = sanitize_alert(alert_data, pii_enabled=active_prompt["pii_masking"] if active_prompt else True)

    # Load all prompts
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM prompts")
    prompts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", prompts=prompts, alert=alert_display, active_prompt=active_prompt)

# ==========================
# EDIT PROMPT
# ==========================
@app.route("/prompt/edit/<int:id>", methods=["GET","POST"])
@lead_required
def edit_prompt(id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        cur.execute("""
            UPDATE prompts
            SET system_prompt=%s,
                user_prompt_template=%s,
                version=version+1,
                pii_masking=%s
            WHERE id=%s
        """, (
            request.form["system_prompt"],
            request.form["user_prompt_template"],
            int("pii_masking" in request.form),
            id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/")

    cur.execute("SELECT * FROM prompts WHERE id=%s", (id,))
    prompt = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_prompt.html", prompt=prompt)

# ==========================
# PROMPT HISTORY
# ==========================
@app.route("/history")
@login_required
def history():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT h.*, p.name AS prompt_name
        FROM prompt_history h
        JOIN prompts p ON h.prompt_id=p.id
        ORDER BY h.created_at DESC
        LIMIT 100
    """)
    history = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("history.html", history=history)

# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
