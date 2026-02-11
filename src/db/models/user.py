from datetime import datetime

from pydantic import BaseModel

from src.db.config import database


class UserSchema(BaseModel):
    id: int
    email: str
    password_hash: str | None = None
    is_verified: bool | None = None
    created_at: datetime
    updated_at: datetime


async def create_user(email: str, password_hash: str) -> UserSchema | None:
    query = """
        INSERT INTO users (email, password_hash)
        VALUES (:email, :password_hash)
        RETURNING id, email, is_verified, created_at, updated_at
    """
    user = await database.fetch_one(
        query=query, values={"email": email, "password_hash": password_hash}
    )
    if user:
        return UserSchema(**user)
    return None


async def get_user_by_email(email: str) -> UserSchema | None:
    query = """
        SELECT id, email, password_hash, is_verified, created_at, updated_at
        FROM users
        WHERE email = :email
    """
    user = await database.fetch_one(query=query, values={"email": email})
    if user:
        return UserSchema(**user)
    return None


async def get_user_by_id(user_id: int) -> UserSchema | None:
    query = """
        SELECT id, email, created_at, updated_at
        FROM users
        WHERE id = :user_id
    """
    user = await database.fetch_one(query=query, values={"user_id": user_id})
    if user:
        return UserSchema(**user)
    return None


async def update_user_by_id(user_id: int, update_dict: dict) -> None:
    set_clause = ", ".join([f"{key} = :{key}" for key in update_dict.keys()])
    query = f"""
        UPDATE users
        SET {set_clause}, updated_at = NOW()
        WHERE id = :user_id
        RETURNING id, email, is_verified, created_at, updated_at
    """
    values = {**update_dict, "user_id": user_id}
    user = await database.fetch_one(query=query, values=values)
    if user:
        return UserSchema(**user)
    return None


async def update_user_by_email(email: str, update_dict: dict) -> None:
    set_clause = ", ".join([f"{key} = :{key}" for key in update_dict.keys()])
    query = f"""
        UPDATE users
        SET {set_clause}, updated_at = NOW()
        WHERE email = :email
        RETURNING id, email, is_verified, created_at, updated_at
    """
    values = {**update_dict, "email": email}
    user = await database.fetch_one(query=query, values=values)
    if user:
        return UserSchema(**user)
    return None
