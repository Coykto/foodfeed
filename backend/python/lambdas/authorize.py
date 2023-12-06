import logging

from dependency.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    token = event.get("authorizationToken")
    if not token or token != settings.TELEGRAM_REQUEST_HEADER:
        logger.info(f"Authorization failed: token {event} !- {settings.TELEGRAM_REQUEST_HEADER}")
        raise Exception("Unauthorized")

    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        }
    }