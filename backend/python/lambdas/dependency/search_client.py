import json
import os
from typing import List

import boto3
from opensearchpy import OpenSearch, AWSV4SignerAuth, RequestsHttpConnection

from config.food_index import index_settings


class Search:

    def __int__(self):
        region = 'eu-west-1'
        service = 'es'
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, region, service)
        OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "")
        self.client = OpenSearch(
            hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
        )

    def _create_bulk(self, index_name, data) -> str:
        bulk_data = ''
        for item in data:
            item_action = json.dumps({"index": {"_index": index_name, "_id": item.pop("id")}})
            item_data = json.dumps(item)

            bulk_data += f"{item_action}\n{item_data}\n"
        return bulk_data

    def bulk(self, index_name: str, items: List[dict]) -> None:
        self.client.bulk(self._create_bulk(index_name, items))

    def doc_exists(self, index_name: str, field: str, value: str) -> bool:
        docs_count = self.client.search(
            timeout=60,
            size=0,
            index=f"{index_name}",
            body={
                "query": {
                    "match": {
                        f"{field}": f"{value}"
                    }
                }
            }
        )["hits"]["total"]["value"]

        return int(docs_count) > 0

    def indexed_venues(self, index_name: str) -> List[str]:
        venues = self.client.search(
            timeout=60,
            size=0,
            index=index_name,
            body={
                "aggs": {
                    "venues": {
                        "terms": {
                            "field": "venue_slug",
                            "size": 1000
                        }
                    }
                }
            }
        )["aggregations"]["venues"]["buckets"]

        return [venue["key"] for venue in venues]

    def initialize(self, index_name: str) -> int:
        if self.client.indices.exists(index_name):
            return 200
        self.client.indices.create(
            index_name,
            body=index_settings,
            timeout=60
        )
        return 201


