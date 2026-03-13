from __future__ import annotations

import urllib.parse
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


GOODFIRMS_SEARCH_URL = "https://www.goodfirms.co/companies/search?search={query}"
GOODFIRMS_DIRECTORY = "https://www.goodfirms.co/directory/software-development-companies"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


class GoodFirmsScraper(BaseScraper):

    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        # Try search-based URL first, fall back to directory
        search_url = GOODFIRMS_SEARCH_URL.format(query=urllib.parse.quote_plus(query))
        try:
            html = await self.request_manager.fetch(search_url, headers=HEADERS)
        except Exception:
            html = await self.request_manager.fetch(GOODFIRMS_DIRECTORY, headers=HEADERS)

        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        # Use targeted selectors for GoodFirms cards
        cards = (
            soup.select("div.company-info, div.cl-detail-tile, li.company-list-item")
            or soup.select("div.company")
            or soup.select("article")
        )

        for card in cards[:20]:
            # Try common selectors for company name link
            name_el = (
                card.select_one("h3 a, h2 a, .company-name a")
                or card.select_one("a[href*='/companies/']")
            )
            if not name_el:
                continue

            name = name_el.get_text(" ", strip=True)
            if not name:
                continue

            profile_url = urljoin(GOODFIRMS_DIRECTORY, name_el.get("href", ""))

            desc_el = card.select_one("p, .tagline, .company-desc")
            description = desc_el.get_text(" ", strip=True) if desc_el else ""

            # Try to get industry tag
            industry_el = card.select_one(".service-focus, .focus-areas, .categories")
            industry = industry_el.get_text(" ", strip=True) if industry_el else "Software Development"

            # Deep enrichment from profile page
            profile_data: Dict[str, str] = {}
            if profile_url and profile_url != GOODFIRMS_DIRECTORY:
                try:
                    profile_data = await self.enrich_from_profile(profile_url, "GoodFirms")
                except Exception:
                    pass

            record = self.build_record(
                company_name=name,
                website="",
                industry=industry,
                industry_type=industry,
                description=description,
                source="goodfirms",
                additional_info=f"GoodFirms result. Original query: {query}",
            )

            records.append(self.merge_records(record, profile_data))

        return records