import logging
from pathlib import Path
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Event: {event}")

    tg_api_url = f"https://api.telegram.org/bot{event['token']}"
    gateway_url = f"{event['webhook_url']})api"
    telegram_secret_header = event["secret_header"]

    resp = requests.post(
        f"{tg_api_url}/setWebhook",
        data={
            "url": gateway_url,
            "drop_pending_updates": True,
            "secret_token": telegram_secret_header
        }
    )
    if resp.status_code != 200:
        raise Exception(f"Failed to setup webhook: {resp}")