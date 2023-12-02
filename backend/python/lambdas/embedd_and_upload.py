import json
import logging
import os
import datetime
import boto3
import uuid

import openai
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.INFO)

index_settings = {
    "settings": {"index.knn": True},
    "mappings": {
        "properties": {
            # venue data
            "venue": {"type": "keyword"},
            "venue_slug": {"type": "keyword"},
            "venue_description": {"type": "keyword"},
            "venue_tags": {"type": "keyword"},
            "venue_rating": {"type": "float"},
            "venue_image": {"type": "keyword"},
            "estimate": {"type": "float"},

            # category data
            "category": {"type": "keyword"},
            "category_slug": {"type": "keyword"},
            "category_description": {"type": "keyword"},
            "category_image": {"type": "keyword"},

            # item data
            "image": {"type": "keyword"},
            "price": {"type": "integer"},
            "enabled": {"type": "boolean"},
            "tags": {"type": "keyword"},
            "name": {"type": "keyword"},
            "description": {"type": "text"},
            "full_slug": {"type": "keyword"},
            "full_description": {"type": "text"},

            # AI data
            "vector": {"type": "knn_vector", "dimension": 1536},
            "calories": {"type": "float"},
            "fat": {"type": "float"},
            "carbohydrates": {"type": "float"},
            "protein": {"type": "float"},
            "ingredients": {"type": "keyword"},
            "fiber": {"type": "float"},
            "sugar": {"type": "float"},
        }
    }
}


# item = {
#     # venue data
#     "venue": clean_string(venue["venue"]["name"]),
#     "venue_slug": venue_slug,
#     "venue_description": clean_string(venue["venue"]["short_description"]),
#     "venue_tags": [clean_string(tag).lower() for tag in venue["venue"]["tags"]],
#     "venue_rating": (venue["venue"].get("rating") or {}).get("score"),
#     "venue_image": (venue.get("image") or {}).get("url", {}),
#     "estimate": venue["venue"]["estimate"],
#
#     # category data
#     "category": clean_string(category["name"]),
#     "category_slug": category["slug"],
#     "category_description": clean_string(category["description"]),
#     "category_image": category.get("image"),
#
#     # item data
#     "id": item["id"],
#     "image": item.get("image") or (item["images"] or [{}])[0].get("url"),
#     "price": item["baseprice"],
#     "enabled": item["enabled"],
#     "tags": clean_tags(item["tags"]),
#     "name": clean_string(item["name"]),
#     "description": clean_string(item["description"]),
#     "full_slug": f"{venue_slug}/{slug(clean_string(item['name']), item['id'])}",
#     "full_description": (
#         f"Venue: {clean_string(venue['venue']['name'])}\n"
#         f"Venue Description: {clean_string(venue['venue']['short_description'])}\n"
#         f"Venue Tags: {', '.join([clean_string(tag).lower() for tag in venue['venue']['tags']])}\n"
#         f"Category: {clean_string(category['name'])}\n"
#         f"Category Description: {clean_string(category['description'])}\n"
#         f"Item: {clean_string(item['name'])}\n"
#         f"Item Description: {clean_string(item['description'])}\n"
#         f"Item Tags: {', '.join(clean_tags(item['tags']))}\n"
#     )
# }

def lambda_handler(event, context):
    logger.info('Event: {}'.format(event))
    logger.info('Context: {}'.format(context))

    # init
    venue_slug = event["s"]
    PROCESSED_VENUES_BUCKET = os.getenv("PROCESSED_VENUES_BUCKET")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT")
    embed_model = "text-embedding-ada-002"
    index_name = "food"
    country = "geo"
    city = "tbilisi"
    region = 'eu-west-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)
    s3_client = boto3.client('s3')
    openai_client = openai.Client(api_key=OPENAI_API_KEY)
    opensearch_client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )
    if not opensearch_client.indices.exists(index_name):
        opensearch_client.indices.create(index_name, body=index_settings)


    # s3_response = s3_client.get_object(
    #     Bucket=PROCESSED_VENUES_BUCKET,
    #     Key=f"{country}/{city}/restaurant/{venue_slug}.json"
    # )
    #
    # menu_items = json.loads(s3_response["Body"].read().decode("utf-8"))


