from __future__ import annotations
import time
from typing import Dict, List, Any

import requests

from app.config import settings
from app.utils.scoring import compute_popularity


PLATFORMS = ("YouTube", "Forum", "Google")
COUNTRIES = ("US", "IN")



# --- Real API calls (best-effort, optional for POC) ---

def fetch_youtube(country: str, query: str = "n8n workflow", max_results: int = 50) -> List[Dict[str, Any]]:
    print(f"[YouTube] Fetching up to {max_results} videos for query '{query}' in {country}...")
    if not settings.YOUTUBE_API_KEY:
        print("[YouTube] Skipping: YOUTUBE_API_KEY is not set.")
        return []

    search_url = "https://www.googleapis.com/youtube/v3/search"
    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    try:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "regionCode": country,
            "key": settings.YOUTUBE_API_KEY,
        }
        s = requests.get(search_url, params=params, timeout=15)
        s.raise_for_status()
        items = s.json().get("items", [])
        video_ids = ",".join(i["id"]["videoId"] for i in items if i.get("id", {}).get("videoId"))
        if not video_ids:
            print("[YouTube] No video IDs found from search.")
            return []

        print(f"[YouTube] Found {len(video_ids.split(','))} video IDs. Fetching details...")
        p2 = {"part": "statistics,snippet", "id": video_ids, "key": settings.YOUTUBE_API_KEY}
        v = requests.get(videos_url, params=p2, timeout=15)
        v.raise_for_status()
        vids = v.json().get("items", [])
    except Exception as e:
        print(f"[YouTube] ERROR: {e}")
        return []

    results: List[Dict[str, Any]] = []
    for vid in vids:
        sn = vid.get("snippet", {})
        st = vid.get("statistics", {})
        results.append(
            {
                "workflow": sn.get("title", "n8n workflow"),
                "platform": "YouTube",
                "popularity_metrics": {
                    "views": int(st.get("viewCount", 0)),
                    "likes": int(st.get("likeCount", 0)) if "likeCount" in st else 0,
                    "comments": int(st.get("commentCount", 0)) if "commentCount" in st else 0,
                },
                "country": country,
                "source_url": f"https://www.youtube.com/watch?v={vid.get('id')}",
                "source_metadata": {"video_id": vid.get("id")},
            }
        )
    print(f"[YouTube] Successfully processed {len(results)} videos for {country}.")
    return results


