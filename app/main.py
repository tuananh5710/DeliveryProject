from fastapi import FastAPI, Depends
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
from aioredis import Redis

from app.global_env import load_config
from app.dependencies import verify_token
from app.logic.job_logic import scheduled_job
from app.routers.orders_router import order_router
from app.routers.resources_router import resources_router
from app.routers.customers_router import users_router
from app.routers.couriers_router import couriers_router

# Load config
load_config()

# Load FastAPI
app = FastAPI()

# Load Regis
redis = Redis(host='127.0.0.1', port=6379, db=0)

# Order route
app.include_router(order_router,
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "Not found"}}
)

# Resources route
app.include_router(resources_router,
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "Not found"}}
)

# Users route
app.include_router(users_router,
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "Not found"}}
)

# Couriers route
app.include_router(couriers_router,
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "Not found"}}
)

# Job run 7h AM every day
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'cron', hour=6, minute=0)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {"messages": "Hello FastAPI"}

