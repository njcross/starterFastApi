# app/routes/utils.py
from flask import request, jsonify
from functools import wraps

def json_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "content-type must be application/json"}), 415
        return fn(*args, **kwargs)
    return wrapper
