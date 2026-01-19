from db import get_db

def get_active_prompt():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM prompts WHERE is_active=1 LIMIT 1")
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def build_prompt(prompt_data, alert):
    user_prompt = prompt_data["user_prompt_template"].format(
        siem=alert["siem"],
        severity=alert["severity"],
        event=alert["event"],
        source_ip=alert["source_ip"],
        destination=alert["destination"]
    )
    return user_prompt
