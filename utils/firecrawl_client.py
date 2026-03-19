import os
import requests
from loguru import logger

from config.env_config import config


class FirecrawlClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or config.firecrawl_api_key
        self.base_url = "https://api.firecrawl.dev/v1"

    def scrape(self, url):
        if not self.api_key:
            logger.error("Firecrawl API key not configured")
            return ""

        if not url or not url.startswith(("http://", "https://")):
            logger.warning(f"Invalid URL for Firecrawl: {url}")
            return ""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                f"{self.base_url}/scrape",
                headers=headers,
                json={
                    "url": url,
                    "formats": ["markdown", "html"],
                    "onlyMainContent": True,
                },
                timeout=30,
            )

            if response.status_code == 401:
                logger.error("Firecrawl: Invalid API key")
                return ""
            elif response.status_code == 402:
                logger.error("Firecrawl: Insufficient credits")
                return ""
            elif response.status_code == 429:
                logger.warning("Firecrawl: Rate limited")
                return ""

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                markdown = data.get("data", {}).get("markdown", "")
                if markdown:
                    logger.info(f"Firecrawl scraped {len(markdown)} chars from {url}")
                return markdown

            logger.warning(
                f"Firecrawl scrape failed: {data.get('error', 'Unknown error')}"
            )
            return ""

        except requests.exceptions.Timeout:
            logger.error(f"Firecrawl timeout for {url}")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Firecrawl request error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Firecrawl error: {e}")
            return ""
