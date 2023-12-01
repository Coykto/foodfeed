import json
import boto3


def clean_string(input_string):
    if input_string is None:
        return ""
    """
    Cleans the given string by removing unicode characters representing emojis and other non-text elements.
    """
    # Using the re library to remove non-ASCII characters
    import re
    clean_str = re.sub(r'[^\x00-\x7F]+', '', input_string)
    return clean_str


def clean_tags(tags):
    return [clean_string(tag["name"]).lower() for tag in tags]


def generate_full_text(item):
    """
    item["venue"] = venue["venue"]["name"]
    item["venue_slug"] = venue_slug
    item["estimate"] = venue["venue"]["estimate"]
    item["venue_description"] = venue["venue"]["short_description"]
    item["venue_tags"] = [clean_string(tag).lower() for tag in venue["venue"]["tags"]]
    item["venue_rating"] = venue["venue"]["rating"]["score"]
    item["venue_image"] = (venue.get("image") or {}).get("url", {})

    # category data
    item["category"] = category["name"]
    item["category_slug"] = category["slug"]
    item["category_description"] = category["description"]
    item["category_image"] = category.get("image")

    # item data
    item["id"] = item["id"]
    item["image"] = item.get("image") or (item["images"] or [{}])[0].get("url")
    item["price"] = item["baseprice"]
    item["enabled"] = item["enabled"]
    item["tags"] = clean_tags(item["tags"])
    item["name"] = clean_string(item["name"])
    item["description"] = clean_string(item["description"])
    """
    name = item["name"]
    description = item["short_description"]
    tags = ', '.join(item["tags"])
    category = item["category"]
    category_description = item["category_description"]
    venue = item["venue"]
    venue_description = item["venue_description"]

    return (
        f"Name: {name}\n"
        f"Short Description: {description}\n"
        f"Tags: {tags}\n"
        f"Category: {category} - {category_description}\n"
        f"Venue: {venue}\n - {venue_description}"
    )