from fastapi import APIRouter

from src.api.accounts.urls import router as accounts_router
from src.api.monitoring.urls import router as monitoring_router

api_router = APIRouter(prefix="/api")

api_router.include_router(monitoring_router, tags=["Monitoring"])
api_router.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
