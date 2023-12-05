import json

import requests
from dependency.config.settings import settings

def lambda_handler(event, context):
    item_url = event["url"]
    reason = event["reason"]
    user_id = event["user_id"]

    requests.post(
        f"{settings.TELEGRAM_API_URL}/sendMessage",
        data={
            "chat_id": user_id,
            "text": f"{reason}\n{item_url}",
        }
    )
