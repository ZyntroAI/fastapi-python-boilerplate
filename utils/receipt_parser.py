import re
from datetime import datetime

def parse_receipt(text):
    """
    Extract key information from receipt text
    Supports common Thai-English receipt formats
    """
    data = {
        "receipt_id": "-",
        "date": "-",
        "merchant": "-",
        "total": "-",
        "vat": "-",
        "item_count": "-",
        "currency": "THB"
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ===== Receipt/Invoice Number =====
    patterns_id = [
        r'(receipt\s*(no|#)|inv\s*no|invoice\s*(no|#))[:\s]*([A-Z0-9\-\/]+)',
        r'([A-Z]{2,3}[-/]\d{4,}|\d{4,}[-/]\d{4,})'
    ]
    for p in patterns_id:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            data["receipt_id"] = m.group(m.lastindex).strip()
            break
    
    # ===== Date =====
    patterns_date = [
        r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',
    ]
    for p in patterns_date:
        m = re.search(p, text)
        if m:
            data["date"] = m.group(0)
            break
    
    # ===== Total Amount =====
    patterns_total = [
        r'(total|grand\s*total|amount|sum)[:\s]*[฿]?\s*([\d,]+\.?\d*)',
        r'([\d,]+\.\d{2})\s*(thb|baht)',
    ]
    for p in patterns_total:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            data["total"] = m.group(m.lastindex)
            break
    
    # ===== Merchant Name =====
    for line in lines[:5]:
        if len(line) > 2 and not re.search(r'(\d{1,2}/\d{1,2}/\d{2,4}|www\.|http:|tel:|phone:)', line, re.IGNORECASE):
            if not any(w in line.lower() for w in ["receipt", "invoice", "date", "total", "---", "==="]):
                data["merchant"] = line
                break
    
    # ===== VAT Amount =====
    m_vat = re.search(r'(vat|tax)[:\s]*[฿]?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if m_vat:
        data["vat"] = m_vat.group(2)
    
    return data
