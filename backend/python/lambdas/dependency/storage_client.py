import json
import os
from typing import List, Dict, Union
from botocore.exceptions import ClientError

import boto3
from .config.settings import settings
from .config.user_settings import user_settings


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

    def _delete_object(self, bucket: str, key: str):
        return self.client.delete_object(
            Bucket=bucket,
            Key=key
        )

    def get_raw_venue(self, country: str, city: str, venue_slug: str) -> Dict:
        return self._get_object(
            settings.RAW_VENUES_BUCKET,
            f"{country}/{city}/restaurant/{venue_slug}.json"
        )

    def save_raw_venue(self, country: str, city: str, venue_slug: str, data: Union[List[dict], Dict]):
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

    def save_processed_venue(self, country: str, city: str, venue_slug: str, data: Union[List[dict], Dict]):
        return self._put_object(
            settings.PROCESSED_VENUES_BUCKET,
            f"{country}/{city}/restaurant/{venue_slug}.json",
            data
        )

    def get_user_settings(self, user_id: str) -> Dict:
        try:
            return self._get_object(
                settings.USER_SETTINGS_BUCKET,
                f"{user_id}_settings.json"
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                default_settings = user_settings
                default_settings["user_id"] = user_id
                self.save_user_settings(user_id, default_settings)
                return default_settings
            raise e

    def save_user_settings(self, user_id: str, data: Dict):
        return self._put_object(
            settings.USER_SETTINGS_BUCKET,
            f"{user_id}_settings.json",
            data
        )

    def get_search_result(self, user_id: str) -> Dict:
        return self._get_object(
            settings.SEARCH_RESULTS_BUCKET,
            f"{user_id}_search_result.json"
        )

    def save_search_result(self, user_id: str, data: Dict):
        return self._put_object(
            settings.SEARCH_RESULTS_BUCKET,
            f"{user_id}_search_result.json",
            data
        )

    def delete_search_result(self, user_id: str):
        return self._delete_object(
            settings.SEARCH_RESULTS_BUCKET,
            f"{user_id}_search_result.json"
        )