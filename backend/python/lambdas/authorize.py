import json
import logging

import boto3

from dependency.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    token = event.get("authorizationToken")
    if not token or token != settings.TELEGRAM_REQUEST_HEADER:
        logger.info(f"Authorization failed: token {event} !- {settings.TELEGRAM_REQUEST_HEADER}")
        raise Exception("Unauthorized")

    sfn_client = boto3.client('stepfunctions')
    sfn_client.start_execution(
        stateMachineArn=settings.SEARCH_MACHINE_ARN,
        input=json.dumps(event)
    )

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