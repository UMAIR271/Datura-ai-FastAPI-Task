from fastapi import Header, HTTPException, status, Depends
from typing import Optional, AsyncGenerator
from redis import Redis
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

def get_redis() -> Redis:
    """
    Get a Redis client instance
    """
    try:
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=False
        )
    except Exception as e:
        print(f"Redis connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {str(e)}"
        )

def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Validate the API key
    """
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return x_api_key