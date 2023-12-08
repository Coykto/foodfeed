import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


from dependency.search_client import Search
from dependency.storage_client import Storage
from dependency.ai_client import AI


def lambda_handler(event, context):
    # init
    venue_slug = event["s"]
    country = "geo"
    city = "tbilisi"
    index_name = f"{country}.{city}.food"

    # Initialize services
    search = Search()
    storage = Storage()
    ai = AI()

    # Lambda logic
    if not search.doc_exists(index_name, "venue_slug", venue_slug):
        menu_items = ai.embedd_items(
            items=storage.get_processed_venue(country, city, venue_slug),
            embedd_field="full_description",
        )
        search.bulk(index_name, menu_items)
        return {"s": venue_slug}
    logger.info("------------------------")