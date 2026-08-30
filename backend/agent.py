import google.generativeai as genai
from config import GEMINI_API_KEY
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel('gemini-3.6-flash')
    logger.info("Using gemini-3.6-flash model")
except Exception:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Using gemini-2.5-flash model")
    except Exception:
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Using gemini-1.5-flash model")

SYSTEM_PROMPT = """You are an expert Business Intelligence assistant for Skylark Drones — a drone technology company.

You have access to two datasets from monday.com:
1. **Deals Board** — Sales pipeline data with deal names, owners, clients, statuses (Open/Won/Dead/On Hold), deal values, sectors, stages, and dates.
2. **Work Orders Board** — Project execution data with serial numbers, customer codes, nature of work, execution status, financial details (amounts, billed, collected), sectors, and dates.

## Your Capabilities:
- Answer founder-level business questions about revenue, pipeline health, sectoral performance, operational metrics
- Query and analyze data across BOTH boards when needed
- Provide context and insights, not just raw numbers
- Handle ambiguous queries by asking clarifying questions
- Report data quality issues when they affect the answer

## Response Guidelines:
- Use markdown formatting: headers, bullet points, bold, tables where appropriate
- Include actual numbers and percentages
- When data is incomplete or has missing values, mention this as a caveat
- Provide actionable insights, not just data dumps
- For 'leadership updates' or 'executive summary' requests, generate a structured brief covering:
  - 📊 **Pipeline Overview** (total deals, by status, total value)
  - 🏆 **Key Wins** (recently won deals, their values)
  - 💰 **Revenue Metrics** (billed vs collected, outstanding)
  - ⚠️ **At-Risk Items** (on-hold deals, stuck work orders)
  - 🏭 **Sector Performance** (breakdown by Mining, Renewables, Railways, etc.)
  - 📋 **Action Items** (recommended next steps)

## Important Notes:
- Deal values are masked/anonymized but proportionally representative
- Deal names use anime/cartoon character names (they are anonymized)
- Owner codes (OWNER_001, etc.) represent sales personnel
- Client codes (COMPANY001, etc.) represent client companies
- Sectors include: Mining, Renewables, Railways, Powerline, Construction, DSP, Security, Others
- Deal stages range from A (Lead Generated) to O (Not Relevant), with key stages being:
  - A. Lead Generated → B. Sales Qualified → C. Demo Done → D. Feasibility → E. Proposal Sent → F. Negotiations → G. Project Won → H. Work Order Received → I. POC → J. Invoice Sent → K. Amount Accrued → L. Project Lost
"""


