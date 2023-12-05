import boto3




def bot_setup(telegram_api_token, telegram_secret_header):
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName="Backend")
    outputs = response['Stacks'][0]['Outputs']
    api_gateway_url = next((item for item in outputs if item["OutputKey"] == "ApiEndpoint"), None)['OutputValue']


    api_url = f"{api_gateway_url}/api"
    print("Setting up telegram webhook")
    print(f"API token: {telegram_api_token}")
    print(f"Secret header: {telegram_secret_header}")
    print(f"API gateway URL: {api_url}")
    print("=====================================")
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

