# n8n Workflow Popularity API

Production-ready REST API that identifies the most popular n8n workflows across YouTube, n8n Forum, and Google Trends with real-time data collection and automated daily updates.

## Features

- **Multi-Platform Data Collection**: YouTube videos, n8n Forum discussions, Google Trends search data
- **Real-Time Metrics**: Views, likes, comments, engagement ratios, search interest scores
- **Country Segmentation**: US and India markets
- **Automated Updates**: Daily cron job for fresh data
- **Production Ready**: Clean code, error handling, API documentation

## Tech Stack

FastAPI • Python 3.10+ • APScheduler • pytrends • YouTube Data API v3 • Discourse API

## Quick Start

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
# Edit .env and add your YOUTUBE_API_KEY
```

**3. Run the API**
```bash
uvicorn app.main:app --port 8000 --env-file .env
```

**4. Access API docs**
```
http://localhost:8000/docs
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/workflows` | GET | List workflows with filters (platform, country, sort, limit, offset) |
| `/stats` | GET | Aggregate statistics by platform and country |
| `/admin/refresh` | POST | Trigger manual data refresh |

**Example Request:**
```bash
curl "http://localhost:8000/workflows?platform=YouTube&country=US&limit=10"
```

**Example Response:**
```json
{
  "workflow": "Automate Gmail with n8n",
  "platform": "YouTube",
  "popularity_metrics": {
    "views": 18400,
    "likes": 920,
    "comments": 112,
    "like_to_view_ratio": 0.05,
    "comment_to_view_ratio": 0.006
  },
  "popularity_score": 87.5,
  "country": "US",
  "source_url": "https://www.youtube.com/watch?v=..."
}
```

## Configuration

Edit `.env` file:

```bash
# Required
YOUTUBE_API_KEY="your_youtube_api_key_here"

# Optional
CRON_SCHEDULE="0 3 * * *"  # Daily at 3 AM UTC
DISCOURSE_BASE_URL="https://community.n8n.io"
TRENDS_KEYWORDS="n8n Slack integration,n8n Google Sheets,n8n Gmail automation"
```

**Note on Google Trends**: Rate limiting is common. Keep `TRENDS_KEYWORDS` list small (5-10 keywords) or configure proxies via `TRENDS_PROXY_HTTP` and `TRENDS_PROXY_HTTPS`.

## Project Structure

```
app/
├── main.py              # FastAPI application & startup
├── config.py            # Environment configuration
├── routers/             # API endpoints
│   ├── workflows.py
│   ├── stats.py
│   ├── admin.py
│   └── health.py
├── services/
│   └── ingestion.py     # Data collection from all platforms
├── utils/
│   └── scoring.py       # Popularity score calculation
├── store/
│   └── repository.py    # JSON file persistence
└── sched/
    └── scheduler.py     # Cron job scheduler
```

## Testing Data Collection

Run standalone test to verify data fetching:
```bash
python test_fetch.py
```

This will collect data from all platforms and save to `app/store/data/workflows.json`.

## Deployment Notes

- **Storage**: Uses JSON file (no database required). For production scale, consider PostgreSQL/MongoDB.
- **Cron**: Automated daily refresh via APScheduler. Runs in-process.
- **API Keys**: YouTube API key is required. Forum and Trends work without authentication.
- **Rate Limits**: Google Trends is most restrictive. Implement delays and keep keyword list minimal.

## License

MIT
