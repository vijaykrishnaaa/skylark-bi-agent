from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time

from monday_client import MondayClient
from data_cleaner import clean_deals_data, clean_work_orders_data
from agent import BIAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Skylark BI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

monday_client = MondayClient()
agent = BIAgent()

# --- Data Cache ---
# Cache monday.com data so we don't fetch on every single query
class DataCache:
    def __init__(self, ttl_seconds: int = 300):  # 5 min cache
        self.ttl = ttl_seconds
        self.deals_data: Optional[List[Dict]] = None
        self.wo_data: Optional[List[Dict]] = None
        self.deals_dq: Optional[Dict] = None
        self.wo_dq: Optional[Dict] = None
        self.last_fetch: float = 0
    
    def is_stale(self) -> bool:
        return (time.time() - self.last_fetch) > self.ttl or self.deals_data is None
    
    async def refresh(self):
        logger.info("Fetching fresh data from monday.com...")
        start = time.time()
        
        deals_raw, deals_cols = await monday_client.get_deals()
        work_orders_raw, wo_cols = await monday_client.get_work_orders()
        
        self.deals_data, self.deals_dq = clean_deals_data(deals_raw, deals_cols)
        self.wo_data, self.wo_dq = clean_work_orders_data(work_orders_raw, wo_cols)
        self.last_fetch = time.time()
        
        elapsed = time.time() - start
        logger.info(f"Data fetched and cleaned in {elapsed:.1f}s — {len(self.deals_data)} deals, {len(self.wo_data)} work orders")
    
    async def get_data(self):
        if self.is_stale():
            await self.refresh()
        return self.deals_data, self.wo_data, self.deals_dq, self.wo_dq

cache = DataCache(ttl_seconds=300)


class ChatRequest(BaseModel):
    message: str
    chat_history: List[Dict[str, str]] = []

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up... Configuration loaded.")
    # Pre-fetch data on startup so first query is fast
    try:
        await cache.refresh()
        logger.info("Initial data pre-fetch complete!")
    except Exception as e:
        logger.warning(f"Initial data fetch failed (will retry on first query): {e}")

@app.get("/")
async def root():
    return {"message": "Skylark BI Agent API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "cached_data": not cache.is_stale()}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Use cached data instead of fetching every time
        deals_data, wo_data, deals_dq, wo_dq = await cache.get_data()
        
        combined_dq = {
            "deals_missing_values": deals_dq,
            "work_orders_missing_values": wo_dq
        }
        
        response_text = agent.process_query(
            user_message=request.message,
            chat_history=request.chat_history,
            deals_data=deals_data,
            work_orders_data=wo_data,
            data_quality=combined_dq
        )
        
        return {
            "response": response_text,
            "data_quality": combined_dq
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh")
async def refresh_data():
    """Force refresh cached data from monday.com"""
    await cache.refresh()
    return {"status": "refreshed", "deals_count": len(cache.deals_data or []), "wo_count": len(cache.wo_data or [])}
