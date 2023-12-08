import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from dependency.utils import clean_float
from dependency.search_client import Search
from dependency.ai_client import AI
from dependency.config.enricher_settings import enricher_settings


def lambda_handler(event, context):
    country = "geo"
    city = "tbilisi"
    index_name = f"{country}.{city}.food"

    search = Search()
    ai = AI()

    not_enriched_items = search.get_not_enriched_items(
        index_name=index_name,
        size=10
    )

    if not not_enriched_items:
        return {
            'statusCode': 404,
            'body': {'message': "no items to enrich"}
        }

    for item in not_enriched_items:
        enriched_item = ai.enrich(
            item_full_text=item["full_description"],
            item_url=item["image"],
            enricher_settings=enricher_settings
        )
        enriched_item["full_description"] = (
            f"{enriched_item['full_description']}/n"
            f"Full description: {enriched_item['extended_description']}"
        )
        enriched_item["enriched"] = True
        for float_key in enricher_settings["float_keys"]:
            enriched_item[float_key] = clean_float(enriched_item[float_key])

        item.update(enriched_item)

    enriched_items = ai.embedd_items(not_enriched_items, "full_description", True)

    search.bulk(index_name, enriched_items)

    # lambda_client = boto3.client('lambda')
    # lambda_client.invoke(
    #     FunctionName=context.function_name,
    #     InvocationType='Event',
    #     Payload=json.dumps(event)
    # )

    return {
        'statusCode': 200,
        'body': {
            'message': f"enriched {len(enriched_items)} items: {', '.join([item['id'] for item in enriched_items])}"
        }
    }
