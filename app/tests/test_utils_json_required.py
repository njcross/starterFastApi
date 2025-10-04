import pytest
from flask import Flask, jsonify, request
from app.routes.utils import json_required

@pytest.fixture()
def app():
    """Create a minimal Flask app for testing the decorator."""
    app = Flask(__name__)

    @app.route("/echo", methods=["POST"])
    @json_required
    def echo():
        data = request.get_json()
        return jsonify({"ok": True, "data": data})

    return app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_json_required_rejects_non_json(client):
    """Should return 415 when content-type is not application/json."""
    resp = client.post("/echo", data="plain text", content_type="text/plain")
    assert resp.status_code == 415
    assert resp.json == {"error": "content-type must be application/json"}

def test_json_required_accepts_json(client):
    """Should pass through and return JSON response when request is valid JSON."""
    payload = {"msg": "hi"}
    resp = client.post("/echo", json=payload)
    assert resp.status_code == 200
    assert resp.json == {"ok": True, "data": payload}
