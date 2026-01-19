import re

def mask_ip(ip):
    if not ip or ip == "Unknown":
        return ip
    return re.sub(r'(\d+\.\d+)\.\d+\.\d+', r'\1.***.***', ip)

def mask_email(email):
    if "@" not in email:
        return email
    name, domain = email.split("@", 1)
    return name[:1] + "***@" + domain

def mask_pii_text(text, enabled=True):
    if not enabled or not text:
        return text
    text = re.sub(
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        lambda m: mask_email(m.group()),
        text
    )
    return text
