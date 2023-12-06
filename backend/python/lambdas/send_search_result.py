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

    telegram_api_url = settings.TELEGRAM_API_URL.format(key=settings.TELEGRAM_TOKEN)
    logger.info(f"TELEGRAM_API_URL: {telegram_api_url}")

    res = requests.post(
        f"{telegram_api_url}/sendMessage",
        data={
            "chat_id": user_id,
            "text": f"{reason}\n{item_url}",
        }
    )
    logger.info(f"Response: {res}")
