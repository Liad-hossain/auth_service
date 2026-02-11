import re
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from pwdlib import PasswordHash

from src.settings import settings

password_hash = PasswordHash.recommended()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.authentication_secret_key,
        algorithm=settings.authentication_algorithm,
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.authentication_secret_key,
        algorithm=settings.authentication_algorithm,
    )


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.authentication_secret_key,
            algorithms=[settings.authentication_algorithm],
        )
        return payload
    except JWTError:
        return None


def create_authentication_tokens(user_id: int, email: str) -> tuple[str, str]:
    token_data = {"sub": str(user_id), "email": email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    return access_token, refresh_token


def is_strong_password(password: str, min_length: int = 8) -> bool:
    """
    Criteria:
    - At least `min_length` characters (default 8)
    - Contains only printable ASCII characters (letters, numbers, symbols; no emojis or Unicode)
    - Contains at least one lowercase letter
    - Contains at least one uppercase letter
    - Contains at least one digit
    - Contains at least one special character (non-alphanumeric)
    - Contains no whitespace
    """
    if password is None:
        return False
    if len(password) < min_length:
        return False
    # Only allow printable ASCII characters (no emojis or other Unicode)
    if not re.match(r"^[\x20-\x7E]+$", password):
        return False
    if re.search(r"\s", password):  # no spaces, tabs, newlines
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    # special character: any non-word, non-space
    if not re.search(r"[^\w\s]", password):
        return False
    return True
