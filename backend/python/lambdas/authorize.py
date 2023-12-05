import json
import logging

from dependency.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("event", event)
    logger.info("context", context)
    token = event['headers'].get('X-Telegram-Bot-Api-Secret-Token')
    if not token or token != settings.TELEGRAM_REQUEST_HEADER:
        raise Exception('Unauthorized')
