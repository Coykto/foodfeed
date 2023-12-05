def bot_setup(
    telegram_api_token: str,
    telegram_secret_header: str,
    api_gateway_url: str
):
    import requests
    url = f"https://api.telegram.org/bot{telegram_api_token}/"
    resp = requests.post(
        url + "setWebhook",
        data={
            "url": api_gateway_url,
            "drop_pending_updates": True,
            "secret_token": telegram_secret_header
        }
    )
    if resp.status_code != 200:
        raise Exception(f"Failed to setup webhook: {resp.text}")

