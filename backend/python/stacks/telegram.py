import json
import os

from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.custom_resources import AwsCustomResource, PhysicalResourceId, AwsCustomResourcePolicy
import aws_cdk.aws_lambda as lambda_
from aws_cdk import aws_logs as logs, Stack
import aws_cdk.aws_apigateway as apigateway
from aws_cdk.aws_stepfunctions import StateMachine

ApiGatewayEndpointStackOutput = "ApiEndpoint"
ApiGatewayDomainStackOutput = "ApiDomain"
ApiGatewayStageStackOutput = "ApiStage"


def setup_telegram(
    stack: Stack,
    dependency_layer: PythonLayerVersion,
    apiGateway: apigateway.RestApi,
    telegram_api_token: str,
    telegram_secret_header: str,
    search_machine: StateMachine,
):

    setup_webhook = lambda_.Function(
        stack, "setupTelegramWebhook",
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
                "webhook_url": apiGateway.url,
                "secret_header": telegram_secret_header
            })
        },
        "physical_resource_id": PhysicalResourceId.of("TelegramWebhookSetup")
    }

    AwsCustomResource(
        stack, "TelegramWebhookSetup",
        log_retention=logs.RetentionDays.ONE_DAY,
        on_create=lambda_params,
        on_update=lambda_params,
        policy=AwsCustomResourcePolicy.from_sdk_calls(
            resources=AwsCustomResourcePolicy.ANY_RESOURCE
        )
    )

    receive_update = lambda_.Function(
        stack, 'receiveUpdate',
        runtime=lambda_.Runtime.PYTHON_3_9,
        code=lambda_.AssetCode.from_asset(
            os.path.join(os.getcwd(), 'python/lambdas/telegram'),
            exclude=["**", "!receive_update.py"]
        ),
        environment={
            "SEARCH_MACHINE_ARN": search_machine.state_machine_arn
        },
        handler='receive_update.lambda_handler',
        tracing=lambda_.Tracing.ACTIVE,
        layers=[dependency_layer]
    )
    search_machine.grant_start_execution(receive_update)


    send_message = lambda_.Function(
        stack, 'sendMessage',
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

    api = apiGateway.root.add_resource('api')
    api.add_method(
        'POST',
        apigateway.LambdaIntegration(receive_update),
    )
