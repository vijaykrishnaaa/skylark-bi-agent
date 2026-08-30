# Decision Log — Skylark Drones BI Agent

## 1. Tech Stack Selection
**Stack Chosen:** Python (FastAPI) + React (Vite) + Google Gemini
- **Why Python backend?** Python offers the most mature ecosystem for AI/LLM integration (LangChain, direct SDKs) and data manipulation. FastAPI was chosen over Flask/Django for its native async support, which is critical when making external API calls to Monday.com and LLMs simultaneously.
- **Why React frontend?** React provides a reactive, component-based UI that handles chat states elegantly. Vite was chosen over Create React App for significantly faster build times.
- **Why Gemini?** Gemini Flash provides a massive context window (crucial for injecting full board data), fast inference speeds, and is cost-effective (free tier available) compared to GPT-4o.

## 2. Monday.com Integration: Direct API vs. MCP
**Decision:** Direct GraphQL API v2 calls with intelligent caching.
- **Context:** The prompt suggested connecting via MCP or API.
- **Rationale:** Building a direct GraphQL client allowed for exact pagination control and custom error handling. Because the assignment data contained ~500 total rows across two boards, we could fetch all relevant data and inject it directly into the LLM context.
- **Trade-off:** Fetching live data for every user query took 2-3 minutes due to API latency and payload size.
- **Solution:** Implemented a caching layer (`DataCache` in `main.py`) that pre-fetches data on startup and caches it for 5 minutes. This brought query latency down to 5-15 seconds.

## 3. Data Resilience & Normalization
**Decision:** Pre-processing layer before LLM ingestion.
- **Context:** The dataset was highly messy (e.g., `#VALUE!` errors, rows acting as headers embedded mid-file, missing deal values).
- **Rationale:** While LLMs are good at inferring dirty data, relying on them to perform accurate mathematical sums on messy data often leads to hallucinations.
- **Implementation:** Built a `data_cleaner.py` module that:
  1. Identifies and strips rogue header rows.
  2. Normalizes numerical strings (stripping currency symbols, handling #VALUE!).
  3. Groups and pre-calculates core metrics (Total Pipeline, Total Billed, Win Rate) *before* sending the context to the LLM.

## 4. Interpretation of "Leadership Updates"
**Decision:** Implemented a specific prompt trigger for executive summaries.
- **Rationale:** Founders don't just want data; they want insights. The system prompt was engineered to recognize terms like "leadership update" or "executive brief" and automatically structure the response into 6 standard business categories: Pipeline Overview, Key Wins, Revenue Metrics, At-Risk Items, Sector Performance, and Action Items.

## 5. Future Improvements (If I had more time)
- **Vector Database:** Instead of injecting all 500 rows into the prompt context, I would implement RAG (Retrieval-Augmented Generation) using Pinecone or ChromaDB to scale to tens of thousands of rows.
- **Webhooks:** Instead of a 5-minute time-based cache, I would set up Monday.com webhooks to invalidate the cache only when a board item is actively updated.
- **OAuth2 Integration:** Currently uses a hardcoded Personal API token. For production, I would implement a full OAuth flow so any Monday.com user could authorize the app.
