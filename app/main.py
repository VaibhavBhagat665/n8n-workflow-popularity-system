from __future__ import annotations
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import workflows, stats, admin, health
from app.store import repository
from app.services.ingestion import collect_all
from app.sched.scheduler import Scheduler


app = FastAPI(title="n8n Workflow Popularity API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(workflows.router)
app.include_router(stats.router)
app.include_router(admin.router)


scheduler: Scheduler | None = None


@app.on_event("startup")
async def on_startup():
    # Bootstrap: ensure we have data, but do not block startup
    def refresh_job():
        items = collect_all()
        repository.save_all(items)

    if not repository.load_all():
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, refresh_job)

    # Start scheduler for daily refresh
    global scheduler
    scheduler = Scheduler(app, refresh_job)
    scheduler.start()


@app.on_event("shutdown")
async def on_shutdown():
    global scheduler
    if scheduler:
        scheduler.shutdown()
