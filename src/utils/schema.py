from fastapi import HTTPException
from pydantic import BaseModel


class CustomException(HTTPException):
    def __init__(
        self,
        message: str | None = None,
        error: str | None = None,
        error_code: int | None = None,
    ):
        if message is None:
            message = "Something Unexpected Happened."
        if error is None:
            error = "invalid"
        if error_code is None:
            error_code = 400

        detail = {"success": False, "message": message, "error": error}
        super().__init__(status_code=error_code, detail=detail)


class ResponseSchema(BaseModel):
    success: bool
    dataSource: dict | None = None


class MessageResponseSchema(BaseModel):
    success: bool
    message: str
