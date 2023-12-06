import json
import os

from aws_cdk.custom_resources import AwsCustomResource
import aws_cdk.aws_lambda as lambda_
from aws_cdk import aws_logs as logs
import aws_cdk.aws_apigateway as apigateway

ApiGatewayEndpointStackOutput = "ApiEndpoint"
ApiGatewayDomainStackOutput = "ApiDomain"
ApiGatewayStageStackOutput = "ApiStage"


def setup_telegram(scope, api, telegram_api_token, telegram_secret_header, dependency_layer):

        setup_webhook = lambda_.Function(
            scope, "setupTelegramWebhook",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), "python/lambdas/telegram"),
                exclude=["**", "!setup_webhook.py"]
            ),
            handler="setup_webhook.lambda_handler",
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )

        lambda_params = {
            "service": "Lambda",
            "action": "invoke",
            "parameters": {
                "FunctionName": setup_webhook.function_arn,
                "Payload": json.dumps({
                    "token": telegram_api_token,
                    "webhook_url": api.url,
                    "secret_header": telegram_secret_header
                })
            },
            "physicalResourceId": "TelegramWebhookSetup"
        }

        AwsCustomResource(
            scope, "TelegramWebhookSetup",
            log_retention=logs.RetentionDays.ONE_DAY,
            on_create=lambda_params,
            on_update=lambda_params
        )

        receive_update = lambda_.Function(
            scope, 'startSearch',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), 'python/lambdas/telegram'),
                exclude=["**", "!receive_update.py"]
            ),
            handler='receive_update.lambda_handler',
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )

        send_message = lambda_.Function(
            scope, 'startSearch',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), 'python/lambdas/telegram'),
                exclude=["**", "!send_message.py"]
            ),
            handler='send_message.lambda_handler',
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )

        send_message.grant_invoke(receive_update)

        api.add_method(
            'POST',
            apigateway.LambdaIntegration(receive_update),
        )