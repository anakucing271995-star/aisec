import time
from alert_utils import load_alert_safe, sanitize_alert, file_hash
from prompt_manager import get_active_prompt, build_prompt
from llm_client import analyze
from telegram import send_to_telegram
from db import get_db

CHECK_INTERVAL = 5
last_hash = None

def save_history(prompt_id, alert_hash, final_prompt, response):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prompt_history
        (prompt_id, alert_hash, final_prompt, llm_response)
        VALUES (%s, %s, %s, %s)
    """, (prompt_id, alert_hash, final_prompt, response))
    conn.commit()
    cur.close()
    conn.close()

def main():
    global last_hash
    while True:
        alert = load_alert_safe()
        if alert:
            h = file_hash(alert)
            if h != last_hash:
                prompt = get_active_prompt()
                if prompt:
                    sanitized = sanitize_alert(alert, prompt.get("pii_masking", True))
                    user_prompt = build_prompt(prompt, sanitized)
                    result = analyze(prompt["system_prompt"], user_prompt)
                    save_history(prompt["id"], h, user_prompt, result)
                    send_to_telegram(result)
                    last_hash = h
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
