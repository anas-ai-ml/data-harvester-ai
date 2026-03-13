from __future__ import annotations

import urllib.parse
from typing import Dict, List

from bs4 import BeautifulSoup

from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://www.justdial.com/search?type=company&what={query}"


class JustDialScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=urllib.parse.quote_plus(query))
        try:
            html = await self.request_manager.fetch(url)
        except Exception:
            return []
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        for card in soup.select("div.cntanr, div.resultbox_info")[:25]:
            name_el = card.select_one("span.jcn a, .resultbox_title_anchor")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url(url, name_el.get("href"))
            address_el = card.select_one("span.cont_fl_addr, .resultbox_address")
            category_el = card.select_one("span.cate, .resultbox_category")
            phones = extract_phones(card.get_text(" ", strip=True))
            profile_data = await self.enrich_from_profile(profile_url, "JustDial")

            record = self.build_record(
                company_name=name,
                phone=phones[0] if phones else "",
                address=address_el.get_text(" ", strip=True) if address_el else "",
                industry=category_el.get_text(" ", strip=True) if category_el else "",
                industry_type=category_el.get_text(" ", strip=True) if category_el else "",
                description=description_el.get_text(" ", strip=True) if description_el else "",
                additional_info=f"JustDial search query: {query}",
                source="justdial",
            )
            records.append(self.merge_records(record, profile_data))

        return records
