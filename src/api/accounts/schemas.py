from pydantic import BaseModel, EmailStr, Field


# Request schemas
class SignupRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=70)


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=70)


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequestSchema(BaseModel):
    refresh_token: str
