from __future__ import annotations

import urllib.parse
from typing import Dict, List

from bs4 import BeautifulSoup
from loguru import logger

from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://www.tradeindia.com/search.html?search_text={query}"


class TradeIndiaScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=urllib.parse.quote_plus(query))
        
        try:
            # Use fetch() which intelligently leverages the stealth browser
            html = await self.request_manager.fetch(url)
        except Exception as exc:
            logger.warning(f"TradeIndia search failed for '{query}': {exc}")
            return []

        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        # Trade India's card selectors
        for card in soup.select("div.listing_product, div.prod-list, div[data-testid='seller-card']")[:10]:
            name_el = card.select_one("a.title, h2 a, .company-name a, a[data-testid='seller-name']")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url(url, name_el.get("href"))
            address_el = card.select_one(".listing_address, .seller-address, [data-testid='seller-city']")
            category_el = card.select_one(".listing_category, .business-type, [data-testid='seller-nature']")
            description_el = card.select_one(".product-description, .listing_desc")

            # Try to grab employee and turnover stats from the card text
            card_text = card.get_text(" ", strip=True)
            phones = extract_phones(card_text)
            
            # Often displayed in stats/tags on the card
            employee_no = ""
            turnover = ""
            if "Employees :" in card_text or "Employees:" in card_text:
                parts = card_text.split("Employees", 1)[1].strip(" :").split(" ")
                if parts:
                    employee_no = parts[0]
            if "Turnover :" in card_text or "Turnover:" in card_text:
                # E.g. Turnover : 100 - 500 Crore
                try:
                    turnover = card_text.split("Turnover", 1)[1].strip(" :").split("|")[0].strip()
                    # cut off at the next stat if any
                    turnover = turnover.split("Employees")[0].split("Gst")[0].strip()
                except Exception:
                    pass

            # Try fetching profile if stealth browser is working well
            profile_data = {}
            if profile_url and profile_url != url:
                try:
                    profile_html = await self.request_manager.fetch(profile_url)
                    p_soup = BeautifulSoup(profile_html, "lxml")
                    p_text = p_soup.get_text(" ", strip=True)
                    
                    # Look for details table in the profile
                    for row in p_soup.select("tr"):
                        row_text = row.get_text(" ", strip=True).lower()
                        if "number of employees" in row_text or "total employees" in row_text:
                            tds = row.select("td")
                            if len(tds) > 1:
                                employee_no = tds[1].get_text(strip=True)
                        if "annual turnover" in row_text:
                            tds = row.select("td")
                            if len(tds) > 1:
                                turnover = tds[1].get_text(strip=True)
                        if "nature of business" in row_text or "company type" in row_text:
                            tds = row.select("td")
                            if len(tds) > 1:
                                profile_data["industry_type"] = tds[1].get_text(strip=True)

                    if not profile_data.get("phone"):
                        p_phones = extract_phones(p_text)
                        if p_phones:
                            profile_data["phone"] = p_phones[0]
                except Exception:
                    pass

            record = self.build_record(
                company_name=name,
                phone=phones[0] if phones else "",
                address=address_el.get_text(" ", strip=True) if address_el else "",
                industry=category_el.get_text(" ", strip=True) if category_el else profile_data.get("industry_type", ""),
                industry_type=profile_data.get("industry_type", ""),
                description=description_el.get_text(" ", strip=True) if description_el else "",
                employee_no=employee_no,
                annual_turnover=turnover,
                additional_info=f"TradeIndia search query: {query}",
                source="tradeindia",
            )
            records.append(self.merge_records(record, profile_data))

        return records
