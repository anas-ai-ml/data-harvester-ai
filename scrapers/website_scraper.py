from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup

from extractors.address_extractor import extract_addresses
from extractors.decision_maker_extractor import extract_decision_makers
from extractors.email_extractor import extract_emails
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper


class WebsiteScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        if "http://" not in query and "https://" not in query:
            return []

        html = await self.request_manager.get_text(query)
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)
        title = soup.title.get_text(" ", strip=True) if soup.title else query
        emails = extract_emails(text)
        phones = extract_phones(text)
        addresses = extract_addresses(html)
        decisions = extract_decision_makers(html)

        return [
            self.build_record(
                company_name=title,
                website=query,
                email=emails[0] if emails else "",
                phone=phones[0] if phones else "",
                address=addresses[0] if addresses else "",
                decision_maker=decisions[0] if decisions else "",
                description=text[:500],
                source="website",
                additional_info=f"Website scrape: {query}",
            )
        ]
