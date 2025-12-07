from typing import List, Optional
from fastapi import APIRouter, Query

from app.store import repository

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/")
def list_workflows(
    platform: Optional[str] = Query(None, description="Filter by platform: YouTube, Forum, Google"),
    country: Optional[str] = Query(None, description="Filter by country: US, IN"),
    sort_by: Optional[str] = Query("popularity_score", description="Field to sort by"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = repository.load_all()

    if platform:
        items = [i for i in items if i.get("platform") == platform]
    if country:
        items = [i for i in items if i.get("country") == country]

    reverse = (order or "desc").lower() == "desc"
    try:
        items.sort(key=lambda x: x.get(sort_by, 0) if sort_by != "popularity_score" else float(x.get("popularity_score", 0)), reverse=reverse)
    except Exception:
        # Fallback to popularity_score if invalid sort field
        items.sort(key=lambda x: float(x.get("popularity_score", 0)), reverse=True)

    total = len(items)
    sliced = items[offset : offset + limit]
    return {"total": total, "items": sliced, "limit": limit, "offset": offset}
