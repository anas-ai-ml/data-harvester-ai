from __future__ import annotations

from typing import Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

MAPS_SEARCH_URL = "https://www.google.com/maps/search/{query}"


class MapsScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = MAPS_SEARCH_URL.format(query=quote_plus(query))
        html = await self.request_manager.get_text(url)
        soup = BeautifulSoup(html, "lxml")
        results: List[Dict[str, str]] = []

        for item in soup.find_all("a"):
            name = item.get("aria-label")
            href = item.get("href", "")
            if not name or "/maps/place" not in href:
                continue
            results.append(
                self.build_record(
                    company_name=name,
                    source="maps",
                    additional_info=f"Google Maps listing: {self.absolute_url(url, href)}",
                )
            )
        return results
