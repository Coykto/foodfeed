import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log_memory_usage():
    import psutil
    import os
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(f'Memory used: {mem_info.rss / 1024 / 1024} MB')

log_memory_usage()

from dependency.search_client import Search
from dependency.storage_client import Storage
from dependency.ai_client import AI


def lambda_handler(event, context):
    # init
    logger.info("++++++++++++++++++++++++")
    venue_slug = event["s"]
    country = "geo"
    city = "tbilisi"
    index_name = f"{country}.{city}.food"
    log_memory_usage()

    # Initialize services
    search = Search()
    storage = Storage()
    ai = AI()
    log_memory_usage()

    # Lambda logic
    if not search.doc_exists(index_name, "venue_slug", venue_slug):
        menu_items = ai.embedd_items(
            items=storage.get_processed_venue(country, city, venue_slug),
            embedd_field="full_description",
        )
        search.bulk(index_name, menu_items)
        return {"s": venue_slug}
    log_memory_usage()
    logger.info("------------------------")