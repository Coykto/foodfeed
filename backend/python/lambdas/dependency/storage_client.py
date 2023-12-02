import json
import os
from typing import List, Dict, Union

import boto3
from .config.settings import settings


class Storage:
    def __init__(self):
        self.client = boto3.client('s3')

    def _get_object(self, bucket: str, key: str):
        s3_response = self.client.get_object(
            Bucket=bucket,
            Key=key
        )
        return json.loads(s3_response["Body"].read().decode("utf-8"))

    def _put_object(self, bucket: str, key: str, data: Union[List[dict], Dict]):
        return self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data)
        )

    def get_raw_venue(self, country: str, city: str, venue_slug: str) -> Dict:
        return self._get_object(
            settings.RAW_VENUES_BUCKET,
            f"{country}/{city}/restaurant/{venue_slug}.json"
        )

    def put_raw_venue(self, country: str, city: str, venue_slug: str, data: Union[List[dict], Dict]):
        return self._put_object(
            settings.RAW_VENUES_BUCKET,
            f"{country}/{city}/restaurant/{venue_slug}.json",
            data
        )

    def get_processed_venue(self, country: str, city: str, venue_slug: str) -> Dict:
        return self._get_object(
            settings.PROCESSED_VENUES_BUCKET,
            f"{country}/{city}/restaurant/{venue_slug}.json"
        )

    def put_processed_venue(self, country: str, city: str, venue_slug: str, data: Union[List[dict], Dict]):
        return self._put_object(
            settings.PROCESSED_VENUES_BUCKET,
            f"{country}/{city}/restaurant/{venue_slug}.json",
            data
        )