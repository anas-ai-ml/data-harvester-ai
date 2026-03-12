from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


KEY_FIELDS = [
    "company_name",
    "website",
    "email",
    "phone",
    "decision_maker",
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
]


def _dedupe_key(rec: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        str(rec.get("company_name", "")).lower(),
        str(rec.get("website", "")).lower(),
        str(rec.get("email", "")).lower(),
    )


def _merge(primary: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(primary)
    for key in KEY_FIELDS:
        if not merged.get(key) and incoming.get(key):
            merged[key] = incoming[key]
    if primary.get("additional_info") and incoming.get("additional_info"):
        extras = [primary["additional_info"], incoming["additional_info"]]
        merged["additional_info"] = " | ".join(dict.fromkeys(extras))
    return merged


def deduplicate(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged_by_key: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    ordered_keys: List[Tuple[str, str, str]] = []

    for rec in records:
        key = _dedupe_key(rec)
        if key not in merged_by_key:
            merged_by_key[key] = dict(rec)
            ordered_keys.append(key)
        else:
            merged_by_key[key] = _merge(merged_by_key[key], rec)

    return [merged_by_key[key] for key in ordered_keys]
