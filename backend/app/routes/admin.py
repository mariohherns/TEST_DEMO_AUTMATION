from fastapi import APIRouter, Depends
from ..deps import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/health")
def health(_: dict = Depends(require_admin)):
    return {"status": "ok"}
