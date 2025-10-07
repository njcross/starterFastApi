# app/routes/protected.py
from fastapi import APIRouter, Depends, status
from ..auth.session import require_auth
from ..schemas.protected import WhoAmIResponse
from ..schemas.auth import ErrorResponse  # or from ..schemas.health import ErrorResponse

router = APIRouter(prefix="/api/protected", tags=["Protected"])

# instantiate once so Depends doesn't create a new closure each time
RequireAuth = require_auth()

@router.get(
    "/whoami",
    summary="Example protected endpoint",
    response_model=WhoAmIResponse,
    responses={
        200: {"model": WhoAmIResponse, "description": "Authenticated user id"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
def whoami(user_id: int = Depends(RequireAuth)) -> WhoAmIResponse:
    return WhoAmIResponse(user_id=user_id)
