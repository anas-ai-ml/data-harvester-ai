from __future__ import annotations

from typing import Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://www.goodfirms.co/companies/search?search={query}"


class GoodFirmsScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=quote_plus(query))
        html = await self.request_manager.get_text(url)
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        for card in soup.select("div.list-item-bx, div.company-card")[:25]:
            name_el = card.select_one("h3 a, .company-card-title a")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url(url, name_el.get("href"))
            website_el = card.select_one("a.visit-website, a[href*='visit-website']")
            desc_el = card.select_one("p.service-des, .company-card-description")
            industry_el = card.select_one("div.services span, .company-card-services")
            profile_data = await self.enrich_from_profile(profile_url, "GoodFirms")

            record = self.build_record(
                company_name=name,
                website=website_el.get("href") if website_el else "",
                industry=industry_el.get_text(" ", strip=True) if industry_el else "",
                description=desc_el.get_text(" ", strip=True) if desc_el else "",
                additional_info=f"GoodFirms search query: {query}",
                source="goodfirms",
            )
            records.append(self.merge_records(record, profile_data))

        return records
