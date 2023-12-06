import logging

from dependency.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # setWebhook
    api_gateway_url = next((item for item in outputs if item["OutputKey"] == "Ap?iEndpoint"), None)['OutputValue']

    api_url = f"{api_gateway_url}/api"
    import requests
    url = f"https://api.telegram.org/bot{telegram_api_token}/"
    resp = requests.post(
        url + "setWebhook",
        data={
            "url": api_url,
            "drop_pending_updates": True,
            "secret_token": telegram_secret_header
        }
    )
    if resp.status_code != 200:
        raise Exception(f"Failed to setup webhook: {resp}")