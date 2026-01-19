import json
import os
import hashlib
from .pii_masking import mask_ip, mask_pii_text

ALERT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alert.json"))

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_alert_safe():
    if not os.path.exists(ALERT_FILE):
        return None
    try:
        with open(ALERT_FILE) as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data[-1]  # Ambil alert terbaru
            return None
    except json.JSONDecodeError:
        return None

def sanitize_alert(alert, pii_enabled=True):
    if not alert:
        return None
    return {
        "siem": alert.get("siem", "Unknown"),
        "severity": alert.get("severity", "Unknown"),
        "event": mask_pii_text(alert.get("event"), pii_enabled),
        "source_ip": mask_ip(alert.get("source_ip")),
        "destination": alert.get("destination", "Unknown")
    }
