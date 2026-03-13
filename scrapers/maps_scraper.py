from __future__ import annotations

import urllib.parse
from typing import Dict, List

from bs4 import BeautifulSoup

from extractors.address_extractor import extract_addresses
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

# DuckDuckGo with location-specific search — no maps API needed
MAPS_SEARCH_URL = "https://html.duckduckgo.com/html/?q={query}+address+contact+location"

DDG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://duckduckgo.com/",
}


def _decode_ddg_href(href: str) -> str:
    """Decode DuckDuckGo redirect URLs to the real destination URL."""
    if href.startswith("//duckduckgo.com/l/?"):
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if "uddg" in parsed:
            return parsed["uddg"][0]
    return href


class MapsScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = MAPS_SEARCH_URL.format(query=urllib.parse.quote_plus(query))
        html = await self.request_manager.fetch(url, headers=DDG_HEADERS)
        soup = BeautifulSoup(html, "lxml")
        results: List[Dict[str, str]] = []

        # DDG HTML result containers — try multiple selectors for robustness
        result_items = (
            soup.select("div.result__body")
            or soup.select("div.results_links_deep")
            or soup.select("div.web-result")
        )

        for div in result_items[:8]:
            title_el = (
                div.select_one("h2.result__title a.result__a")
                or div.select_one("a.result__a")
                or div.select_one("h2 a")
            )
            if not title_el:
                continue

            raw_href = title_el.get("href", "")
            href = _decode_ddg_href(raw_href)

            if not href.startswith("http"):
                continue

            name = title_el.get_text(" ", strip=True)

            # Extract snippet for address/phone hints
            snippet_el = (
                div.select_one("a.result__snippet")
                or div.select_one(".result__snippet")
                or div.select_one("p")
            )
            snippet_text = snippet_el.get_text(" ", strip=True) if snippet_el else ""
            phones = extract_phones(snippet_text)

            # Deep-fetch the result page to extract address details
            address = ""
            profile_data: Dict[str, str] = {}
            if href.startswith("http"):
                try:
                    profile_data = await self.enrich_from_profile(href, "Maps")
                    address = profile_data.get("address", "")
                    if not address:
                        # Try extracting from raw page HTML
                        from utils.request_manager import RequestManager  # noqa: F401
                        addresses_from_snippet = extract_addresses(snippet_text)
                        address = addresses_from_snippet[0] if addresses_from_snippet else ""
                except Exception:
                    pass

            record = self.build_record(
                company_name=name,
                source="maps",
                website=href,
                phone=phones[0] if phones else profile_data.get("phone", ""),
                email=profile_data.get("email", ""),
                address=address,
                description=snippet_text,
                additional_info=f"Location result: {href}",
            )
            results.append(record)

        return results
