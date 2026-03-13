"""
Google Places API scraper — official API, zero bot-blocking risk.

Uses the Places API (Text Search) to find businesses, then the
Place Details endpoint to get phone, website, address, and opening hours.

Requirements:
  - GOOGLE_API_KEY environment variable (or set via .env)
  - Enable "Places API" in Google Cloud Console
  - Free tier: 1,000 requests/day; paid: ~$0.017/request

Docs: https://developers.google.com/maps/documentation/places/web-service
"""
from __future__ import annotations

import os
import urllib.parse
from typing import Any, Dict, List, Optional

from loguru import logger

from scrapers.base_scraper import BaseScraper


_PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


class GooglePlacesScraper(BaseScraper):
    """
    Searches Google Places API for businesses matching a query.
    Returns up to 20 results per query (API limit per page).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")

    async def search_and_extract(self, query: str) -> List[Dict[str, Any]]:
        if not self._api_key:
            logger.warning(
                "GOOGLE_API_KEY not set — skipping Google Places scraper. "
                "Add GOOGLE_API_KEY=your_key to .env to enable."
            )
            return []

        # Step 1: Text Search — find matching places
        search_params = urllib.parse.urlencode({
            "query": query,
            "key": self._api_key,
            "type": "establishment",
        })
        search_url = f"{_PLACES_TEXT_SEARCH_URL}?{search_params}"

        try:
            raw_json = await self.request_manager.fetch(
                search_url,
                headers={"Accept": "application/json"},
            )
        except Exception as exc:
            logger.error(f"Places API text search failed for '{query}': {exc}")
            return []

        import json
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            logger.error(f"Places API returned non-JSON for '{query}'")
            return []

        status = data.get("status", "UNKNOWN")
        if status not in ("OK", "ZERO_RESULTS"):
            logger.warning(f"Places API status={status} for query='{query}'")
            return []

        results: List[Dict[str, Any]] = []
        places = data.get("results", [])[:10]  # Cap at 10 to manage quota

        for place in places:
            place_id = place.get("place_id", "")
            record = await self._get_place_details(place_id, place, query)
            if record:
                results.append(record)

        logger.info(f"Google Places API: '{query}' → {len(results)} records")
        return results

    async def _get_place_details(
        self,
        place_id: str,
        basic: Dict[str, Any],
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch full place details for richer data (phone, website, etc.)."""
        if not place_id:
            return self._build_from_basic(basic, query)

        detail_params = urllib.parse.urlencode({
            "place_id": place_id,
            "key": self._api_key,
            "fields": (
                "name,formatted_address,formatted_phone_number,"
                "website,rating,business_status,types,"
                "opening_hours,url"
            ),
        })
        detail_url = f"{_PLACES_DETAILS_URL}?{detail_params}"

        try:
            import json
            raw = await self.request_manager.fetch(
                detail_url,
                headers={"Accept": "application/json"},
            )
            detail_data = json.loads(raw)
            result = detail_data.get("result", {})
        except Exception as exc:
            logger.debug(f"Places details fetch failed for {place_id}: {exc}")
            return self._build_from_basic(basic, query)

        name = result.get("name") or basic.get("name", "")
        address = result.get("formatted_address") or basic.get("formatted_address", "")
        phone = result.get("formatted_phone_number", "")
        website = result.get("website", "")
        rating = result.get("rating", "")
        types = result.get("types", [])
        maps_url = result.get("url", "")

        industry = _infer_industry(types)

        return self.build_record(
            company_name=name,
            address=address,
            phone=phone,
            website=website,
            industry=industry,
            source="google_places",
            description=f"Google Places result | Rating: {rating} | Types: {', '.join(types[:3])}",
            additional_info=f"Google Maps: {maps_url} | Query: {query} | Place ID: {place_id}",
        )

    def _build_from_basic(self, place: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Fallback when details fetch fails — use basic search result fields."""
        name = place.get("name", "")
        address = place.get("formatted_address", "")
        types = place.get("types", [])
        rating = place.get("rating", "")
        return self.build_record(
            company_name=name,
            address=address,
            industry=_infer_industry(types),
            source="google_places",
            description=f"Google Places | Rating: {rating}",
            additional_info=f"Query: {query}",
        )


def _infer_industry(types: List[str]) -> str:
    """Map Google Places types to human-readable industry labels."""
    mapping = {
        "restaurant": "Food & Beverage",
        "food": "Food & Beverage",
        "store": "Retail",
        "health": "Healthcare",
        "hospital": "Healthcare",
        "doctor": "Healthcare",
        "school": "Education",
        "university": "Education",
        "real_estate_agency": "Real Estate",
        "lawyer": "Legal Services",
        "accounting": "Finance",
        "bank": "Banking & Finance",
        "insurance_agency": "Insurance",
        "car_dealer": "Automotive",
        "lodging": "Hospitality",
        "hotel": "Hospitality",
        "gym": "Fitness & Wellness",
        "spa": "Beauty & Wellness",
        "travel_agency": "Travel",
        "it_company": "Information Technology",
        "software": "Information Technology",
        "manufacturer": "Manufacturing",
        "logistics": "Logistics",
        "construction": "Construction",
    }
    for place_type in types:
        for key, label in mapping.items():
            if key in place_type:
                return label
    return types[0].replace("_", " ").title() if types else ""
