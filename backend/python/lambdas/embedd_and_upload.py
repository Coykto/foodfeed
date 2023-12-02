import json
import logging
import os

import boto3

import openai
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

from dependency.utils import embedd_items, create_bulk

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Event: {}'.format(event))
    logger.info('Context: {}'.format(context))

    # init
    venue_slug = event["s"]
    PROCESSED_VENUES_BUCKET = os.getenv("PROCESSED_VENUES_BUCKET")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT")
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

    s3_response = s3_client.get_object(
        Bucket=PROCESSED_VENUES_BUCKET,
        Key=f"{country}/{city}/restaurant/{venue_slug}.json"
    )

    menu_items = embedd_items(
        openai_client,
        items=json.loads(s3_response["Body"].read().decode("utf-8")),
        embedd_field="full_description",
    )

    bulk_data = create_bulk(index_name, menu_items)
    opensearch_client.bulk(bulk_data, index=index_name, timeout=300)

    return {"s": venue_slug}
