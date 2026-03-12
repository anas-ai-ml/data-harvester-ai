from __future__ import annotations

ERP_PATTERNS = {
    "SAP": [" sap ", "sap s/4hana", "sap business one"],
    "Oracle ERP": ["oracle erp", "oracle fusion"],
    "Microsoft Dynamics": ["microsoft dynamics", "dynamics 365", "d365"],
    "NetSuite": ["netsuite"],
    "Odoo": ["odoo"],
    "Zoho ERP": ["zoho erp", "zoho finance"],
    "Tally ERP": ["tally erp", "tallyprime", "tally prime"],
    "Infor ERP": ["infor erp", "infor cloudsuite", "infor"],
}


def detect_erp_name(text: str | None) -> str:
    haystack = f" {text.lower()} " if text else " "
    for erp_name, patterns in ERP_PATTERNS.items():
        if any(pattern in haystack for pattern in patterns):
            return erp_name
    return ""
