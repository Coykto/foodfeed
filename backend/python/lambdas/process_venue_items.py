import json
import logging
import os
import boto3
import requests


from dependency.utils import clean_string, clean_tags
from dependency.slugify import slug


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_venue_categories(base_host, venue_categories_uri, venue_slug):
    return requests.get(
        f"{base_host}{venue_categories_uri.format(venue=venue_slug)}",
        params={
            "unit_prices": True,
            "show_weighted_items": True,
            "show_subcategories": True,
            "language": "en"
        }
    ).json()


def lambda_handler(event, context):
    logger.info('Event: {}'.format(event))
    logger.info('Context: {}'.format(str(context)))

    BASE_HOST = os.getenv("BASE_HOST")
    VENUE_CATEGORIES_URI = os.getenv("VENUE_CATEGORIES_URI")
    VENUE_MENU_URI = os.getenv("VENUE_MENU_URI")
    RAW_VENUES_BUCKET = os.getenv("RAW_VENUES_BUCKET")
    PROCESSED_VENUES_BUCKET = os.getenv("PROCESSED_VENUES_BUCKET")

    country = "geo"
    city = "tbilisi"

    s3_client = boto3.client('s3')

    venue_slug = event["s"]
    s3_response =  s3_client.get_object(
        Bucket=RAW_VENUES_BUCKET,
        Key=f"{country}/{city}/restaurant/{venue_slug}.json"
    )

    venue = json.loads(s3_response["Body"].read().decode("utf-8"))

    venue_categories = get_venue_categories(BASE_HOST, VENUE_CATEGORIES_URI, venue_slug)

    menu_items = []
    for category in venue_categories["categories"]:
        logger.info(f"Category: {category['slug']}")
        category_menu_items = requests.get(
            f"{BASE_HOST}{VENUE_MENU_URI.format(venue=venue_slug, category=category['slug'])}",
            params={
                "unit_prices": True,
                "show_weighted_items": True,
                "show_subcategories": True,
                "language": "en"
            }
        ).json()

        for item in category_menu_items["items"]:
            menu_items.append({
                # venue data
                "venue": clean_string(venue["venue"]["name"]),
                "venue_slug": venue_slug,
                "estimate": venue["venue"]["estimate"],
                "venue_description": clean_string(venue["venue"]["short_description"]),
                "venue_tags": [clean_string(tag).lower() for tag in venue["venue"]["tags"]],
                "venue_rating": (venue["venue"].get("rating") or {}).get("score"),
                "venue_image": (venue.get("image") or {}).get("url", {}),

                # category data
                "category": clean_string(category["name"]),
                "category_slug": category["slug"],
                "category_description": clean_string(category["description"]),
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
                    f"Venue Description: {clean_string(venue['venue']['short_description'])}\n"
                    f"Venue Tags: {', '.join([clean_string(tag).lower() for tag in venue['venue']['tags']])}\n"
                    f"Category: {clean_string(category['name'])}\n"
                    f"Category Description: {clean_string(category['description'])}\n"
                    f"Item: {clean_string(item['name'])}\n"
                    f"Item Description: {clean_string(item['description'])}\n"
                    f"Item Tags: {', '.join(clean_tags(item['tags']))}\n"
                )
            })

    s3_client.put_object(
        Body=json.dumps(menu_items),
        Bucket=PROCESSED_VENUES_BUCKET,
        Key=f"{country}/{city}/restaurant/{venue_slug}.json"
    )

    return {"s": venue_slug}