from __future__ import annotations

import urllib.parse
from typing import Dict, List, Any

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

# Search DuckDuckGo for LinkedIn company pages as a discovery step
LINKEDIN_DDG_URL = "https://html.duckduckgo.com/html/?q=site:linkedin.com/company+{query}"

# Fallback: search Google for LinkedIn profiles via DDG
LINKEDIN_GOOGLE_URL = "https://html.duckduckgo.com/html/?q={query}+company+linkedin+profile+email+phone"


class LinkedInScraper(BaseScraper):
    """
    LinkedIn scraper with two-stage approach:
    1. Find LinkedIn company URLs via DuckDuckGo and parse their true names.
    2. Try to enrich each LinkedIn profile (via Stealth Browser).
    """

    async def search_and_extract(self, query: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        # Stage 1: discover LinkedIn company URLs via DDG
        profiles = await self._find_linkedin_profiles(query)

        if profiles:
            # Stage 2: try to enrich each LinkedIn profile
            for profile in profiles[:5]:
                url = profile["url"]
                exact_name = profile["name"]
                
                try:
                    # Uses stealth browser under the hood
                    profile_data = await self.enrich_from_profile(url, "LinkedIn")
                except Exception:
                    profile_data = {}

                # If LinkedIn blocked us (empty result), do a web fallback
                if not profile_data or not any(profile_data.values()):
                    profile_data = await self._web_fallback(url, query)

                # Name fallback hierarchy: DDG Title -> Enriched description -> Slug
                company_name = exact_name or (
                    profile_data.get("description", "").split("|")[0].strip()
                    or urllib.parse.urlparse(url).path.split("/")[-1].replace("-", " ").title()
                )

                # Fix company_type (industry) if available
                industry = profile_data.get("industry_type") or profile_data.get("industry") or "B2B LinkedIn Company"

                record = self.build_record(
                    company_name=company_name,
                    decision_maker=profile_data.get("decision_maker", ""),
                    website=profile_data.get("website", ""),
                    address=profile_data.get("address", ""),
                    industry=industry,
                    industry_type=profile_data.get("industry_type", ""),
                    description=profile_data.get("description", profile["snippet"]),
                    email=profile_data.get("email", ""),
                    phone=profile_data.get("phone", ""),
                    source="linkedin",
                    additional_info=profile_data.get(
                        "additional_info", f"LinkedIn company profile: {url}"
                    ),
                )
                results.append(record)
        else:
            # No LinkedIn profiles found — do a general web search for the query
            fallback = await self._general_web_search(query)
            results.extend(fallback)

        return results

    async def _find_linkedin_profiles(self, query: str) -> List[Dict[str, str]]:
        """Use DuckDuckGo to discover LinkedIn company page URLs and their real names."""
        search_url = LINKEDIN_DDG_URL.format(query=urllib.parse.quote_plus(query))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
        }
        try:
            # request_manager.fetch replaces get_text, supporting headers implicitly
            html = await self.request_manager.fetch(search_url, headers=headers)
        except Exception:
            return []

        soup = BeautifulSoup(html, "lxml")
        profiles: List[Dict[str, str]] = []
        seen_urls = set()

        # Parse DuckDuckGo results robustly
        for div in soup.select("div.result__body")[:5]:
            anchor = div.select_one("a.result__url, a.result__a, h2.result__title a")
            if not anchor:
                continue
                
            href = anchor.get("href") or ""
            # Decode DDG redirect URLs
            if href.startswith("//duckduckgo.com/l/?uddg="):
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                if "uddg" in parsed:
                    href = parsed["uddg"][0]

            if "linkedin.com/company" in href and href not in seen_urls:
                seen_urls.add(href)
                # True company name is usually before the pipe in the DDG Title
                title_el = div.select_one("h2.result__title a")
                name = title_el.get_text(" ", strip=True) if title_el else ""
                
                # Strip generic linkedin branding
                if " | LinkedIn" in name:
                    name = name.split(" | LinkedIn")[0].strip()
                elif " - LinkedIn" in name:
                    name = name.split(" - LinkedIn")[0].strip()
                
                snippet_el = div.select_one("a.result__snippet")
                snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
                
                profiles.append({"url": href, "name": name, "snippet": snippet})

        return profiles

    async def _web_fallback(self, linkedin_url: str, query: str) -> Dict[str, Any]:
        """When LinkedIn blocks us, search the web for the company's contact info."""
        slug = linkedin_url.rstrip("/").split("/")[-1].replace("-", " ")
        search_url = LINKEDIN_GOOGLE_URL.format(
            query=urllib.parse.quote_plus(f"{slug} {query}")
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
        }
        try:
            html = await self.request_manager.fetch(search_url, headers=headers)
        except Exception:
            return {}

        soup = BeautifulSoup(html, "lxml")
        for anchor in soup.select("a.result__url, a.result__a")[:3]:
            href = anchor.get("href") or ""
            if href.startswith("//duckduckgo.com/l/?uddg="):
                parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                if "uddg" in parsed_qs:
                    href = parsed_qs["uddg"][0]
            if href.startswith("http") and "linkedin.com" not in href:
                try:
                    data = await self.enrich_from_profile(href, "LinkedIn-Fallback")
                    if data and any(data.values()):
                        return data
                except Exception:
                    continue
        return {}

    async def _general_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Final fallback: run a general DDG search and return basic records."""
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query + ' company contact')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
        }
        results = []
        try:
            html = await self.request_manager.fetch(search_url, headers=headers)
            soup = BeautifulSoup(html, "lxml")
            for div in soup.select("div.result__body")[:5]:
                title_el = div.select_one("h2.result__title a")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                if href.startswith("//duckduckgo.com/l/?uddg="):
                    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    if "uddg" in parsed_qs:
                        href = parsed_qs["uddg"][0]
                snippet_el = div.select_one("a.result__snippet")
                description = snippet_el.get_text(" ", strip=True) if snippet_el else ""
                
                name = title_el.get_text(" ", strip=True)
                results.append(
                    self.build_record(
                        company_name=name,
                        website=href if href.startswith("http") else "",
                        description=description,
                        source="linkedin_general_search",
                        additional_info=f"Web search fallback for: {query}",
                    )
                )
        except Exception:
            pass
        return results
