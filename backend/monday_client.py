import httpx
import logging
from config import MONDAY_API_TOKEN, MONDAY_API_URL, DEALS_BOARD_ID, WORK_ORDERS_BOARD_ID
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MondayClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {MONDAY_API_TOKEN}",
            "Content-Type": "application/json",
            "API-Version": "2024-01"
        }
        self.url = MONDAY_API_URL
        
    async def fetch_board_items(self, board_id: str) -> Tuple[list, list]:
        query = """
        query ($boardId: [ID!]!, $cursor: String) {
          boards(ids: $boardId) {
            name
            columns {
              id
              title
              type
            }
            items_page(limit: 500, cursor: $cursor) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  column {
                    title
                  }
                  text
                  value
                }
              }
            }
          }
        }
        """
        all_items = []
        columns = []
        cursor = None
        has_next_page = True
        
        async with httpx.AsyncClient() as client:
            while has_next_page:
                variables = {"boardId": [board_id]}
                if cursor:
                    variables["cursor"] = cursor
                
                payload = {"query": query, "variables": variables}
                
                try:
                    response = await client.post(self.url, json=payload, headers=self.headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "errors" in data:
                        logger.error(f"GraphQL errors: {data['errors']}")
                        return [], []
                        
                    board_data = data.get("data", {}).get("boards", [])
                    if not board_data:
                        return [], []
                        
                    board = board_data[0]
                    if not columns:
                        columns = board.get("columns", [])
                        
                    items_page = board.get("items_page", {})
                    items = items_page.get("items", [])
                    all_items.extend(items)
                    
                    cursor = items_page.get("cursor")
                    if not cursor:
                        has_next_page = False
                        
                except Exception as e:
                    logger.error(f"Error fetching board items: {e}")
                    return all_items, columns
                    
        return all_items, columns

    async def get_deals(self) -> Tuple[list, list]:
        return await self.fetch_board_items(DEALS_BOARD_ID)
        
    async def get_work_orders(self) -> Tuple[list, list]:
        return await self.fetch_board_items(WORK_ORDERS_BOARD_ID)
