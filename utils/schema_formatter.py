from __future__ import annotations

from typing import Any, Dict, Iterable, List


OUTPUT_FIELDS = [
    "SL No.",
    "Company Name",
    "Website",
    "Owner/ IT Head/ CEO/Finance Head Name",
    "Phone Number",
    "EMail Address",
    "Address",
    "Industry_Type",
    "Employee _No",
    "Branch/ Warehouse _No",
    "Annual_Turnover",
    "Current_Use_ERP Software_Name",
    "Additional_Information",
]


def to_output_schema(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for idx, rec in enumerate(records, start=1):
        mapped: Dict[str, str] = {
            "SL No.": str(idx),
            "Company Name": str(rec.get("company_name") or rec.get("name") or ""),
            "Website": str(rec.get("website") or ""),
            "Owner/ IT Head/ CEO/Finance Head Name": str(rec.get("decision_maker") or ""),
            "Phone Number": str(rec.get("phone") or ""),
            "EMail Address": str(rec.get("email") or ""),
            "Address": str(rec.get("address") or ""),
            "Industry_Type": str(rec.get("industry_type") or rec.get("industry") or ""),
            "Employee _No": str(rec.get("employee_no") or ""),
            "Branch/ Warehouse _No": str(rec.get("branch_no") or ""),
            "Annual_Turnover": str(rec.get("annual_turnover") or ""),
            "Current_Use_ERP Software_Name": str(rec.get("current_erp") or ""),
            "Additional_Information": str(rec.get("additional_info") or rec.get("description") or ""),
        }
        result.append(mapped)
    return result
