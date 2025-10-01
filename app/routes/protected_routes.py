# app/routes/protected_routes.py
from flask import Blueprint, jsonify, g
from ..auth.session import login_required

bp = Blueprint("protected", __name__, url_prefix="/api/protected")

@bp.get("/whoami")
@login_required
def whoami():
    return jsonify({"user_id": g.user_id})
