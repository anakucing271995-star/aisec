from flask import Flask, render_template, request, redirect, session
from db import get_db
from auth import login_required, lead_required
import hashlib
import os
from alert_utils import load_alert_safe, sanitize_alert
from prompt_manager import get_active_prompt, build_prompt

# -----------------------------
# Inisialisasi Flask
# -----------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "dev_secret_key"


# -----------------------------
# LOGIN ROUTE
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password_hash = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password_hash=%s",
            (username, password_hash)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/")
        return "Login failed. Periksa username/password Anda."

    return render_template("login.html")


# -----------------------------
# DASHBOARD ROUTE
# -----------------------------
@app.route("/")
@login_required
def index():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM prompts")
    prompts = cur.fetchall()

    # Load latest alert
    alert_data = load_alert_safe()
    alert_display = sanitize_alert(alert_data) if alert_data else None

    cur.close()
    conn.close()
    return render_template("index.html", prompts=prompts, alert=alert_display)


# -----------------------------
# EDIT PROMPT ROUTE (LEAD ONLY)
# -----------------------------
@app.route("/prompt/edit/<int:id>", methods=["GET", "POST"])
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
            request.form["user_prompt"],
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


# -----------------------------
# HISTORY ROUTE
# -----------------------------
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


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    # Debug True untuk melihat error saat develop
    app.run(host="0.0.0.0", port=5000, debug=True)
