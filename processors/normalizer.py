from __future__ import annotations

import re
from typing import Any, Dict
from urllib.parse import urlparse


NON_DIGIT_PHONE = re.compile(r"[^\d+]")


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""
    normalized = NON_DIGIT_PHONE.sub("", phone)
    return normalized


def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    value = url.strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"
    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme.lower()}://{host}{path}"


def normalize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(rec)
    normalized["company_name"] = str(normalized.get("company_name", "")).strip()
    normalized["website"] = normalize_url(str(normalized.get("website", "")))
    normalized["phone"] = normalize_phone(str(normalized.get("phone", "")))
    normalized["email"] = str(normalized.get("email", "")).strip().lower()
    normalized["industry"] = str(normalized.get("industry", "")).strip().title()
    normalized["industry_type"] = str(normalized.get("industry_type", "")).strip().title()
    normalized["address"] = str(normalized.get("address", "")).strip(" ,")
    return normalized
