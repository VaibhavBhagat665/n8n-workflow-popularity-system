# Setup & Deployment Instructions

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- YouTube Data API v3 key (get from Google Cloud Console)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd n8n_popularity
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your YouTube API key
# YOUTUBE_API_KEY="your_actual_key_here"
```

### 4. Generate Initial Dataset
```bash
python generate_dataset.py
```

This will collect 50+ workflows from YouTube and n8n Forum (takes ~30 seconds).

### 5. Start API Server
```bash
uvicorn app.main:app --port 8000
```

API will be available at: `http://localhost:8000`

## Verify Installation

### Check Health
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

### View Statistics
```bash
curl http://localhost:8000/stats
```
Expected: JSON with workflow counts by platform and country

### Query Workflows
```bash
curl "http://localhost:8000/workflows?limit=5"
```
Expected: JSON array with 5 workflows

### Access API Documentation
Open browser: `http://localhost:8000/docs`

Interactive Swagger UI for testing all endpoints.

## API Usage Examples

### Get YouTube Workflows (US only)
```bash
curl "http://localhost:8000/workflows?platform=YouTube&country=US&limit=10"
```

### Get Top 20 by Popularity Score
```bash
curl "http://localhost:8000/workflows?sort_by=popularity_score&order=desc&limit=20"
```

### Get Forum Discussions (India)
```bash
curl "http://localhost:8000/workflows?platform=Forum&country=IN"
```

### Trigger Manual Data Refresh
```bash
curl -X POST http://localhost:8000/admin/refresh
```

## Production Deployment

### Option 1: Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t n8n-popularity-api .
docker run -p 8000:8000 --env-file .env n8n-popularity-api
```

### Option 2: Cloud Platforms

**Heroku**:
```bash
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku config:set YOUTUBE_API_KEY="your_key"
git push heroku main
```

**AWS EC2**:
```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run with systemd or supervisor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Google Cloud Run**:
```bash
gcloud run deploy n8n-popularity \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 3: VPS with Nginx

1. Install Nginx and configure reverse proxy
2. Use systemd service for auto-restart
3. Setup SSL with Let's Encrypt

Example systemd service (`/etc/systemd/system/n8n-api.service`):
```ini
[Unit]
Description=n8n Popularity API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/n8n_popularity
Environment="PATH=/usr/local/bin"
EnvironmentFile=/var/www/n8n_popularity/.env
ExecStart=/usr/local/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

[Install]
WantedBy=multi-user.target
```

## Automated Updates

The API automatically refreshes data daily at 3:00 AM UTC (configurable via `CRON_SCHEDULE` in `.env`).

To change schedule:
```bash
# Edit .env
CRON_SCHEDULE="0 */6 * * *"  # Every 6 hours
```

## Monitoring

### Check Logs
```bash
# If running with systemd
journalctl -u n8n-api -f

# If running with Docker
docker logs -f container-name
```

### Health Endpoint
Setup monitoring service (UptimeRobot, Pingdom) to ping:
```
GET http://your-domain.com/health
```

## Troubleshooting

### Issue: "No data collected"
- Verify `YOUTUBE_API_KEY` is set correctly in `.env`
- Check API key has YouTube Data API v3 enabled
- Ensure network connectivity

### Issue: "Google Trends rate limiting"
- Reduce `TRENDS_KEYWORDS` count in `.env`
- Increase `TRENDS_BACKOFF` value
- Configure proxy via `TRENDS_PROXY_HTTP`

### Issue: "Port already in use"
```bash
# Change port
uvicorn app.main:app --port 8080
```

### Issue: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Security Notes

- Never commit `.env` file to Git (already in `.gitignore`)
- Rotate API keys regularly
- Use environment variables in production
- Enable HTTPS in production
- Consider rate limiting for public APIs

## Support

For issues or questions:
1. Check API documentation: `http://localhost:8000/docs`
2. Review logs for error messages
3. Verify environment configuration
4. Test individual data sources with `generate_dataset.py`
