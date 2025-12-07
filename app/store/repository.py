import json
import os
from datetime import datetime
from typing import List, Dict, Any

from app.config import settings


def ensure_dirs():
    os.makedirs(os.path.dirname(settings.DATA_FILE), exist_ok=True)


def load_all() -> List[Dict[str, Any]]:
    ensure_dirs()
    if not os.path.exists(settings.DATA_FILE):
        return []
    with open(settings.DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return data if isinstance(data, list) else []


def save_all(items: List[Dict[str, Any]]):
    ensure_dirs()
    with open(settings.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def stats() -> Dict[str, Any]:
    items = load_all()
    by_platform: Dict[str, int] = {}
    by_country: Dict[str, int] = {}
    for it in items:
        by_platform[it.get("platform", "Unknown")] = by_platform.get(it.get("platform", "Unknown"), 0) + 1
        by_country[it.get("country", "Unknown")] = by_country.get(it.get("country", "Unknown"), 0) + 1

    return {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "by_platform": by_platform,
        "by_country": by_country,
        "total": len(items),
    }
