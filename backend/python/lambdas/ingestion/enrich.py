import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from dependency.utils import clean_float
from dependency.search_client import Search
from dependency.ai_client import AI, AIRateLimitExceeded
from dependency.config.enricher_settings import enricher_settings


def lambda_handler(event, context):
    country = "geo"
    city = "tbilisi"
    index_name = f"{country}.{city}.food"

    search = Search()
    ai = AI()

    enrichment_batch_size = 10

    not_enriched_items = search.get_not_enriched_items(
        index_name=index_name,
        size=enrichment_batch_size
    )

    if not not_enriched_items:
        return {
            'statusCode': 404,
            'body': {'message': "no items to enrich"}
        }

    enriched_items_count = 0

    try:
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
            item["vector"] = ai.embedd_item(item)
            search.index(index_name, item)

            enriched_items_count += 1
    except AIRateLimitExceeded as e:
        return {
            'statusCode': 429,
            'body': {
                'message': f"Rate limit exceeded: {e}"
            }
        }
    except Exception as e:
        logger.exception(e)

        if enriched_items_count == 0:
            return {
                'statusCode': 500,
                'body': {
                    'message': f"Failed to enrich items: {e}"
                }
            }

        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType='Event',
            Payload=json.dumps(event)
        )

    return {
        'statusCode': 200,
        'body': {
            'message': f"enriched {enriched_items_count} items"
        }
    }
