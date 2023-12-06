import json
from os import path
import os

import boto3
from aws_cdk import (
    StackProps,
    Stack,
    CfnOutput
)
from uuid import uuid4

from aws_cdk import aws_iam as iam
from constructs import Construct
import aws_cdk.aws_lambda as lambda_
from aws_cdk import aws_logs as logs
import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_opensearchservice as opensearch
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, BundlingOptions
from aws_cdk import DockerImage, Duration
import aws_cdk.aws_s3 as s3

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


class TelegramStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        telegram_api_token: str,
        telegram_secret_header: str,
        dependency_layer: PythonLayerVersion,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # setWebhook
        client = boto3.client('cloudformation', region_name=os.getenv('CDK_DEFAULT_REGION'))
        response = client.describe_stacks(StackName="Backend")
        outputs = response['Stacks'][0]['Outputs']
        api_gateway_url = next((item for item in outputs if item["OutputKey"] == "ApiEndpoint"), None)['OutputValue']

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


