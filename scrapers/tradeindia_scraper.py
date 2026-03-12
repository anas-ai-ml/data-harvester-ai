from __future__ import annotations

from typing import Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://www.tradeindia.com/search.html?search_text={query}"


class TradeIndiaScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=quote_plus(query))
        html = await self.request_manager.get_text(url)
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        for card in soup.select("div.listing_product, div.prod-list")[:25]:
            name_el = card.select_one("a.title, h2 a, .company-name a")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url(url, name_el.get("href"))
            address_el = card.select_one(".listing_address, .seller-address")
            category_el = card.select_one(".listing_category, .business-type")
            description_el = card.select_one(".product-description, .listing_desc")
            phones = extract_phones(card.get_text(" ", strip=True))
            profile_data = await self.enrich_from_profile(profile_url, "TradeIndia")

            record = self.build_record(
                company_name=name,
                phone=phones[0] if phones else "",
                address=address_el.get_text(" ", strip=True) if address_el else "",
                industry=category_el.get_text(" ", strip=True) if category_el else "",
                description=description_el.get_text(" ", strip=True) if description_el else "",
                additional_info=f"TradeIndia search query: {query}",
                source="tradeindia",
            )
            records.append(self.merge_records(record, profile_data))

        return records
