@app.route("/")
@login_required
def index():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Ambil semua prompts
    cur.execute("SELECT * FROM prompts")
    prompts = cur.fetchall()

    # Ambil alert terakhir dari alert.json
    raw_alert = load_alert_safe()
    # Ambil prompt aktif untuk menentukan apakah PII masking aktif
    active_prompt = get_active_prompt()
    latest_alert = sanitize_alert(raw_alert, pii_enabled=active_prompt["pii_masking"]) if raw_alert else None

    # Ambil LLM response terakhir
    cur.execute("""
        SELECT h.*, p.name AS prompt_name
        FROM prompt_history h
        JOIN prompts p ON h.prompt_id=p.id
        ORDER BY h.created_at DESC
        LIMIT 1
    """)
    latest_history = cur.fetchone()

    return render_template(
        "index.html",
        prompts=prompts,
        latest_alert=latest_alert,
        latest_history=latest_history
    )
