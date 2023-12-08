import logging
import requests
from dependency.config.settings import settings
from dependency.storage_client import Storage

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    result_key = event["Records"][0]["s3"]["object"]["key"]
    user_id = result_key.split("_")[0]

    storage = Storage()
    search_result = storage.get_search_result(user_id)

    item_url = search_result["url"]
    reason = search_result["reason"]
    user_id = search_result["user_id"]

    telegram_api_url = settings.TELEGRAM_API_URL.format(key=settings.TELEGRAM_TOKEN)

    res = requests.post(
        f"{telegram_api_url}/sendMessage",
        data={
            "chat_id": user_id,
            "text": f"{reason}\n{item_url}",
        }
    )
    if res.status_code != 200:
        logger.error(f"Failed to send message to Telegram: {res.text}")
        raise Exception("Failed to send message to Telegram")

    storage.delete_search_result(user_id)
