from flask import session, redirect
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def lead_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "lead":
            return "Access denied", 403
        return f(*args, **kwargs)
    return wrapper
