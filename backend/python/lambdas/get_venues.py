import json
import logging
import os
import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Event: {}'.format(event))
    logger.info('Context: {}'.format(str(context)))

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
            'statusCode': 200,
            'Payload': [{"s": venue.get('venue').get('slug')} for venue in venues]
        }
