from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlparse

from extractors.email_extractor import EMAIL_REGEX
from extractors.phone_extractor import PHONE_REGEX


TEXT_KEYS = {
    "company_name",
    "website",
    "decision_maker",
    "phone",
    "email",
    "address",
    "industry",
    "industry_type",
    "employee_no",
    "branch_no",
    "annual_turnover",
    "current_erp",
    "description",
    "additional_info",
    "source",
}


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def _valid_url(url: str) -> bool:
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    return bool(parsed.netloc and "." in parsed.netloc)


def clean_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for key, value in rec.items():
        if isinstance(value, str):
            text = _clean_text(value)
            cleaned[key] = text if text else ""
        else:
            cleaned[key] = value if value is not None else ""

    email = str(cleaned.get("email", ""))
    if email and not EMAIL_REGEX.fullmatch(email):
        cleaned["email"] = ""

    phone = str(cleaned.get("phone", ""))
    if phone and not PHONE_REGEX.fullmatch(phone):
        cleaned["phone"] = ""

    website = str(cleaned.get("website", ""))
    if website and not _valid_url(website):
        cleaned["website"] = ""

    for key in TEXT_KEYS:
        cleaned.setdefault(key, "")

    return cleaned
