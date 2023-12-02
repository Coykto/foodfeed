import json
import logging
import os
import boto3
import requests
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

from dependency.utils import get_venues_in_opensearch

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Event: {}'.format(event))
    logger.info('Context: {}'.format(str(context)))

    refresh = event.get("refresh", False)

    endpoint = os.getenv('VENUES_ENDPOINT')
    latitude = float(os.getenv('LATITUDE', 0.0))
    longitude = float(os.getenv('LONGITUDE', 0.0))
    bucket_name = os.getenv('RAW_VENUES_BUCKET')

    country = "geo"
    city = "tbilisi"

    s3_client = boto3.client('s3')

    try:
        venues_data = requests.get(
            endpoint,
            params={
                "lat": latitude,
                "lon": longitude,
                "language": "en"
            }
        ).json()

        venues = venues_data["sections"][1]["items"]

        if not refresh:
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
                pool_maxsize=20,
            )
            venues_in_opensearch = get_venues_in_opensearch(opensearch_client, index_name)
            venues = [venue for venue in venues if venue.get('venue').get('slug') not in venues_in_opensearch]

        for venue in venues:
            s3_client.put_object(
                Body=json.dumps(venue),
                Bucket=bucket_name,
                Key=f"{country}/{city}/restaurant/{venue.get('venue').get('slug')}.json"
            )

    except Exception as error:
        error_msg = f"{error.__class__}: {error}"
        logger.error(error_msg)
        return {
            'statusCode': 500,
            'body': {'message': error_msg}
        }
    else:
        return {
            'Payload': [{"s": venue.get('venue').get('slug')} for venue in venues]
        }