from fastapi import APIRouter

from src.api.monitoring.urls import router as monitoring_router

api_router = APIRouter()

api_router.include_router(monitoring_router, tags=["Monitoring"])
