"""
Rotating proxy manager.

Supports three modes (set via config/proxies.yaml):
  1. pool       — a static list of proxies rotated round-robin per request
  2. webshare   — Webshare.io rotating endpoint (one URL, auto-rotates server-side)
  3. brightdata  — Bright Data (ex-Luminati) super-proxy with session rotation
  4. smartproxy  — SmartProxy rotating residential endpoint
  5. custom     — single custom proxy URL

Configure in config/proxies.yaml and .env:
  PROXY_USERNAME / PROXY_PASSWORD for authenticated services.
"""
from __future__ import annotations

import itertools
import os
import random
from threading import Lock
from typing import Any, Dict, List, Optional


class ProxyPool:
    """Thread-safe rotating proxy pool."""

    def __init__(self, proxies: List[str], strategy: str = "round_robin") -> None:
        self._proxies = proxies
        self._strategy = strategy
        self._lock = Lock()
        self._cycle = itertools.cycle(proxies) if proxies else iter([])

    def get(self) -> Optional[str]:
        if not self._proxies:
            return None
        with self._lock:
            if self._strategy == "random":
                return random.choice(self._proxies)
            return next(self._cycle)  # round_robin


# Module-level pool singleton — configured by _build_pool()
_POOL: Optional[ProxyPool] = None


def _build_pool(proxy_config: Dict[str, Any]) -> Optional[ProxyPool]:
    """Build proxy pool from config dict."""
    if not proxy_config.get("enabled"):
        return None

    strategy = proxy_config.get("rotation_strategy", "round_robin")
    mode = proxy_config.get("mode", "pool")

    # ------------------------------------------------------------------
    # Mode 1: static pool list
    # ------------------------------------------------------------------
    if mode == "pool":
        raw_list: List[str] = proxy_config.get("list", [])
        if not raw_list:
            # Also accept single http/https keys
            http = proxy_config.get("http")
            https = proxy_config.get("https")
            raw_list = [p for p in [http, https] if p]
        if not raw_list:
            return None
        return ProxyPool(raw_list, strategy)

    # ------------------------------------------------------------------
    # Mode 2: Webshare.io rotating endpoint
    #   endpoint: http://proxy.webshare.io:80
    #   credentials from PROXY_USERNAME / PROXY_PASSWORD env vars
    # ------------------------------------------------------------------
    if mode == "webshare":
        endpoint = proxy_config.get("endpoint", "")
        username = proxy_config.get("username") or os.getenv("PROXY_USERNAME", "")
        password = proxy_config.get("password") or os.getenv("PROXY_PASSWORD", "")
        if endpoint and username and password:
            proxy_url = _inject_auth(endpoint, username, password)
            return ProxyPool([proxy_url], "round_robin")
        return None

    # ------------------------------------------------------------------
    # Mode 3: Bright Data super-proxy
    #   endpoint: http://brd.superproxy.io:22225
    #   Rotates to a new IP on each session-id change.
    # ------------------------------------------------------------------
    if mode == "brightdata":
        endpoint = proxy_config.get("endpoint", "http://brd.superproxy.io:22225")
        username = proxy_config.get("username") or os.getenv("PROXY_USERNAME", "")
        password = proxy_config.get("password") or os.getenv("PROXY_PASSWORD", "")
        if username and password:
            # Generate session-rotation pool: 20 unique session IDs
            pool = []
            for i in range(20):
                session_user = f"{username}-session-{i}"
                proxy_url = _inject_auth(endpoint, session_user, password)
                pool.append(proxy_url)
            return ProxyPool(pool, strategy)
        return None

    # ------------------------------------------------------------------
    # Mode 4: SmartProxy rotating residential
    #   endpoint: http://gate.smartproxy.com:7000
    # ------------------------------------------------------------------
    if mode == "smartproxy":
        endpoint = proxy_config.get("endpoint", "http://gate.smartproxy.com:7000")
        username = proxy_config.get("username") or os.getenv("PROXY_USERNAME", "")
        password = proxy_config.get("password") or os.getenv("PROXY_PASSWORD", "")
        if username and password:
            pool = []
            for i in range(20):
                session_user = f"{username}-session-{random.randint(1, 99999)}"
                proxy_url = _inject_auth(endpoint, session_user, password)
                pool.append(proxy_url)
            return ProxyPool(pool, strategy)
        return None

    # ------------------------------------------------------------------
    # Mode 5: single custom proxy URL
    # ------------------------------------------------------------------
    if mode == "custom":
        url = proxy_config.get("url") or proxy_config.get("https") or proxy_config.get("http")
        if url:
            return ProxyPool([url], strategy)

    return None


def _inject_auth(endpoint: str, username: str, password: str) -> str:
    """Inject username:password@ into a proxy URL."""
    if "@" in endpoint:
        return endpoint  # already has auth
    if "://" in endpoint:
        scheme, rest = endpoint.split("://", 1)
        return f"{scheme}://{username}:{password}@{rest}"
    return f"http://{username}:{password}@{endpoint}"


def configure_proxy_pool(proxy_config: Dict[str, Any]) -> None:
    """Call once at startup to initialise the module-level pool."""
    global _POOL
    _POOL = _build_pool(proxy_config)


def get_proxy_for_request(proxy_config: Dict[str, Any]) -> Optional[str]:
    """
    Return the next proxy URL for a request, or None if proxies are disabled.
    Lazily initialises the pool from proxy_config on first call.
    """
    global _POOL
    if _POOL is None:
        _POOL = _build_pool(proxy_config)
    if _POOL is None:
        return None
    return _POOL.get()