def fetch_forum(country: str, max_topics: int = 40, detail_limit: int = 20) -> List[Dict[str, Any]]:
    print(f"[Forum] Fetching topics for {country} from {settings.DISCOURSE_BASE_URL}...")

    base = settings.DISCOURSE_BASE_URL.rstrip("/")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) n8n-popularity-bot"}

    def get_topics(path: str) -> List[dict]:
        try:
            print(f"[Forum] Getting {base}{path}")
            resp = requests.get(f"{base}{path}", headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json() or {}
            topic_list = (data.get("topic_list", {}) or {}).get("topics", []) or data.get("topics", [])
            print(f"[Forum] Found {len(topic_list)} topics from {path}")
            return topic_list
        except Exception as e:
            print(f"[Forum] ERROR fetching {path}: {e}")
            return []

    latest = get_topics("/latest.json?order=created")
    top_week = get_topics("/top/weekly.json")
    combined: dict[int, dict] = {t["id"]: t for t in (latest + top_week) if isinstance(t, dict) and t.get("id")}

    topics = list(combined.values())[:max_topics]
    print(f"[Forum] Combined to {len(topics)} unique topics. Fetching details for {min(len(topics), detail_limit)}...")

    details_cache: dict[int, dict] = {}
    for t in topics[:detail_limit]:
        tid = t.get("id")
        try:
            d = requests.get(f"{base}/t/{tid}.json", headers=headers, timeout=20)
            if d.ok:
                details_cache[tid] = d.json() or {}
        except Exception:
            continue

    results: List[Dict[str, Any]] = []
    for t in topics:
        tid = t.get("id")
        det = details_cache.get(tid, {})
        details_data = det.get("details", {}) or {}
        participants = details_data.get("participants") or details_data.get("posters") or []

        results.append(
            {
                "workflow": t.get("title", "n8n workflow discussion"),
                "platform": "Forum",
                "popularity_metrics": {
                    "replies": int(t.get("reply_count", det.get("reply_count", 0))),
                    "likes": int(t.get("like_count", det.get("like_count", 0))),
                    "contributors": max(int(t.get("participant_count", 0)), len(participants)),
                    "views": int(t.get("views", det.get("views", 0))),
                },
                "country": country,
                "source_url": f"{base}/t/{tid}",
                "source_metadata": {"topic_id": tid},
            }
        )
    print(f"[Forum] Successfully processed {len(results)} topics for {country}.")
    return results


def fetch_trends(country: str, keywords: List[str]) -> List[Dict[str, Any]]:
    print(f"[Trends] Fetching {len(keywords)} keywords for {country}...")
    try:
        from pytrends.request import TrendReq
        import pandas as pd  # noqa: F401
    except Exception:
        print("[Trends] ERROR: pytrends or pandas is not installed.")
        return []

    def chunks(lst: List[str], n: int):
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    proxies = {"http": settings.TRENDS_PROXY_HTTP, "https": settings.TRENDS_PROXY_HTTPS}
    req_args = {
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"},
        "proxies": {k: v for k, v in proxies.items() if v},
        "timeout": (10, 25),
    }

    results: List[Dict[str, Any]] = []
    timeframes = ["today 12-m"]  # Reduced to single timeframe to avoid rate limits

    for group in chunks([k.strip() for k in keywords if k and k.strip()], 3):  # Reduced batch size to 3
        print(f"[Trends] Processing group: {', '.join(group)}")
        try:
            # Create new instance per group to avoid session issues
            pytrends = TrendReq(
                hl="en-US", tz=0, retries=1, backoff_factor=0.5, requests_args=req_args
            )
            time.sleep(2)  # Wait before request
            
            pytrends.build_payload(group, timeframe=timeframes[0], geo=country)
            df = pytrends.interest_over_time()
            
            if df is not None and not df.empty:
                for kw in [c for c in group if c in df.columns]:
                    series = df[kw]
                    win = 14 if len(series) >= 14 else len(series)
                    interest_score = float(series.tail(win).mean()) if win > 0 else 0.0

                    if len(series) >= 60:
                        last30 = float(series.tail(30).mean())
                        prev30 = float(series.tail(60).head(30).mean())
                        change = ((last30 - prev30) / prev30) if prev30 != 0 else 0.0
                    else:
                        change = 0.0

                    entry = {
                        "workflow": kw,
                        "platform": "Google",
                        "popularity_metrics": {"interest_score": round(interest_score, 2), "trend_30d_change": round(change, 4)},
                        "country": country,
                        "source_url": f"https://trends.google.com/trends/explore?date={requests.utils.quote(timeframes[0])}&q={requests.utils.quote(kw)}&geo={country}",
                        "source_metadata": {"keyword": kw, "timeframe": timeframes[0]},
                    }
                    metrics, score = compute_popularity("Google", dict(entry["popularity_metrics"]))
                    entry["popularity_metrics"] = metrics
                    entry["popularity_score"] = score
                    results.append(entry)
                print(f"[Trends] Successfully processed group: {', '.join(group)}")
            else:
                print(f"[Trends] No data returned for group: {', '.join(group)}")
        except Exception as e:
            print(f"[Trends] ERROR processing group: {e}")
            # Continue to next group instead of failing completely
            continue
        
        # Longer delay between groups to avoid rate-limiting
        print("[Trends] Pausing for 8 seconds to avoid rate-limiting...")
        time.sleep(8)
    
    print(f"[Trends] Successfully processed {len(results)} keywords for {country}.")
    return results


# --- Aggregation ---

def collect_all() -> List[Dict[str, Any]]:
    print("\n--- Starting Data Ingestion (real data) ---")
    items: List[Dict[str, Any]] = []

    for country in COUNTRIES:
        print(f"\n--- Processing Country: {country} ---")
        items.extend(fetch_youtube(country))
        items.extend(fetch_forum(country))
        keywords = [k for k in settings.TRENDS_KEYWORDS.split(",") if k.strip()]
        items.extend(fetch_trends(country, keywords))

    print(f"\n--- Ingestion Complete: Total items fetched: {len(items)} ---")

    enriched: List[Dict[str, Any]] = []
    for it in items:
        if it.get("popularity_score") is None:
            metrics, score = compute_popularity(it["platform"], dict(it["popularity_metrics"]))
            it["popularity_metrics"] = metrics
            it["popularity_score"] = score
        enriched.append(it)

    print(f"--- Enrichment Complete: Total items processed: {len(enriched)} ---")
    return enriched
