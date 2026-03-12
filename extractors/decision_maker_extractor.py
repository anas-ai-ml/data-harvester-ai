from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup


ROLE_KEYWORDS = [
    "ceo",
    "founder",
    "co-founder",
    "cto",
    "cfo",
    "director",
    "head of it",
    "it head",
    "finance head",
    "chief technology officer",
    "chief financial officer",
    "managing director",
]
NAME_PATTERN = re.compile(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})")


def extract_decision_makers(html: str) -> List[str]:
    soup = BeautifulSoup(html or "", "lxml")
    candidates: List[str] = []

    for tag in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "span", "div"]):
        text = " ".join(tag.get_text(separator=" ", strip=True).split())
        if not text:
            continue
        lower = text.lower()
        if any(keyword in lower for keyword in ROLE_KEYWORDS):
            name_match = NAME_PATTERN.search(text)
            if name_match:
                candidates.append(f"{name_match.group(1)} ({text})")
            else:
                candidates.append(text)

    seen = set()
    unique: List[str] = []
    for item in candidates:
        normalized = item.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(item)
    return unique
