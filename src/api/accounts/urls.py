from fastapi import APIRouter

from src.api.accounts import views

router = APIRouter()

router.add_api_route("/register", views.register_view, methods=["POST"])
router.add_api_route("/login", views.login_view, methods=["POST"])
router.add_api_route("/refresh", views.refresh_view, methods=["POST"])
router.add_api_route("/logout", views.logout_view, methods=["POST"])
router.add_api_route("/verify-email", views.verify_email_view, methods=["GET"])
router.add_api_route("/get-user-details", views.get_user_details_view, methods=["GET"])
