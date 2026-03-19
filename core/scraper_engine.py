from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence, Type

from loguru import logger
from tqdm.asyncio import tqdm_asyncio

from config.settings import Settings
from scrapers.base_scraper import BaseScraper
from scrapers.google_scraper import GoogleScraper
from scrapers.maps_scraper import MapsScraper
from scrapers.website_scraper import WebsiteScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.indiamart_scraper import IndiaMartScraper
from scrapers.tradeindia_scraper import TradeIndiaScraper
from scrapers.justdial_scraper import JustDialScraper
from scrapers.clutch_scraper import ClutchScraper
from scrapers.goodfirms_scraper import GoodFirmsScraper
from utils.request_manager import RequestManager
from scrapers.discovery_scraper import DiscoveryScraper
from scrapers.google_places_scraper import GooglePlacesScraper
from scrapers.searx_scraper import SearxScraper
from scrapers.direct_website_scraper import DirectWebsiteScraper


SCRAPER_REGISTRY: Dict[str, Type[BaseScraper]] = {
    "discovery": DiscoveryScraper,
    "google": GoogleScraper,
    "maps": MapsScraper,
    "website": WebsiteScraper,
    "linkedin": LinkedInScraper,
    "indiamart": IndiaMartScraper,
    "tradeindia": TradeIndiaScraper,
    "justdial": JustDialScraper,
    "clutch": ClutchScraper,
    "goodfirms": GoodFirmsScraper,
    "google_places": GooglePlacesScraper,
    "searx": SearxScraper,
    "direct_website": DirectWebsiteScraper,
}


@dataclass
class ScraperResult:
    records: List[Dict[str, Any]]


class ScraperEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _active_platforms(self) -> Sequence[str]:
        p = self.settings.platforms
        platforms: List[str] = []

        if getattr(p, "discovery", False):
            platforms.append("discovery")
        if p.google:
            platforms.append("google")
        if p.maps:
            platforms.append("maps")
        if p.website:
            platforms.append("website")
        if p.linkedin:
            platforms.append("linkedin")
        if getattr(p, "indiamart", False):
            platforms.append("indiamart")
        if getattr(p, "tradeindia", False):
            platforms.append("tradeindia")
        if getattr(p, "justdial", False):
            platforms.append("justdial")
        if getattr(p, "clutch", False):
            platforms.append("clutch")
        if getattr(p, "goodfirms", False):
            platforms.append("goodfirms")
        if getattr(p, "google_places", False):
            platforms.append("google_places")
        if getattr(p, "searx", False):
            platforms.append("searx")
        if getattr(p, "direct_website", False):
            platforms.append("direct_website")
        return platforms

    async def _run_platforms_for_term(
        self,
        term: str,
        platforms: Sequence[str],
        request_manager: RequestManager,
        step_callback=None,
    ) -> List[Dict[str, Any]]:
        tasks = []
        platform_names: List[str] = []

        for name in platforms:
            scraper_cls = SCRAPER_REGISTRY.get(name)
            if not scraper_cls:
                logger.warning(f"No scraper registered for platform={name}")
                if step_callback:
                    step_callback()
                continue
            scraper = scraper_cls(request_manager=request_manager)
            await scraper.initialize()

            # Helper to bind platform name explicitly to the result
            async def run_task(scr, plt_name, query):
                try:
                    res = await scr.search_and_extract(query)
                    return plt_name, res
                except Exception as e:
                    return plt_name, e

            tasks.append(run_task(scraper, name, term))
            platform_names.append(name)

        results: List[Dict[str, Any]] = []
        if tasks:
            for coro in asyncio.as_completed(tasks):
                platform_name, out = await coro
                if step_callback:
                    step_callback()
                if isinstance(out, Exception):
                    logger.error(
                        f"Scraper error for platform='{platform_name}' query='{term}': {out}"
                    )
                    continue
                logger.info(
                    f"Platform '{platform_name}' yielded {len(out)} records for query '{term}'"
                )
                results.extend(out)

        return results

    @staticmethod
    def _extract_website_targets(records: Sequence[Dict[str, Any]]) -> List[str]:
        seen = set()
        websites: List[str] = []
        for record in records:
            website = str(record.get("website", "")).strip()
            if not website.startswith(("http://", "https://")):
                continue
            if website in seen:
                continue
            seen.add(website)
            websites.append(website)
        return websites

    async def _run_for_query(
        self,
        query: str,
        platforms: Sequence[str],
        request_manager: RequestManager,
        step_callback=None,
    ) -> List[Dict[str, Any]]:
        use_discovery = "discovery" in platforms
        use_website = "website" in platforms
        use_searx = "searx" in platforms
        remaining = [p for p in platforms if p not in {"discovery", "website"}]

        results: List[Dict[str, Any]] = []
        discovery_records: List[Dict[str, Any]] = []

        if use_discovery:
            discovery_records = await self._run_platforms_for_term(
                query, ["discovery"], request_manager, step_callback
            )
            results.extend(discovery_records)
            if not discovery_records:
                logger.warning(f"Discovery scraper returned 0 results for '{query}'")

        if remaining:
            remaining_records = await self._run_platforms_for_term(
                query, remaining, request_manager, step_callback
            )
            results.extend(remaining_records)

        if use_website:
            website_targets = self._extract_website_targets(results)

            if not website_targets:
                if use_discovery or use_searx:
                    logger.warning(
                        f"No websites found from discovery for '{query}', trying direct website scraping..."
                    )

                direct_urls = self._try_direct_search(query)
                if direct_urls:
                    logger.info(f"Found {len(direct_urls)} direct URLs for '{query}'")
                    website_targets.extend(direct_urls)

            if website_targets:
                logger.info(f"Scraping {len(website_targets)} websites for '{query}'")
                website_batches = [
                    self._run_platforms_for_term(
                        url, ["website"], request_manager, step_callback
                    )
                    for url in website_targets[:10]
                ]
                website_results = await asyncio.gather(
                    *website_batches, return_exceptions=True
                )
                for url, out in zip(website_targets[:10], website_results):
                    if isinstance(out, Exception):
                        logger.error(f"Website scraping failed for '{url}': {out}")
                        continue
                    if out:
                        results.extend(out)
                        logger.info(
                            f"Website scraper got {len(out)} records from {url}"
                        )
            else:
                logger.warning(
                    f"No discovered website targets for query '{query}', trying direct website scraper..."
                )

                if "direct_website" in SCRAPER_REGISTRY:
                    direct_results = await self._run_platforms_for_term(
                        query, ["direct_website"], request_manager, step_callback
                    )
                    if direct_results:
                        logger.info(
                            f"Direct website scraper got {len(direct_results)} records"
                        )
                        results.extend(direct_results)
                    else:
                        logger.warning(
                            f"Direct website scraper also returned 0 results for '{query}'"
                        )

                direct_urls = self._try_direct_search(query)
                if direct_urls:
                    logger.info(f"Found {len(direct_urls)} direct URLs for '{query}'")
                    website_targets.extend(direct_urls)

            if website_targets:
                logger.info(f"Scraping {len(website_targets)} websites for '{query}'")
                website_batches = [
                    self._run_platforms_for_term(
                        url, ["website"], request_manager, step_callback
                    )
                    for url in website_targets[:10]
                ]
                website_results = await asyncio.gather(
                    *website_batches, return_exceptions=True
                )
                for url, out in zip(website_targets[:10], website_results):
                    if isinstance(out, Exception):
                        logger.error(f"Website scraping failed for '{url}': {out}")
                        continue
                    if out:
                        results.extend(out)
                        logger.info(
                            f"Website scraper got {len(out)} records from {url}"
                        )
            else:
                logger.warning(
                    f"No discovered website targets for query '{query}', skipping website scraper"
                )

        return results

    def _try_direct_search(self, query: str) -> List[str]:
        urls = []

        company_name = re.sub(r"[^\w\s]", " ", query).strip()
        company_name_clean = company_name.replace(" ", "").lower()

        common_tlds = [".com", ".co.in", ".in", ".org", ".net"]

        for tld in common_tlds:
            url = f"https://www.{company_name_clean}{tld}"
            urls.append(url)

        hyphenated = company_name.replace(" ", "-").lower()
        for tld in [".com", ".co.in"]:
            url = f"https://{hyphenated}{tld}"
            if url not in urls:
                urls.append(url)

        return list(dict.fromkeys(urls))[:5]

    async def run_async(
        self, queries: Iterable[str], progress_callback=None
    ) -> ScraperResult:
        platforms = self._active_platforms()
        all_records: List[Dict[str, Any]] = []
        query_list = list(queries)
        total_queries = len(query_list)
        logger.info(f"Queries executed: {total_queries}")

        total_steps = len(platforms) * total_queries
        steps_done = 0

        def step_callback():
            nonlocal steps_done
            steps_done += 1
            if progress_callback and total_steps > 0:
                # Max progress goes dynamically from 15% -> 85% as steps finish
                current_progress = 15 + int((steps_done / total_steps) * 70)
                progress_callback(min(current_progress, 84))

        async with RequestManager(proxy_config=self.settings.proxies.__dict__) as rm:
            for idx, query in enumerate(
                tqdm_asyncio(query_list, desc="Scraping queries")
            ):
                try:
                    records = await self._run_for_query(
                        query, platforms, rm, step_callback
                    )
                    logger.info(f"Query '{query}' yielded {len(records)} raw records")
                    all_records.extend(records)
                except Exception as exc:
                    logger.exception(f"Failed to scrape for query='{query}': {exc}")

        return ScraperResult(records=all_records)
