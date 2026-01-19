import json
import os
import hashlib
from pii_masking import mask_ip, mask_pii_text

ALERT_FILE = "../alert.json"  # sesuaikan path relatif daemon ke alert.json

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_alert_safe():
    if not os.path.exists(ALERT_FILE):
        return []
    try:
        with open(ALERT_FILE) as f:
            data = json.load(f)
            # pastikan selalu list
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        return []

def sanitize_alert(alert, pii_enabled=True):
    return {
        "siem": alert.get("siem", "Unknown"),
        "severity": alert.get("severity", "Unknown"),
        "event": mask_pii_text(alert.get("event"), pii_enabled),
        "source_ip": mask_ip(alert.get("source_ip")),
        "destination": alert.get("destination", "Unknown")
    }
