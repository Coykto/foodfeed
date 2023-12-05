import json

from dependency.config.settings import settings

def lambda_handler(event, context):
    token = event['headers'].get('X-Telegram-Bot-Api-Secret-Token')
    if not token or token != settings.TELEGRAM_REQUEST_HEADER:
        raise Exception('Unauthorized')
