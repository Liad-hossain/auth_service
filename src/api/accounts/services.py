import json
import logging
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import status

from src.db.config import redis
from src.db.models.user import (
    UserSchema,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_by_email,
    update_user_by_id,
)
from src.externals.smtp import SMTPEmailHandler
from src.settings import settings
from src.utils.schema import CustomException

from .utils import (
    create_authentication_tokens,
    decode_token,
    get_password_hash,
    is_strong_password,
    verify_password,
)

logger = logging.getLogger("stdout")


async def register(email: str, password: str) -> UserSchema:
    try:
        existing_user = await get_user_by_email(email)
        if existing_user:
            if existing_user.is_verified:
                raise CustomException(
                    message="A verified account with this email already exists.",
                    error="email_already_registered",
                    error_code=status.HTTP_400_BAD_REQUEST,
                )
            else:
                cache = None
                try:
                    cache = redis.get(f"email_verification: {email}")
                except Exception as e:
                    logger.error(f"Error fetching email verification cache: {e}")

                if cache:
                    raise CustomException(
                        message="A verification email has already been sent to this address. Please check your inbox.",
                        error="verification_email_already_sent",
                        error_code=status.HTTP_400_BAD_REQUEST,
                    )

        if not is_strong_password(password):
            raise CustomException(
                message="Password is not strong enough. It must be at least 8 characters long and include uppercase letters, lowercase letters, digits, and special characters.",
                error="weak_password",
                error_code=status.HTTP_400_BAD_REQUEST,
            )

        password_hash = get_password_hash(password)
        if not existing_user:
            user = await create_user(email=email, password_hash=password_hash)
        else:
            user = await update_user_by_id(
                user_id=existing_user.id,
                update_dict={"password_hash": password_hash},
            )

        token = uuid4()
        verification_link = (
            settings.base_url
            + f"/api/accounts/verify-email?email={email}&token={token}"
        )
        SMTPEmailHandler().send_verification_email(
            to_email=email, verification_link=verification_link
        )

        redis.set(f"email_verification: {email}", str(token), ex=3600 * 24)
    except CustomException:
        raise
    except Exception as e:
        logger.error(f"Error while registering for email {email}: {e}")
        raise CustomException(
            message="Registration failed due to an internal error.",
            error="registration_failed",
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e
    return user.__dict__ if user else {}


async def login(email: str, password: str) -> tuple[str, str]:
    try:
        user = await get_user_by_email(email)
        if not user or not user.is_verified:
            raise CustomException(
                message="Invalid email",
                error="invalid_credentials",
                error_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not verify_password(password, user.password_hash):
            raise CustomException(
                message="Invalid password",
                error="invalid_credentials",
                error_code=status.HTTP_401_UNAUTHORIZED,
            )

        access_token, refresh_token = create_authentication_tokens(user.id, user.email)
        redis.set(
            f"auth: {access_token}",
            json.dumps({"user_id": user.id, "email": user.email}),
            ex=settings.access_token_expire_minutes * 60,
        )
    except Exception as e:
        logger.error(f"Error during login for email {email}: {e}")
        raise CustomException(
            message="Login failed due to an internal error.",
            error="login_failed",
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e

    return access_token, refresh_token


async def refresh_tokens(refresh_token: str) -> tuple[str, str]:
    is_blacklisted = redis.get(f"blacklist:{refresh_token}")
    if is_blacklisted:
        raise CustomException(
            message="Refresh token has been revoked",
            error="token_revoked",
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = decode_token(refresh_token)
    if not payload:
        raise CustomException(
            message="Invalid or expired refresh token",
            error="invalid_token",
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    token_type = payload.get("type")
    if token_type != "refresh":
        raise CustomException(
            message="Provided token is not a valid refresh token",
            error="invalid_token_type",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_id = int(payload.get("sub"))
        email = payload.get("email")
    except Exception as exc:
        raise CustomException(
            message="Malformed token payload",
            error="invalid_payload",
            error_code=status.HTTP_400_BAD_REQUEST,
        ) from exc

    exp = payload.get("exp")
    if exp:
        from datetime import UTC, datetime

        ttl = exp - int(datetime.now(UTC).timestamp())
        if ttl > 0:
            redis.setex(f"blacklist:{refresh_token}", ttl, "1")

    access_token, new_refresh_token = create_authentication_tokens(user_id, email)
    return access_token, new_refresh_token


async def logout(token: str) -> bool:
    payload = decode_token(token)
    if not payload:
        raise CustomException(
            message="Invalid token",
            error="invalid_token",
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    exp = payload.get("exp")
    if exp:
        ttl = exp - int(datetime.now(UTC).timestamp())
        if ttl > 0:
            redis.setex(f"blacklist:{token}", ttl, "1")

    return True


async def verify_email(email: str, token: str) -> bool:
    try:
        cache_token = redis.get(f"email_verification: {email}")
        if not cache_token or cache_token != token:
            raise CustomException(
                message="Invalid or expired email verification token",
                error="invalid_token",
                error_code=status.HTTP_400_BAD_REQUEST,
            )

        user = await update_user_by_email(
            email=email, update_dict={"is_verified": True}
        )
        if not user:
            raise CustomException(
                message="User not found for email verification",
                error="invalid_user",
                error_code=status.HTTP_404_NOT_FOUND,
            )
        redis.delete(f"email_verification: {email}")
        return True
    except Exception as e:
        logger.error(f"Error verifying email: {e}")
        return False


async def get_user_details(token: str) -> UserSchema:
    payload = decode_token(token)
    if not payload:
        raise CustomException(
            message="Invalid or expired access token",
            error="invalid_token",
            error_code=status.HTTP_401_UNAUTHORIZED,
        )

    token_type = payload.get("type")
    if token_type != "access":
        raise CustomException(
            message="Provided token is not a valid access token",
            error="invalid_token_type",
            error_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_id = int(payload.get("sub"))
        user = await get_user_by_id(user_id)
        if not user:
            raise CustomException(
                message="User not found",
                error="invalid_user",
                error_code=status.HTTP_404_NOT_FOUND,
            )
    except Exception as exc:
        raise CustomException(
            message="Malformed token payload",
            error="invalid_payload",
            error_code=status.HTTP_400_BAD_REQUEST,
        ) from exc

    return user.__dict__ if user else {}
