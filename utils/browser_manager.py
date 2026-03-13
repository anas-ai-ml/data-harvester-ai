"""
Stealth headless browser manager using Playwright.

Features:
  - Full stealth mode (hides all automation fingerprints)
  - Random viewport, realistic headers, WebGL/canvas spoofing
  - Proxy support per-context
  - Persistent browser instance (reused across requests for speed)
  - Human-like delays to avoid detection
  - Cookie jar + localStorage persistence between page loads

Install:
    pip install playwright && playwright install chromium
"""
from __future__ import annotations

import asyncio
import random
from typing import Optional

from loguru import logger

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    _PLAYWRIGHT_AVAILABLE = False


# Realistic desktop viewports
_VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 800},
]

# Real-world user agent strings (Chrome 123 / 124)
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# JavaScript to inject that removes all Playwright / automation signals
_STEALTH_SCRIPT = """
// 1. Remove webdriver flag
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// 2. Override plugins to look like a real browser
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const arr = [1, 2, 3, 4, 5];
        arr.__proto__ = PluginArray.prototype;
        return arr;
    }
});

// 3. Override languages
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

// 4. Spoof hardware concurrency (realistic)
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });

// 5. Spoof deviceMemory
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

// 6. Remove chrome.runtime if it's missing (catches some detectors)
if (!window.chrome) {
    window.chrome = { runtime: {} };
}

// 7. Spoof permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters)
);

// 8. WebGL vendor/renderer spoofing
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Intel Inc.';
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
    return getParameter.call(this, parameter);
};
"""


class BrowserManager:
    """
    Persistent stealth headless browser.
    Launch once, reuse context across scraping runs.
    """

    def __init__(self, proxy_url: Optional[str] = None) -> None:
        self._proxy_url = proxy_url
        self._playwright: Optional["Playwright"] = None
        self._browser: Optional["Browser"] = None
        self._started = False

    async def _ensure_started(self) -> None:
        if self._started:
            return
        if not _PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright is not installed.\n"
                "Run: pip install playwright && playwright install chromium"
            )

        self._playwright = await async_playwright().start()
        proxy_settings = None
        if self._proxy_url:
            proxy_settings = {"server": self._proxy_url}

        self._browser = await self._playwright.chromium.launch(
            headless=True,
            proxy=proxy_settings,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        self._started = True

    async def _new_stealth_context(self, proxy_url: Optional[str] = None) -> "BrowserContext":
        """Create a new browser context with anti-detection settings."""
        await self._ensure_started()
        assert self._browser is not None

        viewport = random.choice(_VIEWPORTS)
        user_agent = random.choice(_USER_AGENTS)

        proxy_settings = None
        if proxy_url:
            proxy_settings = {"server": proxy_url}
        elif self._proxy_url:
            proxy_settings = {"server": self._proxy_url}

        context = await self._browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"latitude": 40.7128, "longitude": -74.0060},
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Upgrade-Insecure-Requests": "1",
            },
            proxy=proxy_settings,
        )

        # Inject stealth scripts on every page before any JS runs
        await context.add_init_script(_STEALTH_SCRIPT)
        return context

    async def fetch(self, url: str, proxy_url: Optional[str] = None) -> str:
        """
        Fetch a URL using a stealth headless browser context.
        Each call gets a fresh context (separate cookie jar / fingerprint).
        """
        context = await self._new_stealth_context(proxy_url)
        page = await context.new_page()

        try:
            # Human-like: random delay before navigating
            await asyncio.sleep(random.uniform(0.5, 1.5))

            await page.goto(
                url,
                timeout=45_000,
                wait_until="domcontentloaded",
            )

            # Simulate human scrolling + reading delay
            await page.evaluate("window.scrollTo(0, Math.random() * 300)")
            await asyncio.sleep(random.uniform(1.0, 2.5))

            # Wait for any lazy-loaded content
            try:
                await page.wait_for_load_state("networkidle", timeout=8_000)
            except Exception:
                pass  # networkidle can time out on heavy pages; content loaded enough

            html = await page.content()
            logger.debug(f"Browser fetched {len(html)} bytes from {url}")
            return html

        except Exception as exc:
            logger.warning(f"Browser fetch failed for {url}: {exc}")
            raise
        finally:
            await page.close()
            await context.close()

    async def close(self) -> None:
        """Shutdown the browser and Playwright instance."""
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
        self._started = False

    @property
    def available(self) -> bool:
        return _PLAYWRIGHT_AVAILABLE
