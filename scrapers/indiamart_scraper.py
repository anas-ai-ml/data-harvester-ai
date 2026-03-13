from __future__ import annotations

import urllib.parse
from typing import Dict, List

from bs4 import BeautifulSoup
from loguru import logger

from extractors.email_extractor import extract_emails
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://www.indiamart.com/search.mp?ss={query}"


class IndiaMartScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = SEARCH_URL.format(query=urllib.parse.quote_plus(query))
        try:
            html = await self.request_manager.fetch(url)
        except Exception as exc:
            logger.warning(f"IndiaMart search fetch failed for '{query}': {exc}")
            return []
            
        soup = BeautifulSoup(html, "lxml")
        records: List[Dict[str, str]] = []

        for card in soup.select("div.l-cl.brdwhite.mkcl, div.cardbody")[:10]:
            name_el = card.select_one("a.fs20, a.comp-name, a[data-click='company-name']")
            if not name_el:
                continue
            name = name_el.get_text(" ", strip=True)
            profile_url = self.absolute_url("https://www.indiamart.com", name_el.get("href"))
            address_el = card.select_one(".fwn.grey-txt.fs12, .company-address, .newLocationUi")
            description_el = card.select_one(".fs13, .company-description, .catalog-desc")
            industry_el = card.select_one(".product-list, .business-type, .catgory_name")
            phone_text = card.get_text(" ", strip=True)

            description = description_el.get_text(" ", strip=True) if description_el else ""
            emails = extract_emails(description)
            phones = extract_phones(phone_text)
            
            # Additional variables
            employee_no = ""
            annual_turnover = ""
            industry_type = industry_el.get_text(" ", strip=True) if industry_el else ""

            profile_data = {}
            if profile_url:
                try:
                    # Enrich from base generic methodology
                    profile_data = await self.enrich_from_profile(profile_url, "IndiaMART")
                    
                    # Also scrape the profile directly for specific TradeIndia-like facts
                    profile_html = await self.request_manager.fetch(profile_url)
                    p_soup = BeautifulSoup(profile_html, "lxml")
                    
                    # IndiaMart often places data in tables or definition lists
                    for tr in p_soup.select("tr, li, div.factsheet div, div.row"):
                        text = tr.get_text(" ", strip=True).lower()
                        # Extract Employee Count
                        if "number of employees" in text or "total employees" in text:
                            tds = tr.select("td, span, div")
                            if len(tds) > 1:
                                employee_no = tds[-1].get_text(" ", strip=True)
                            else:
                                employee_no = text.split("employees")[-1].strip(" :|-")
                        
                        # Extract Turnover
                        if "annual turnover" in text or "turnover" in text:
                            tds = tr.select("td, span, div")
                            if len(tds) > 1:
                                annual_turnover = tds[-1].get_text(" ", strip=True)
                            else:
                                annual_turnover = text.split("turnover")[-1].split("gst")[0].strip(" :|-")
                                
                        # Update Industry Type if better one found
                        if "nature of business" in text or "company type" in text:
                            tds = tr.select("td, span, div")
                            if len(tds) > 1:
                                industry_type = tds[-1].get_text(" ", strip=True)

                except Exception as exc:
                    logger.debug(f"Failed to extract specific profile details from {profile_url}: {exc}")

            record = self.build_record(
                company_name=name,
                website="",
                phone=phones[0] if phones else "",
                email=emails[0] if emails else "",
                address=address_el.get_text(" ", strip=True) if address_el else "",
                industry=industry_type,
                industry_type=industry_type,
                employee_no=employee_no,
                annual_turnover=annual_turnover,
                description=description,
                additional_info=f"IndiaMart result for: {query}",
                source="indiamart",
            )
            records.append(self.merge_records(record, profile_data))

        return records
