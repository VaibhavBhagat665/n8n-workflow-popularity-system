from fastapi import APIRouter

from app.services.ingestion import collect_all
from app.store.repository import save_all

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/refresh")
def refresh_data():
    items = collect_all()
    save_all(items)
    return {"status": "ok", "count": len(items)}
