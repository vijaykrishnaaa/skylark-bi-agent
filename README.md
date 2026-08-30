# Skylark Drones BI Agent

An AI-powered Business Intelligence agent that connects directly to Monday.com to answer founder-level business questions about sales pipelines and operations.

## Features

- **Live Monday.com Integration:** Fetches real-time data from Deals and Work Orders boards using the GraphQL API v2.
- **Intelligent Caching:** Pre-fetches and caches data to reduce latency from 3+ minutes down to 5-15 seconds per query.
- **Data Normalization:** Automatically cleans messy data (e.g., duplicate header rows, missing values, `#VALUE!` errors).
- **Executive Summaries:** Pre-calculates critical metrics (win rates, pipeline value, total billed vs collected) so the AI provides mathematically accurate answers.
- **Conversational Analytics:** Uses Google's Gemini Flash model to interpret complex business queries, cross-reference both boards, and provide structured insights.
- **Modern UI:** A clean, professional React frontend built with Vite and Tailwind-style custom CSS.

## Architecture

- **Backend:** Python + FastAPI
- **Frontend:** React + Vite
- **LLM:** Google Gemini Flash
- **Data Source:** Monday.com GraphQL API

## Prerequisites

- Node.js (LTS)
- Python 3.12+
- Monday.com API Token
- Google Gemini API Key

## Local Setup Instructions

### 1. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONDAY_API_TOKEN=your_monday_token_here
GEMINI_API_KEY=your_gemini_key_here
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
```

### 2. Start the Backend (FastAPI)

```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start the Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:3000`.

## Example Queries to Try

- *"Give me an executive leadership briefing."*
- *"What is our win rate, and who is our top performing sales rep?"*
- *"Show me the pipeline breakdown by sector."*
- *"Which work orders are stuck or at risk?"*
- *"What is our total unbilled contract value?"*
