from __future__ import annotations

from typing import Dict, List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from extractors.email_extractor import extract_emails
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://www.indiamart.com/search.mp?ss={query}"


class IndiaMartScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=quote_plus(query))
        html = await self.request_manager.get_text(url)
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        for card in soup.select("div.l-cl.brdwhite.mkcl, div.cardbody")[:25]:
            name_el = card.select_one("a.fs20, a.comp-name, a[data-click='company-name']")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url(url, name_el.get("href"))
            address_el = card.select_one(".fwn.grey-txt.fs12, .company-address, .newLocationUi")
            description_el = card.select_one(".fs13, .company-description, .catalog-desc")
            industry_el = card.select_one(".product-list, .business-type, .catgory_name")
            phone_text = card.get_text(" ", strip=True)

            profile_data = await self.enrich_from_profile(profile_url, "IndiaMART")
            description = description_el.get_text(" ", strip=True) if description_el else ""
            emails = extract_emails(description)
            phones = extract_phones(phone_text)

            record = self.build_record(
                company_name=name,
                website="",
                phone=phones[0] if phones else "",
                email=emails[0] if emails else "",
                address=address_el.get_text(" ", strip=True) if address_el else "",
                industry=industry_el.get_text(" ", strip=True) if industry_el else "",
                description=description,
                additional_info=f"IndiaMART search query: {query}",
                source="indiamart",
            )
            records.append(self.merge_records(record, profile_data))

        return records
