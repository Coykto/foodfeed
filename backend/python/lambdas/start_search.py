import json
import logging

import boto3

from dependency.config.settings import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    sfn_client = boto3.client("stepfunctions")
    sfn_client.start_execution(
        stateMachineArn=settings.SEARCH_MACHINE_ARN,
        input=json.dumps(json.loads(event["body"])["message"])
    )

    return {"statusCode": 200}