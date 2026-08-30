import google.generativeai as genai
from config import GEMINI_API_KEY
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

# Use the latest model which exists
model = genai.GenerativeModel('gemini-3.6-flash')
logger.info("Using gemini-3.6-flash model")

SYSTEM_PROMPT = """You are an expert Business Intelligence assistant for Skylark Drones.

You have access to two datasets from monday.com:
1. **Deals Board** — Sales pipeline data.
2. **Work Orders Board** — Project execution data.

## Response Guidelines:
- Answer founder-level business questions about revenue, pipeline health, operational metrics.
- Use markdown formatting: headers, bullet points, bold, tables where appropriate.
- Include actual numbers and percentages.
- Provide actionable insights, not just data dumps.
- For 'leadership updates', generate a structured brief covering Pipeline Overview, Key Wins, Revenue Metrics, At-Risk Items, and Action Items.
- Deal values are masked but proportionally representative.
"""

class BIAgent:
    def __init__(self):
        self.model = model

    def _build_data_summary(self, deals_data: List[Dict[str, Any]], work_orders_data: List[Dict[str, Any]], data_quality: Dict[str, Any]) -> str:
        """Build an intelligent, highly compressed summary of the data for the LLM context."""
        summary_parts = []

        summary_parts.append("## DEALS DATA (Metrics)")
        if deals_data:
            total_deals = len(deals_data)
            status_counts = {}
            total_value = 0
            
            # Compress deals to avoid token limits (keep only essential keys)
            compact_deals = []
            for deal in deals_data:
                status = deal.get("Deal Status", "N/A")
                status_counts[status] = status_counts.get(status, 0) + 1
                try:
                    total_value += float(deal.get("Masked Deal value", "0") or "0")
                except:
                    pass
                
                # Keep only what's needed to answer questions like "which tasks are overdue"
                compact_deal = {
                    "Name": deal.get("Name"),
                    "Status": status,
                    "Stage": deal.get("Deal Stage"),
                    "Value": deal.get("Masked Deal value"),
                    "Close Date": deal.get("Tentative Close Date"),
                    "Sector": deal.get("Sector/service")
                }
                # Remove empty keys to save tokens
                compact_deals.append({k: v for k, v in compact_deal.items() if v and v != "N/A"})

            summary_parts.append(f"Total Deals: {total_deals} | Total Value: {total_value:,.2f}")
            summary_parts.append(f"Status Breakdown: {json.dumps(status_counts)}")
            summary_parts.append(f"Essential Deal Records:\n{json.dumps(compact_deals, separators=(',', ':'))}")

        summary_parts.append("\n## WORK ORDERS DATA (Metrics)")
        if work_orders_data:
            total_wo = len(work_orders_data)
            exec_status_counts = {}
            total_amount = 0
            total_billed = 0
            
            compact_wos = []
            for wo in work_orders_data:
                exec_status = wo.get("Execution Status", "N/A")
                exec_status_counts[exec_status] = exec_status_counts.get(exec_status, 0) + 1
                try:
                    total_amount += float(wo.get("Amount in Rupees (Excl of GST) (Masked)", "0") or "0")
                except:
                    pass
                
                compact_wo = {
                    "ID": wo.get("Name"),
                    "Status": exec_status,
                    "Sector": wo.get("Sector"),
                    "Value": wo.get("Amount in Rupees (Excl of GST) (Masked)"),
                    "End Date": wo.get("Probable End Date"),
                    "Start Date": wo.get("Probable Start Date")
                }
                compact_wos.append({k: v for k, v in compact_wo.items() if v and v != "N/A"})

            summary_parts.append(f"Total WO: {total_wo} | Total Value: {total_amount:,.2f}")
            summary_parts.append(f"Status Breakdown: {json.dumps(exec_status_counts)}")
            summary_parts.append(f"Essential WO Records:\n{json.dumps(compact_wos, separators=(',', ':'))}")

        return "\n".join(summary_parts)

    def process_query(self, user_message: str, chat_history: List[Dict[str, str]], deals_data: List[Dict[str, Any]], work_orders_data: List[Dict[str, Any]], data_quality: Dict[str, Any]) -> str:
        data_context = self._build_data_summary(deals_data, work_orders_data, data_quality)

        full_prompt = f"{SYSTEM_PROMPT}\n\n--- DATA CONTEXT ---\n{data_context}\n--- END DATA ---\n\nUSER QUESTION: {user_message}"

        messages = []
        # Keep ONLY the last 4 messages to save tokens
        for msg in chat_history[-4:]:
            role = "user" if msg.get("role") == "user" else "model"
            messages.append({"role": role, "parts": [msg.get("content", "")]})

        messages.append({"role": "user", "parts": [full_prompt]})

        try:
            response = self.model.generate_content(messages)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error while processing your query: {str(e)}. Please try again or rephrase your question."
