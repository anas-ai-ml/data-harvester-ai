from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup


ADDRESS_PATTERN = re.compile(
    r"\b\d+[\w\-,./ ]{5,}(street|st\.|road|rd\.|avenue|ave\.|boulevard|blvd\.|lane|ln\.|sector|suite|floor|industrial area|park|city|state|zip|postal)\b",
    re.IGNORECASE,
)


def extract_addresses(html: str) -> List[str]:
    soup = BeautifulSoup(html or "", "lxml")
    candidates: List[str] = []

    for tag in soup.find_all(["address", "p", "div", "span", "li"]):
        text = " ".join(tag.get_text(separator=" ", strip=True).split())
        if not text:
            continue
        classes = " ".join(tag.get("class", []))
        if tag.name == "address" or any(key in classes.lower() for key in ["address", "location", "contact"]):
            candidates.append(text)
        elif ADDRESS_PATTERN.search(text):
            candidates.append(text)

    seen = set()
    unique: List[str] = []
    for item in candidates:
        normalized = item.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(item)
    return unique
