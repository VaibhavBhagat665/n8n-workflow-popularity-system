from __future__ import annotations
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from app.config import settings


class Scheduler:
    def __init__(self, app: FastAPI, job_func):
        self.app = app
        self.job_func = job_func
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self):
        # Parse CRON_SCHEDULE: "min hour day month dow"
        minute, hour, day, month, dow = settings.CRON_SCHEDULE.split()
        trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow)
        self.scheduler.add_job(self.job_func, trigger, id="refresh_job", replace_existing=True)
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=False)
