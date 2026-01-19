from flask import Flask, render_template, request, redirect, session
from auth import login_required, lead_required
from daemon.alert_utils import load_alert_safe, sanitize_alert
from daemon.prompt_manager import get_active_prompt
from daemon.db import get_db
import hashlib
import os

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
@login_required
def index():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM prompts")
    prompts = cur.fetchall()
    alert_data = load_alert_safe()
    alert_display = sanitize_alert(alert_data) if alert_data else None
    return render_template("index.html", prompts=prompts, alert=alert_display)

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
            request.form["user_prompt"],
            int("pii_masking" in request.form),
            id
        ))
        conn.commit()
        return redirect("/")
    cur.execute("SELECT * FROM prompts WHERE id=%s", (id,))
    prompt = cur.fetchone()
    return render_template("edit_prompt.html", prompt=prompt)

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
    return render_template("history.html", history=history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
