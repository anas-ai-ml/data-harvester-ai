from __future__ import annotations

from typing import Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from extractors.email_extractor import extract_emails
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

GOOGLE_SEARCH_URL = "https://www.google.com/search?q={query}"


class GoogleScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = GOOGLE_SEARCH_URL.format(query=quote_plus(query))
        html = await self.request_manager.get_text(url)
        soup = BeautifulSoup(html, "lxml")
        results: List[Dict[str, str]] = []

        for div in soup.select("div.g")[:10]:
            title_el = div.select_one("h3")
            link_el = div.select_one("a[href]")
            if not title_el or not link_el:
                continue

            href = link_el.get("href") or ""
            description_el = div.select_one("span.aCOpRe, div.VwiC3b")
            description = description_el.get_text(" ", strip=True) if description_el else ""
            emails = extract_emails(description)
            phones = extract_phones(description)
            profile_data = {}
            if href.startswith("http"):
                profile_data = await self.enrich_from_profile(href, "Google")

            record = self.build_record(
                company_name=title_el.get_text(" ", strip=True),
                website=href,
                description=description,
                email=emails[0] if emails else "",
                phone=phones[0] if phones else "",
                source="google",
                additional_info=f"Google result for query: {query}",
            )
            results.append(self.merge_records(record, profile_data))

        return results
