from __future__ import annotations

from typing import Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://clutch.co/search?search={query}"


class ClutchScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=quote_plus(query))
        html = await self.request_manager.get_text(url)
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        for card in soup.select("li.provider, div.provider-row")[:25]:
            name_el = card.select_one("h3.company_name a, .provider__title a")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url(url, name_el.get("href"))
            website_el = card.select_one("a.website-link__item, a[href*='visit-website']")
            industry_el = card.select_one(".list-item.block-tagline, .provider__services")
            desc_el = card.select_one(".company_info .field-content, .provider__description")
            profile_data = await self.enrich_from_profile(profile_url, "Clutch")

            record = self.build_record(
                company_name=name,
                website=website_el.get("href") if website_el else "",
                industry=industry_el.get_text(" ", strip=True) if industry_el else "",
                description=desc_el.get_text(" ", strip=True) if desc_el else "",
                additional_info=f"Clutch search query: {query}",
                source="clutch",
            )
            records.append(self.merge_records(record, profile_data))

        return records
