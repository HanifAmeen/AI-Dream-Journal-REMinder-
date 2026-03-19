from flask import request, jsonify
from functools import wraps
from app import decode_token  # keep this

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
