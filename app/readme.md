# 🧩 Example: Adding a New Model (`Finding`) in FastAPI

This example shows how to add a SQLAlchemy model, Pydantic schemas, CRUD routes, Alembic migration steps, and unit tests (SQLite in-memory) that don’t touch Postgres/Redis.

---

## 1) Model

📂 `app/models/finding.py`
```python
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, DateTime, Integer
from ..models import Base  # your project's Base (already used by User, etc.)

class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="low")  # low|medium|high|critical
    description: Mapped[str] = mapped_column(Text, default="")
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Finding {self.id} {self.title} sev={self.severity}>"
```

---

## 2) Pydantic Schemas

📂 `app/schemas/finding.py`
```python
from datetime import datetime
from pydantic import BaseModel, Field, constr
from typing import Literal, Optional

Severity = Literal["low", "medium", "high", "critical"]

class FindingBase(BaseModel):
    title: constr(min_length=1, max_length=200)
    severity: Severity = "low"
    description: str = ""
    is_open: bool = True

class FindingCreate(FindingBase):
    pass

class FindingUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=200)] = None
    severity: Optional[Severity] = None
    description: Optional[str] = None
    is_open: Optional[bool] = None

class FindingRead(FindingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## 3) Routes (APIRouter)

📂 `app/routes/finding_routes.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from ..db import get_db
from ..models.finding import Finding
from ..schemas.finding import FindingCreate, FindingRead, FindingUpdate

router = APIRouter(prefix="/api/findings", tags=["Findings"])

@router.get("", response_model=List[FindingRead])
def list_findings(db: Session = Depends(get_db)):
    stmt = select(Finding).order_by(Finding.created_at.desc())
    return db.execute(stmt).scalars().all()

@router.post("", response_model=FindingRead, status_code=status.HTTP_201_CREATED)
def create_finding(payload: FindingCreate, db: Session = Depends(get_db)):
    obj = Finding(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{finding_id}", response_model=FindingRead)
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    obj = db.get(Finding, finding_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Finding not found")
    return obj

@router.patch("/{finding_id}", response_model=FindingRead)
def update_finding(finding_id: int, payload: FindingUpdate, db: Session = Depends(get_db)):
    obj = db.get(Finding, finding_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Finding not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_finding(finding_id: int, db: Session = Depends(get_db)):
    obj = db.get(Finding, finding_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Finding not found")
    db.delete(obj)
    db.commit()
```

---

## 4) Register the Router

📂 `app/main.py`
```python
from .routes.health import router as health_router

app.include_router(health_router)
```

---

## 5) Database Migrations (Alembic)

```bash
alembic revision --autogenerate -m "add findings table"
alembic upgrade head
```

Or inside Docker Compose:

```bash
docker compose exec web alembic revision --autogenerate -m "add findings table"
docker compose exec web alembic upgrade head
```

---

## 6) Unit Tests (SQLite in-memory)

📂 `app/tests/test_findings.py`
```python
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db
from app.models import Base
from app.models.finding import Finding

TEST_ENGINE = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False, future=True)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=TEST_ENGINE)

client = TestClient(app)

def test_create_and_get_finding():
    resp = client.post("/api/findings", json={
        "title": "Outdated dependency",
        "severity": "medium",
        "description": "Upgrade library X",
        "is_open": True
    })
    assert resp.status_code == 201
    created = resp.json()
    fid = created["id"]
    assert created["title"] == "Outdated dependency"
    assert created["severity"] == "medium"

    resp = client.get(f"/api/findings/{fid}")
    assert resp.status_code == 200

def test_patch_and_delete_finding():
    c = client.post("/api/findings", json={"title": "To fix", "severity": "low"})
    fid = c.json()["id"]
    u = client.patch(f"/api/findings/{fid}", json={"severity": "critical", "is_open": False})
    assert u.status_code == 200
    updated = u.json()
    assert updated["severity"] == "critical"

    d = client.delete(f"/api/findings/{fid}")
    assert d.status_code == 204
```
