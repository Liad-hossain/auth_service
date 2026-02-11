from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.accounts.schemas import (
    LoginRequestSchema,
    LoginResponseSchema,
    RefreshRequestSchema,
    SignupRequestSchema,
)
from src.api.accounts.services import (
    get_user_details,
    login,
    logout,
    refresh_tokens,
    register,
    verify_email,
)
from src.utils.schema import MessageResponseSchema, ResponseSchema

security = HTTPBearer()


async def register_view(data: SignupRequestSchema) -> ResponseSchema:
    data = await register(email=data.email, password=data.password)
    return ResponseSchema(success=True, dataSource=data)


async def login_view(data: LoginRequestSchema) -> LoginResponseSchema:
    access_token, refresh_token = await login(email=data.email, password=data.password)
    return LoginResponseSchema(access_token=access_token, refresh_token=refresh_token)


async def refresh_view(data: RefreshRequestSchema) -> LoginResponseSchema:
    access_token, new_refresh_token = await refresh_tokens(data.refresh_token)
    return LoginResponseSchema(
        access_token=access_token, refresh_token=new_refresh_token
    )


async def logout_view(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> MessageResponseSchema:
    token = credentials.credentials
    await logout(token)

    return MessageResponseSchema(success=True, message="Logged out successfully.")


async def verify_email_view(email: str = Query(...), token: str = Query(...)) -> MessageResponseSchema:
    is_success = await verify_email(email=email, token=token)
    if not is_success:
        return MessageResponseSchema(
            success=False, message="Email verification failed."
        )
    return MessageResponseSchema(success=True, message="Email verified successfully.")


async def get_user_details_view(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> ResponseSchema:
    token = credentials.credentials
    user_details = await get_user_details(token)
    return ResponseSchema(success=True, dataSource=user_details)
