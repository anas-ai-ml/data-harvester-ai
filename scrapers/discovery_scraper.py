from __future__ import annotations

import urllib.parse
from typing import Dict, List

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


SEARCH_URL = "https://www.bing.com/search?q={query}"


class DiscoveryScraper(BaseScraper):

    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:

        url = SEARCH_URL.format(query=urllib.parse.quote_plus(query))

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        html = await self.request_manager.fetch(url, headers=headers)

        soup = BeautifulSoup(html, "lxml")

        records: List[Dict[str, str]] = []

        for result in soup.select("li.b_algo")[:15]:
            # Extract human-readable title from the anchor text
            title_el = result.select_one("h2 a")
            if not title_el:
                continue

            href = title_el.get("href", "")
            if not href or "bing.com" in href:
                continue

            # Use the anchor text as the company name (human-readable)
            company_name = title_el.get_text(" ", strip=True)

            # Fall back to the domain name if title is useless
            if not company_name or len(company_name) < 2:
                domain = urllib.parse.urlparse(href).netloc
                company_name = domain.replace("www.", "")

            # Extract snippet/description
            snippet_el = result.select_one("p, .b_caption p")
            description = snippet_el.get_text(" ", strip=True) if snippet_el else ""

            record = self.build_record(
                company_name=company_name,
                website=href,
                description=description or f"Discovered via search query: {query}",
                source="discovery",
                additional_info="Search engine discovery",
            )

            records.append(record)

        return records