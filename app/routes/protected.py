# app/routes/protected.py
from fastapi import APIRouter, Depends
from ..auth.session import require_auth

router = APIRouter(prefix="/api/protected", tags=["Protected"])

@router.get("/whoami", summary="Example protected endpoint")
def whoami(user_id: int = Depends(require_auth())):
    return {"user_id": user_id}