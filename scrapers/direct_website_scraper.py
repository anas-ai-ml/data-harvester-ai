import os
import re
from typing import Dict, List

from bs4 import BeautifulSoup

from extractors.email_extractor import extract_emails
from extractors.phone_extractor import extract_phones
from scrapers.base_scraper import BaseScraper
from utils.firecrawl_client import FirecrawlClient


class DirectWebsiteScraper(BaseScraper):
    async def search_and_extract(self, query: str) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []

        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return results

        urls = self._extract_urls_from_query(query)

        firecrawl = FirecrawlClient(api_key)

        for url in urls[:5]:
            try:
                content = firecrawl.scrape(url)
                if not content:
                    continue

                emails = extract_emails(content)
                phones = extract_phones(content)

                soup = BeautifulSoup(content, "lxml")
                text = soup.get_text(" ", strip=True)

                company_name = self._extract_company_name(text, url)

                record = self.build_record(
                    company_name=company_name,
                    website=url,
                    email=emails[0] if emails else "",
                    phone=phones[0] if phones else "",
                    description=text[:500] if text else "",
                    source="direct_website",
                    additional_info=f"Direct website scrape for: {query}",
                )
                results.append(record)

            except Exception as e:
                continue

        return results

    def _extract_urls_from_query(self, query: str) -> List[str]:
        urls = []

        urls_from_query = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', query)
        if urls_from_query:
            return [u.rstrip(".,;:") for u in urls_from_query[:5]]

        company_name = re.sub(r"[^\w\s]", " ", query).strip()

        search_patterns = [
            f"https://{company_name.replace(' ', '')}.com",
            f"https://www.{company_name.replace(' ', '')}.com",
            f"https://{company_name.replace(' ', '-').lower()}.com",
            f"https://www.{company_name.replace(' ', '-').lower()}.com",
        ]

        for url in search_patterns:
            if url not in urls:
                urls.append(url)

        return urls

    def _extract_company_name(self, text: str, url: str) -> str:
        if not text:
            return ""

        lines = text.split("\n")
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and len(line) < 100:
                if not line.startswith(
                    ("http", "www", "contact", "email", "phone", "address")
                ):
                    return line

        from urllib.parse import urlparse

        domain = urlparse(url).netloc
        company = domain.replace("www.", "").split(".")[0]
        return company.replace("-", " ").title()
