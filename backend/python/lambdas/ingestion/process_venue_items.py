import json
import logging
import os
import boto3
import requests


from dependency.utils import clean_string, clean_tags
from dependency.slugify import slug
from dependency.storage_client import Storage
from dependency.wolt_client import Wolt


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    country = "geo"
    city = "tbilisi"

    storage = Storage()
    wolt = Wolt()

    venue_slug = event["s"]
    venue = storage.get_raw_venue(country, city, venue_slug)

    venue_categories = wolt.categories(venue_slug, )

    menu_items = []
    for category in venue_categories:
        logger.info(f"Category: {category['slug']}")

        category_menu_items = wolt.menu_items(venue_slug, category["slug"])

        for item in category_menu_items:
            menu_items.append({
                # venue data
                "venue": clean_string(venue["venue"]["name"]),
                "venue_slug": venue_slug,
                "estimate": venue["venue"]["estimate"],
                "venue_description": clean_string(venue["venue"].get("short_description", "")),
                "venue_tags": [clean_string(tag).lower() for tag in venue["venue"]["tags"]],
                "venue_rating": (venue["venue"].get("rating") or {}).get("score"),
                "venue_image": (venue.get("image") or {}).get("url", {}),

                # category data
                "category": clean_string(category["name"]),
                "category_slug": category["slug"],
                "category_description": clean_string(category.get("description", "")),
                "category_image": category.get("image"),

                # item data
                "id": item["id"],
                "image": item.get("image") or (item["images"] or [{}])[0].get("url"),
                "price": item["baseprice"],
                "enabled": item["enabled"],
                "tags": clean_tags(item["tags"]),
                "name": clean_string(item["name"]),
                "description": clean_string(item["description"]),
                "full_slug": f"{venue_slug}/{slug(clean_string(item['name']), item['id'])}",
                "full_description": (
                    f"Venue: {clean_string(venue['venue']['name'])}\n"
                    f"Venue Description: {clean_string(venue['venue'].get('short_description',''))}\n"
                    f"Venue Tags: {', '.join([clean_string(tag).lower() for tag in venue['venue']['tags']])}\n"
                    f"Category: {clean_string(category['name'])}\n"
                    f"Category Description: {clean_string(category.get('description', ''))}\n"
                    f"Item: {clean_string(item['name'])}\n"
                    f"Item Description: {clean_string(item['description'])}\n"
                    f"Item Tags: {', '.join(clean_tags(item['tags']))}\n"
                )
            })

    storage.save_processed_venue(country, city, venue_slug, menu_items)

    return {"s": venue_slug}