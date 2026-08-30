import datetime
import re
from typing import List, Dict, Any, Tuple

def _extract_text(item: Dict[str, Any], column_title: str) -> str:
    for cv in item.get("column_values", []):
        col_info = cv.get("column", {})
        if col_info and col_info.get("title") == column_title:
            return cv.get("text") or ""
    return ""

def _clean_value(val: str, default: str = "N/A") -> str:
    val = val.strip()
    if not val or val.lower() in ("null", "none", "#value!"):
        return default
    return val

def _parse_date(date_str: str) -> str:
    if not date_str or date_str == "N/A":
        return "N/A"
    try:
        # Return as is if format parsing is ambiguous, usually monday.com returns a decent string
        return date_str
    except Exception:
        return "N/A"

def _parse_numeric(num_str: str) -> float:
    if not num_str or num_str == "N/A":
        return 0.0
    clean_str = re.sub(r'[^\d.-]', '', num_str)
    try:
        return float(clean_str) if clean_str else 0.0
    except ValueError:
        return 0.0

def _normalize_sector(sector: str) -> str:
    if not sector or sector == "N/A":
        return "N/A"
    return sector.title()

def clean_deals_data(raw_items: List[Dict[str, Any]], columns: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    cleaned_data = []
    dq_report = {}
    
    col_titles = [c.get("title") for c in columns if c.get("title")]
    for t in col_titles:
        dq_report[t] = 0
        
    for item in raw_items:
        clean_item = {"Name": item.get("name", "N/A")}
        is_header_row = False
        
        for col in columns:
            title = col.get("title")
            if not title:
                continue
            
            raw_val = _extract_text(item, title)
            val = _clean_value(raw_val)
            
            if val.lower() == title.lower() and val != "N/A":
                is_header_row = True
                break
                
            if val == "N/A":
                dq_report[title] = dq_report.get(title, 0) + 1
                
            if "date" in title.lower():
                val = _parse_date(val)
            elif "value" in title.lower() or "revenue" in title.lower() or "amount" in title.lower():
                val = str(_parse_numeric(val))
            elif "sector" in title.lower():
                val = _normalize_sector(val)
                
            clean_item[title] = val
            
        if not is_header_row:
            cleaned_data.append(clean_item)
            
    return cleaned_data, dq_report

def clean_work_orders_data(raw_items: List[Dict[str, Any]], columns: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    return clean_deals_data(raw_items, columns)