class BIAgent:
    def __init__(self):
        self.model = model

    def _build_data_summary(self, deals_data: List[Dict[str, Any]], work_orders_data: List[Dict[str, Any]], data_quality: Dict[str, Any]) -> str:
        """Build an intelligent summary of the data for the LLM context."""
        summary_parts = []

        # Data Quality Report
        summary_parts.append("## DATA QUALITY REPORT")
        summary_parts.append(json.dumps(data_quality, indent=2))

        # Deals Summary
        summary_parts.append("\n## DEALS DATA")
        if deals_data:
            total_deals = len(deals_data)
            summary_parts.append(f"Total Deals: {total_deals}")

            # Count by status
            status_counts = {}
            sector_counts = {}
            stage_counts = {}
            total_value = 0
            value_by_status = {}
            value_by_sector = {}

            for deal in deals_data:
                status = deal.get("Deal Status", "N/A")
                sector = deal.get("Sector/service", "N/A")
                stage = deal.get("Deal Stage", "N/A")

                status_counts[status] = status_counts.get(status, 0) + 1
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

                try:
                    val = float(deal.get("Masked Deal value", "0") or "0")
                    total_value += val
                    value_by_status[status] = value_by_status.get(status, 0) + val
                    value_by_sector[sector] = value_by_sector.get(sector, 0) + val
                except (ValueError, TypeError):
                    pass

            summary_parts.append(f"\nStatus Breakdown: {json.dumps(status_counts)}")
            summary_parts.append(f"Sector Breakdown: {json.dumps(sector_counts)}")
            summary_parts.append(f"Stage Breakdown: {json.dumps(stage_counts)}")
            summary_parts.append(f"Total Deal Value (all): {total_value:,.2f}")
            summary_parts.append(f"Value by Status: {json.dumps({k: f'{v:,.2f}' for k, v in value_by_status.items()})}")
            summary_parts.append(f"Value by Sector: {json.dumps({k: f'{v:,.2f}' for k, v in value_by_sector.items()})}")

            # Include all deals as compact records
            summary_parts.append(f"\nAll Deals Records ({total_deals} records):")
            summary_parts.append(json.dumps(deals_data, indent=1))
        else:
            summary_parts.append("No deals data available.")

        # Work Orders Summary
        summary_parts.append("\n## WORK ORDERS DATA")
        if work_orders_data:
            total_wo = len(work_orders_data)
            summary_parts.append(f"Total Work Orders: {total_wo}")

            exec_status_counts = {}
            wo_sector_counts = {}
            total_amount = 0
            total_billed = 0
            total_collected = 0

            for wo in work_orders_data:
                exec_status = wo.get("Execution Status", "N/A")
                sector = wo.get("Sector", "N/A")

                exec_status_counts[exec_status] = exec_status_counts.get(exec_status, 0) + 1
                wo_sector_counts[sector] = wo_sector_counts.get(sector, 0) + 1

                try:
                    amt = float(wo.get("Amount in Rupees (Excl of GST) (Masked)", "0") or "0")
                    total_amount += amt
                except (ValueError, TypeError):
                    pass
                try:
                    billed = float(wo.get("Billed Value in Rupees (Excl of GST.) (Masked)", "0") or "0")
                    total_billed += billed
                except (ValueError, TypeError):
                    pass
                try:
                    collected = float(wo.get("Collected Amount in Rupees (Incl of GST.) (Masked)", "0") or "0")
                    total_collected += collected
                except (ValueError, TypeError):
                    pass

            summary_parts.append(f"\nExecution Status Breakdown: {json.dumps(exec_status_counts)}")
            summary_parts.append(f"Sector Breakdown: {json.dumps(wo_sector_counts)}")
            summary_parts.append(f"Total Contract Amount (Excl GST): {total_amount:,.2f}")
            summary_parts.append(f"Total Billed (Excl GST): {total_billed:,.2f}")
            summary_parts.append(f"Total Collected (Incl GST): {total_collected:,.2f}")
            summary_parts.append(f"Collection Rate: {(total_collected / total_billed * 100) if total_billed > 0 else 0:.1f}%")

            # Include all work orders as compact records
            summary_parts.append(f"\nAll Work Orders Records ({total_wo} records):")
            summary_parts.append(json.dumps(work_orders_data, indent=1))
        else:
            summary_parts.append("No work orders data available.")

        return "\n".join(summary_parts)

    def process_query(self, user_message: str, chat_history: List[Dict[str, str]], deals_data: List[Dict[str, Any]], work_orders_data: List[Dict[str, Any]], data_quality: Dict[str, Any]) -> str:

        data_context = self._build_data_summary(deals_data, work_orders_data, data_quality)

        full_prompt = f"""{SYSTEM_PROMPT}

--- START OF DATA CONTEXT ---
{data_context}
--- END OF DATA CONTEXT ---

USER QUESTION: {user_message}

Analyze the data above and provide a comprehensive, insightful answer. Use markdown formatting."""

        messages = []
        for msg in chat_history[-10:]:  # Keep last 10 messages for context
            role = "user" if msg.get("role") == "user" else "model"
            messages.append({"role": role, "parts": [msg.get("content", "")]})

        messages.append({"role": "user", "parts": [full_prompt]})

        try:
            response = self.model.generate_content(messages)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error while processing your query: {str(e)}. Please try again or rephrase your question."
