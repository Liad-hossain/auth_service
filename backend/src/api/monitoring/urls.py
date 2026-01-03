from fastapi import APIRouter

from src.api.monitoring import views

router = APIRouter()

router.add_api_route("/", views.welcome, methods=["GET"])
router.add_api_route("/health", views.health_check, methods=["GET"])
