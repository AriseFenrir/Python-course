"""API key authentication dependency."""

import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = os.environ.get("API_KEY", "dev-secret-key")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate the API key from the X-API-Key header.

    Raises:
        HTTPException: 403 if the key is missing or invalid.
    """
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key
