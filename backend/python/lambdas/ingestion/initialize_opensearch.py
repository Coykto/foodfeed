import logging
from dependency.search_client import Search

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    country = "geo"
    city = "tbilisi"
    index_name = f"{country}.{city}.food"

    return {
        "Payload": {
            "statusCode": Search().initialize(index_name),
            "refresh": event.get("refresh", False)
        }
    }