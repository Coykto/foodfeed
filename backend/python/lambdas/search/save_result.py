import logging
from dependency.storage_client import Storage

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")
    storage = Storage()
    storage.save_search_result(event["user_id"], event)