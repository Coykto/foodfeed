from typing import Dict

import requests
from .config.settings import settings


class Wolt:

    def get_venues(self, latitude: float, longitude: float) -> Dict:
        return requests.get(
            settings.VENUES_ENDPOINT,
            params={
                "lat": latitude,
                "lon": longitude,
                "language": "en"
            }
        ).json()["sections"][1]["items"]

    def categories(self, venue_slug):
        return requests.get(
            f"{settings.WOLT_API_BASE}{settings.VENUE_CATEGORIES_URI.format(venue=venue_slug)}",
            params={
                "unit_prices": True,
                "show_weighted_items": True,
                "show_subcategories": True,
                "language": "en"
            }
        ).json()["categories"]

    def menu_items(self, venue_slug, category_slug):
        return requests.get(
            f"{settings.WOLT_API_BASE}{settings.VENUE_MENU_URI.format(venue=venue_slug, category=category_slug)}",
            params={
                "unit_prices": True,
                "show_weighted_items": True,
                "show_subcategories": True,
                "language": "en"
            }
        ).json()["items"]

    def get_venue_info(self, venue_slug):
        return requests.get(
            settings.VENUE_INFO_ENDPOINT.format(
                venue_slug=venue_slug,
                latitude=settings.LATITUDE,
                longitue=settings.LONGITUDE
            ),
            params={
                "lat": settings.LATITUDE,
                "lon": settings.LONGITUDE,
                "language": "en"
            }
        ).json()

    def check_venue(self, venue_slug: str):
        venue_info = requests.get(
            settings.VENUE_DETAILS_URI.format(venue_slug=venue_slug),
            params={
                "lat": settings.LATITUDE,
                "lon": settings.LONGITUDE,
                "language": "en"
            }
        ).json()
        venue_open = venue_info.get("venue", {}).get("open_status", {}).get("is_open", False)
        delivery_open = venue_info.get("venue", {}).get("delivery_open_status", {}).get("is_open", False)
        online = venue_info.get("venue", {}).get("online", False)
        alive = venue_info.get("venue_raw", {}).get("alive", False)

        return venue_open and delivery_open and online and alive