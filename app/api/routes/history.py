from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.api.deps import get_api_key
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text
from app.db.models import DividendQueryHistory, SentimentTaskHistory
import traceback

router = APIRouter()

@router.get("/query-history", summary="Get dividend query history")
async def get_query_history(
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    netuid: Optional[int] = Query(None, description="Filter by network UID"),
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Get historical dividend query data"""
    try:
        print("Querying dividend history")
        query = select(DividendQueryHistory).order_by(desc(DividendQueryHistory.created_at))
        
        if netuid is not None:
            print(f"Filtering by netuid: {netuid}")
            query = query.filter(DividendQueryHistory.netuid == netuid)
            
        query = query.limit(limit)
        print(f"Query SQL: {query}")
        
        result = await db.execute(query)
        queries = result.scalars().all()
        
        # Check if table exists and has any records - using proper text() function
        check_query = text("SELECT COUNT(*) FROM dividend_query_history")
        count_result = await db.execute(check_query)
        total_count = count_result.scalar()
        print(f"Total records in dividend_query_history: {total_count}")
        
        # Convert to list to log the count
        query_list = list(queries)
        print(f"Found {len(query_list)} records in query result")
        
        return [
            {
                "query_id": q.query_id,
                "netuid": q.netuid,
                "hotkey": q.hotkey,
                "dividends": q.dividends,
                "stake": q.stake,
                "balance": q.balance,
                "cached": q.cached,
                "created_at": q.created_at.isoformat()
            }
            for q in query_list
        ]
    except Exception as e:
        print(f"Error retrieving query history: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/task-history", summary="Get sentiment analysis task history")
async def get_task_history(
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Get history of sentiment analysis tasks"""
    try:
        query = select(SentimentTaskHistory).order_by(desc(SentimentTaskHistory.created_at))
        
        if status:
            query = query.filter(SentimentTaskHistory.status == status.upper())
            
        query = query.limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return [
            {
                "task_id": task.task_id,
                "netuid": task.netuid,
                "hotkey": task.hotkey,
                "sentiment_score": task.sentiment_score,
                "action": task.action,
                "amount": task.amount,
                "status": task.status,
                "error": task.error,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in tasks
        ]
    except Exception as e:
        print(f"Error retrieving task history: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
