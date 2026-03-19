from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "CHANGE_THIS_SECRET"  # match your app.py

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["user_id"]
    except Exception:
        return None

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        user_id = decode_token(header.split(" ", 1)[1])
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        request.user_id = user_id
        return f(*args, **kwargs)

    return wrapper