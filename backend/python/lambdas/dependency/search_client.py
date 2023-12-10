from .config.food_index import index_settings
from opensearchpy import OpenSearch, AWSV4SignerAuth, RequestsHttpConnection
from googletrans import Translator, LANGUAGES

from typing import List
import boto3

import json
from .config.settings import settings


class Search:

    def __init__(self):
        self.client = OpenSearch(
            hosts=[{'host': settings.OPENSEARCH_ENDPOINT, 'port': 443}],
            http_auth=AWSV4SignerAuth(
                credentials=boto3.Session().get_credentials(),
                region=settings.REGION,
                service='es'
            ),
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

    def index(self, index_name: str, item: dict) -> None:
        item_id = item.pop("id")
        self.client.index(index_name=index_name, id=item_id, body=item)

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
                            "size": 10000
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

    def search_menu(self, index_name: str, vector: List[float], search_settings: dict, size: int = 10) -> List[dict]:
        search_result = self.client.search(
            timeout=60,
            size=size,
            index=index_name,
            body={
                "_source": {
                    "excludes": ["vector"]
                },
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "price": {
                                        "lte": search_settings["max_price"],
                                        "gte": search_settings["min_price"]
                                    }
                                }
                            },
                            {
                                "range": {
                                    "estimate": {
                                        "lte": search_settings["max_delivery_time"]
                                    }
                                }
                            },
                            {
                                "range": {
                                    "venue_rating": {
                                        "gte": search_settings["min_rating"]
                                    }
                                }
                            }
                        ],
                        "must": {
                            "knn": {
                                "vector": {
                                    "vector": vector,
                                    "k": size
                                }
                            }
                        }
                    }
                }
            }
        )["hits"]["hits"]
        return [hit["_source"] for hit in search_result]

    def get_not_enriched_items(
        self,
        index_name: str,
        size: int = 10
    ) -> List[dict]:
        search_result = self.client.search(
            timeout=60,
            size=size,
            index=index_name,
            body={
                "_source": {
                    "excludes": ["vector"]
                },
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "term": {
                                    "enriched": False
                                }
                            }
                        ]
                    }
                }
            }
        )["hits"]["hits"]
        return [hit["_source"] for hit in search_result]

    @classmethod
    def detect_and_translate(cls, query: str, to_lang:str = "en", max_attempts: int = 3, attempt: int = 0):
        try:
            translator = Translator()
            detected_language = translator.detect(query).lang
            lang = LANGUAGES.get(detected_language, 'unknown').capitalize()
            if detected_language != to_lang:
                translated = translator.translate(query, src=detected_language, dest=to_lang)
                return translated.text, lang
            else:
                return query, lang
        except Exception as e:
            if attempt > max_attempts:
                raise e
            return cls.detect_and_translate(query, to_lang, max_attempts, attempt + 1)
