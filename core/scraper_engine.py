from __future__ import annotations

import asyncio
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
        return platforms

    async def _run_platforms_for_term(
        self,
        term: str,
        platforms: Sequence[str],
        request_manager: RequestManager,
    ) -> List[Dict[str, Any]]:
        tasks = []
        platform_names: List[str] = []

        for name in platforms:
            scraper_cls = SCRAPER_REGISTRY.get(name)
            if not scraper_cls:
                logger.warning(f"No scraper registered for platform={name}")
                continue
            scraper = scraper_cls(request_manager=request_manager)
            await scraper.initialize()
            tasks.append(scraper.search_and_extract(term))
            platform_names.append(name)

        results: List[Dict[str, Any]] = []
        if tasks:
            gathered = await asyncio.gather(*tasks, return_exceptions=True)
            for platform_name, out in zip(platform_names, gathered):
                if isinstance(out, Exception):
                    logger.error(f"Scraper error for platform='{platform_name}' query='{term}': {out}")
                    continue
                logger.info(f"Platform '{platform_name}' yielded {len(out)} records for query '{term}'")
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
    ) -> List[Dict[str, Any]]:
        use_discovery = "discovery" in platforms
        use_website = "website" in platforms
        remaining = [p for p in platforms if p not in {"discovery", "website"}]

        results: List[Dict[str, Any]] = []

        discovery_records: List[Dict[str, Any]] = []
        if use_discovery:
            discovery_records = await self._run_platforms_for_term(
                query,
                ["discovery"],
                request_manager,
            )
            results.extend(discovery_records)

        if remaining:
            remaining_records = await self._run_platforms_for_term(
                query,
                remaining,
                request_manager,
            )
            results.extend(remaining_records)

        if use_website:
            website_targets = self._extract_website_targets(discovery_records)
            if website_targets:
                website_batches = [
                    self._run_platforms_for_term(url, ["website"], request_manager)
                    for url in website_targets
                ]
                website_results = await asyncio.gather(*website_batches, return_exceptions=True)
                for url, out in zip(website_targets, website_results):
                    if isinstance(out, Exception):
                        logger.error(f"Website scraping failed for '{url}': {out}")
                        continue
                    results.extend(out)
            else:
                logger.warning(
                    f"No discovered website targets for query '{query}', skipping website scraper"
                )

        return results

    async def run_async(self, queries: Iterable[str]) -> ScraperResult:
        platforms = self._active_platforms()
        all_records: List[Dict[str, Any]] = []
        query_list = list(queries)
        logger.info(f"Queries executed: {len(query_list)}")

        async with RequestManager(proxy_config=self.settings.proxies.__dict__) as rm:
            for query in tqdm_asyncio(query_list, desc="Scraping queries"):
                try:
                    records = await self._run_for_query(query, platforms, rm)
                    logger.info(f"Query '{query}' yielded {len(records)} raw records")
                    all_records.extend(records)
                except Exception as exc:
                    logger.exception(f"Failed to scrape for query='{query}': {exc}")

        return ScraperResult(records=all_records)
