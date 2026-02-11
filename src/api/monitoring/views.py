from fastapi import status
from fastapi.responses import JSONResponse


async def welcome():
    """Welcome endpoint to verify the service is running."""
    return {"message": "Welcome to the authentication service", "version": "1.0.0"}


async def health_check():
    """Health check endpoint to verify the service is running."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "message": "Authentication service is running"},
    )
