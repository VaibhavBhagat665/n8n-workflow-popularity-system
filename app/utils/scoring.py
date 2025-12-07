from __future__ import annotations
from typing import Dict, Any


def safe_div(n: float, d: float) -> float:
    return (n / d) if d else 0.0

def compute_youtube_ratios(metrics: Dict[str, Any]) -> Dict[str, Any]:
    views = float(metrics.get("views", 0))
    likes = float(metrics.get("likes", 0))
    comments = float(metrics.get("comments", 0))
    metrics["like_to_view_ratio"] = round(safe_div(likes, views), 6)
    metrics["comment_to_view_ratio"] = round(safe_div(comments, views), 6)
    return metrics


def compute_forum_ratios(metrics: Dict[str, Any]) -> Dict[str, Any]:
    views = float(metrics.get("views", 0))
    replies = float(metrics.get("replies", 0))
    likes = float(metrics.get("likes", 0))
    metrics["reply_to_view_ratio"] = round(safe_div(replies, views), 6)
    metrics["like_to_view_ratio"] = round(safe_div(likes, views), 6)
    return metrics


def youtube_score(metrics: Dict[str, Any]) -> float:
    views = float(metrics.get("views", 0))
    likes = float(metrics.get("likes", 0))
    comments = float(metrics.get("comments", 0))
    lvr = float(metrics.get("like_to_view_ratio", 0))

    # Heuristic normalization caps for POC
    v = min(1.0, views / 200_000)
    l = min(1.0, likes / 5_000)
    c = min(1.0, comments / 1_000)

    # Weighted sum, keep in [0,1]
    score = 0.45 * v + 0.3 * l + 0.15 * c + 0.10 * min(1.0, lvr * 50)
    return round(min(1.0, score), 6)


def forum_score(metrics: Dict[str, Any]) -> float:
    views = float(metrics.get("views", 0))
    replies = float(metrics.get("replies", 0))
    likes = float(metrics.get("likes", 0))
    contributors = float(metrics.get("contributors", 0))

    v = min(1.0, views / 20_000)
    r = min(1.0, replies / 200)
    l = min(1.0, likes / 300)
    u = min(1.0, contributors / 60)

    score = 0.4 * v + 0.3 * r + 0.2 * l + 0.1 * u
    return round(min(1.0, score), 6)


def trends_score(metrics: Dict[str, Any]) -> float:
    msv = float(metrics.get("monthly_search_volume", 0))
    change = float(metrics.get("trend_30d_change", 0))  # fraction, e.g. 0.25 for +25%
    interest = float(metrics.get("interest_score", 0))  # 0-100

    v = min(1.0, msv / 100_000)
    t = max(0.0, min(1.0, (change + 0.5)))  # shift to keep [-0.5, +0.5] in [0,1]
    i = min(1.0, interest / 100.0)

    score = 0.5 * v + 0.3 * i + 0.2 * t
    return round(min(1.0, score), 6)


def compute_popularity(platform: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    if platform == "YouTube":
        metrics = compute_youtube_ratios(metrics)
        score = youtube_score(metrics)
    elif platform == "Forum":
        metrics = compute_forum_ratios(metrics)
        score = forum_score(metrics)
    else:  # Google
        score = trends_score(metrics)
    return metrics, score
