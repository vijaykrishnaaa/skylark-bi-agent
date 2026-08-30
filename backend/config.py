import os
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")
MONDAY_API_URL = "https://api.monday.com/v2"
