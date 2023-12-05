import json
import logging
import requests
from dependency.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")
    item_url = event["url"]
    reason = event["reason"]
    user_id = event["user_id"]
    logger.info(f"TELEGRAM_API_URL: {settings.TELEGRAM_API_URL}")

    res = requests.post(
        f"{settings.TELEGRAM_API_URL}/sendMessage",
        data={
            "chat_id": user_id,
            "text": f"{reason}\n{item_url}",
        }
    )
    logger.info(f"Response: {res}")
