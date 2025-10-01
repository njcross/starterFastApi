Example of a New Model
1) Model

📂 app/models/finding.py

from datetime import datetime
from ..extensions import db

class Finding(db.Model):
    __tablename__ = "findings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, default="low")  # low|medium|high|critical
    description = db.Column(db.Text, default="")
    is_open = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Finding {self.id} {self.title} sev={self.severity}>"

2) Schema

📂 app/schemas/finding.py

from marshmallow import validate, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from ..extensions import db
from ..models.finding import Finding

class FindingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Finding
        sqla_session = db.session
        load_instance = True
        unknown = EXCLUDE

    id = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    title = auto_field(required=True, validate=validate.Length(min=1, max=200))
    severity = auto_field(validate=validate.OneOf(["low", "medium", "high", "critical"]))

3) Routes (Blueprint)

📂 app/routes/finding_routes.py

from flask import Blueprint, request, jsonify, abort
from sqlalchemy import select
from ..extensions import db
from ..models.finding import Finding
from ..schemas.finding import FindingSchema

bp = Blueprint("findings", __name__, url_prefix="/api/findings")

schema = FindingSchema()
schemas = FindingSchema(many=True)

@bp.get("")
def list_findings():
    stmt = select(Finding).order_by(Finding.created_at.desc())
    objs = db.session.execute(stmt).scalars().all()
    return jsonify(schemas.dump(objs)), 200

@bp.post("")
def create_finding():
    data = request.get_json() or {}
    obj = schema.load(data)
    db.session.add(obj)
    db.session.commit()
    return schema.jsonify(obj), 201

@bp.get("/<int:finding_id>")
def get_finding(finding_id):
    obj = db.session.get(Finding, finding_id)
    if not obj:
        abort(404, "Finding not found")
    return schema.jsonify(obj), 200

@bp.patch("/<int:finding_id>")
def update_finding(finding_id):
    obj = db.session.get(Finding, finding_id)
    if not obj:
        abort(404, "Finding not found")
    data = request.get_json() or {}
    obj = schema.load(data, instance=obj, partial=True)
    db.session.commit()
    return schema.jsonify(obj), 200

@bp.delete("/<int:finding_id>")
def delete_finding(finding_id):
    obj = db.session.get(Finding, finding_id)
    if not obj:
        abort(404, "Finding not found")
    db.session.delete(obj)
    db.session.commit()
    return "", 204

4) Register in Routes

📂 app/routes/__init__.py

from flask import Flask
from .finding_routes import bp as findings_bp

def register_routes(app: Flask):
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    app.register_blueprint(findings_bp)

5) Database Migrations

With Flask-Migrate and Alembic set up, here’s how you run migrations:

Local venv (no Docker)
# ensure env var if using app factory
export FLASK_APP="app:create_app"          # Bash
# PowerShell:
# $env:FLASK_APP="app:create_app"

flask db init                              # run once to create migrations/
flask db migrate -m "create findings"
flask db upgrade

Inside Docker Compose

Since you’re using wsgi.py as your entrypoint:

docker compose exec web flask --app wsgi db init       # run once
docker compose exec web flask --app wsgi db migrate -m "create findings"
docker compose exec web flask --app wsgi db upgrade


⚠️ If you see No changes in schema detected, double-check you’ve imported your model in app/models/__init__.py and that app/__init__.py calls from . import models.

6) Unit tests (SQLite in-memory; super fast)

These tests run without Postgres, so they won’t touch your local DB. They create a fresh schema in memory.

app/tests/conftest.py

import os
import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope="session")
def app():
    # Use in-memory SQLite for unit tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()

    with app.app_context():
        _db.create_all()
    yield app

    # (no teardown needed for sqlite:///:memory: with session scope)

@pytest.fixture()
def client(app):
    return app.test_client()


app/tests/test_findings.py

def test_create_and_get_finding(client):
    # create
    resp = client.post("/api/findings", json={
        "title": "Outdated dependency",
        "severity": "medium",
        "description": "Upgrade library X",
        "is_open": True
    })
    assert resp.status_code == 201, resp.get_data(as_text=True)
    created = resp.get_json()
    fid = created["id"]
    assert created["title"] == "Outdated dependency"
    assert created["severity"] == "medium"
    assert created["is_open"] is True

    # read
    resp = client.get(f"/api/findings/{fid}")
    assert resp.status_code == 200
    got = resp.get_json()
    assert got["id"] == fid

def test_list_findings_and_filter(client):
    # ensure at least one exists
    client.post("/api/findings", json={"title": "A", "severity": "low"})
    client.post("/api/findings", json={"title": "B", "severity": "high"})
    resp = client.get("/api/findings?severity=high&per_page=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert data["per_page"] == 1
    assert all(item["severity"] == "high" for item in data["items"])

def test_patch_and_delete_finding(client):
    # create
    c = client.post("/api/findings", json={"title": "To fix", "severity": "low"})
    fid = c.get_json()["id"]

    # patch
    u = client.patch(f"/api/findings/{fid}", json={"severity": "critical", "is_open": False})
    assert u.status_code == 200
    updated = u.get_json()
    assert updated["severity"] == "critical"
    assert updated["is_open"] is False

    # delete
    d = client.delete(f"/api/findings/{fid}")
    assert d.status_code == 204

    # gone
    g = client.get(f"/api/findings/{fid}")
    assert g.status_code == 404


These count as unit tests (using SQLite). Your integration tests can hit the real Postgres/Redis and be marked with @pytest.mark.integration if you want to keep them out of the default run.