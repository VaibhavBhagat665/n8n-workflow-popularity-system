from fastapi import APIRouter

from app.store import repository

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
def get_stats():
    return repository.stats()
