import json
from typing import List

import boto3
import openai


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


def embedd_items(
    openai_client: openai.Client,
    items: List[dict],
    embedd_field: str,
    enriched: bool = False,
    embed_model: str = "text-embedding-ada-002",
    max_attempts: int = 3,
    attempt: int = 0,
) -> List[dict]:
    if attempt > max_attempts:
        raise Exception("Too many attempts to embedd")
    try:
        res = openai_client.embeddings.create(
            input=[item[embedd_field] for item in items],
            model=embed_model
        )
        embeds = [record.embedding for record in res.data]
        for index, item in enumerate(items):
            item["vector"] = embeds[index]
            item["enriched"] = enriched
        return items
    except Exception as e:
        return embedd_items(
            openai_client,
            items,
            embedd_field,
            enriched,
            embed_model,
            max_attempts,
            attempt + 1
        )


def create_bulk(index_name, data) -> str:
    bulk_data = ''
    for item in data:
        item_action = json.dumps({"index": {"_index": index_name, "_id": item.pop("id")}})
        item_data = json.dumps(item)

        bulk_data += f"{item_action}\n{item_data}\n"
    return bulk_data


def embedd_query(
    openai_client: openai.Client,
    query: str,
    embed_model: str = "text-embedding-ada-002",
    max_attempts: int = 3,
    attempt: int = 0,
) -> List[float]:
    if attempt > max_attempts:
        raise Exception("Too many attempts to embedd")
    try:
        return openai_client.embeddings.create(
            input=[query],
            model=embed_model
        ).data[0].embedding
    except Exception:
        return embedd_query(
            openai_client,
            query,
            embed_model,
            max_attempts,
            attempt + 1
        )

