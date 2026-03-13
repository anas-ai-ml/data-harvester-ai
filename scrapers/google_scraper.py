from __future__ import annotations

import urllib.parse
from typing import Dict, List

from bs4 import BeautifulSoup

from extractors.email_extractor import extract_emails
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper

# Using DuckDuckGo HTML — zero bot protection, no JS required
DDG_SEARCH_URL = "https://html.duckduckgo.com/html/?q={query}"

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


class GoogleScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        url = DDG_SEARCH_URL.format(query=urllib.parse.quote_plus(query))
        html = await self.request_manager.fetch(url, headers=DDG_HEADERS)
        soup = BeautifulSoup(html, "lxml")
        results: List[Dict[str, str]] = []

        # DDG HTML result containers — try multiple selectors for robustness
        result_items = (
            soup.select("div.result__body")
            or soup.select("div.results_links_deep")
            or soup.select("div.web-result")
        )

        for div in result_items[:10]:
            # Title/link — try multiple known DDG selectors
            title_el = (
                div.select_one("h2.result__title a.result__a")
                or div.select_one("a.result__a")
                or div.select_one("h2 a")
            )
            if not title_el:
                continue

            raw_href = title_el.get("href") or ""
            href = _decode_ddg_href(raw_href)

            # Skip non-HTTP urls (DDG internal pages, etc.)
            if not href.startswith("http"):
                continue

            company_name = title_el.get_text(" ", strip=True)

            # Description / snippet
            snippet_el = (
                div.select_one("a.result__snippet")
                or div.select_one(".result__snippet")
                or div.select_one("p")
            )
            description = snippet_el.get_text(" ", strip=True) if snippet_el else ""

            # Quick extraction from snippet text
            emails = extract_emails(description)
            phones = extract_phones(description)

            # Deep enrichment: fetch the actual page
            profile_data: Dict[str, str] = {}
            if href.startswith("http"):
                try:
                    profile_data = await self.enrich_from_profile(href, "Search")
                except Exception:
                    pass

            record = self.build_record(
                company_name=company_name,
                website=href,
                description=description,
                email=emails[0] if emails else "",
                phone=phones[0] if phones else "",
                source="google",
                additional_info=f"Search result for query: {query}",
            )
            results.append(self.merge_records(record, profile_data))

        return results
