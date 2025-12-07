import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables.

    CRON_SCHEDULE: APScheduler cron string (minute hour day month day_of_week).
    DATA_FILE: Path to persisted aggregated data JSON.
    YOUTUBE_API_KEY, DISCOURSE_API_KEY, DISCOURSE_API_USERNAME: Optional API creds.
    """

    CRON_SCHEDULE: str = os.getenv("CRON_SCHEDULE", "0 3 * * *")  # daily at 03:00

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE: str = os.getenv(
        "DATA_FILE",
        os.path.join(BASE_DIR, "store", "data", "workflows.json"),
    )

    # Optional proxies/retries for Google Trends
    TRENDS_PROXY_HTTP: Optional[str] = os.getenv("TRENDS_PROXY_HTTP")
    TRENDS_PROXY_HTTPS: Optional[str] = os.getenv("TRENDS_PROXY_HTTPS")
    TRENDS_RETRIES: int = int(os.getenv("TRENDS_RETRIES", "2"))
    TRENDS_BACKOFF: float = float(os.getenv("TRENDS_BACKOFF", "0.1"))

    # Optional external API credentials
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")

    DISCOURSE_BASE_URL: str = os.getenv("DISCOURSE_BASE_URL", "https://community.n8n.io")
    DISCOURSE_API_KEY: Optional[str] = os.getenv("DISCOURSE_API_KEY")
    DISCOURSE_API_USERNAME: Optional[str] = os.getenv("DISCOURSE_API_USERNAME")

    # Google Trends keywords (comma-separated). Defaults to a curated list.
    TRENDS_KEYWORDS: str = os.getenv(
        "TRENDS_KEYWORDS",
        ",".join(
            [
                "n8n Slack integration",
                "n8n WhatsApp reminders",
                "n8n Google Sheets",
                "n8n Gmail automation",
                "n8n Notion integration",
                "n8n Telegram bot",
                "n8n Airtable",
                "n8n Trello",
                "n8n Jira",
                "n8n Shopify",
                "n8n Stripe",
                "n8n Zoom",
                "n8n Calendly",
                "n8n Dropbox",
                "n8n Google Drive",
                "n8n GitHub issues",
                "n8n RSS",
                "n8n Zendesk",
                "n8n OpenAI",
                "n8n Facebook leads",
            ]
        ),
    )


settings = Settings()
