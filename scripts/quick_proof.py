import json
import os
import re
import pathlib
import sys

import requests

try:
    from pytrends.request import TrendReq
except Exception:
    TrendReq = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


def read_env_var(key: str) -> str | None:
    if not ENV_PATH.exists():
        return None
    text = ENV_PATH.read_text(encoding="utf-8", errors="ignore")
    m = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*\"?([^\r\n\"]+)", text)
    return m.group(1) if m else None


def youtube_sample():
    key = read_env_var("YOUTUBE_API_KEY")
    if not key:
        return {"error": "YOUTUBE_API_KEY not set in .env"}
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "type": "video",
                "maxResults": 5,
                "q": "n8n workflow",
                "regionCode": "US",
                "key": key,
            },
            timeout=20,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        return [
            {"title": i["snippet"]["title"], "channel": i["snippet"]["channelTitle"]}
            for i in items
            if isinstance(i, dict) and i.get("snippet")
        ]
    except Exception as e:
        return {"error": f"YouTube request failed: {e}"}


def forum_sample():
    try:
        r = requests.get(
            "https://community.n8n.io/latest.json?order=created", timeout=20
        )
        r.raise_for_status()
        topics = (r.json().get("topic_list", {}) or {}).get("topics", [])[:5]
        return [
            {
                "title": t.get("title"),
                "views": t.get("views"),
                "replies": t.get("reply_count"),
                "likes": t.get("like_count"),
            }
            for t in topics
        ]
    except Exception as e:
        return {"error": f"Forum request failed: {e}"}


def trends_sample():
    if TrendReq is None:
        return {"error": "pytrends not installed"}
    try:
        py = TrendReq(hl="en-US", tz=0)
        kw = "n8n Slack integration"
        py.build_payload([kw], timeframe="now 7-d", geo="US")
        df = py.interest_over_time()
        if df is None or df.empty or kw not in df.columns:
            return {"keyword": kw, "interest_score_7d_avg": 0.0, "points": 0}
        s = df[kw]
        val = float(s.tail(7).mean()) if len(s) > 0 else 0.0
        return {"keyword": kw, "interest_score_7d_avg": round(val, 2), "points": int(len(s))}
    except Exception as e:
        return {"error": f"Trends request failed: {e}"}


def main():
    print("YouTube sample:")
    print(json.dumps(youtube_sample(), indent=2, ensure_ascii=False))
    print("\nForum sample:")
    print(json.dumps(forum_sample(), indent=2, ensure_ascii=False))
    print("\nTrends sample:")
    print(json.dumps(trends_sample(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
