import logging
import os
import boto3
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.INFO)


index_settings = {
    "settings": {"index.knn": True},
    "aliases": {
        "food": {}
    },
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
            "enriched": {"type": "boolean"}
        }
    }
}


def lambda_handler(event, context):
    country = "geo"
    city = "tbilisi"
    index_name = f"{country}.{city}.food"
    region = 'eu-west-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)
    OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT")
    opensearch_client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )
    status_code = 200
    if not opensearch_client.indices.exists(index_name):
        status_code = 201
        opensearch_client.indices.create(index_name, body=index_settings)

    return {
        "statusCode": status_code
    }