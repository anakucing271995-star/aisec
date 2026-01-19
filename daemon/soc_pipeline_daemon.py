import json
import time
import hashlib
from alert_utils import load_alert_safe, sanitize_alert
from prompt_manager import get_active_prompt, build_prompt
from llm_client import analyze
from telegram import send_to_telegram
from db import get_db

ALERT_FILE = "../alert.json"
CHECK_INTERVAL = 2  # cek file setiap 2 detik
last_hashes = set()  # simpan hash tiap alert

def alert_hash(alert):
    """Hitung hash unik per alert"""
    return hashlib.md5(json.dumps(alert, sort_keys=True).encode()).hexdigest()

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

def process_alert(alert):
    """Proses satu alert baru"""
    h = alert_hash(alert)
    if h in last_hashes:
        return
    prompt = get_active_prompt()
    if not prompt:
        return
    sanitized = sanitize_alert(alert, prompt["pii_masking"])
    user_prompt = build_prompt(prompt, sanitized)
    result = analyze(prompt["system_prompt"], user_prompt)
    save_history(prompt["id"], h, user_prompt, result)
    send_to_telegram(result)
    last_hashes.add(h)
    print(f"[INFO] Processed alert: {alert['event']}")

def main():
    print("[INFO] SOC Daemon started, watching alerts...")
    while True:
        alerts = load_alert_safe()
        for alert in alerts:
            process_alert(alert)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
