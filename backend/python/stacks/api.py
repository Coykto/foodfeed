from os import path
import os

from aws_cdk import CfnOutput, Stack

import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_apigateway as apigateway
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


def setup_api(
    stack: Stack,
    dependency_layer: PythonLayerVersion,
    telegram_secret_header: str
) -> apigateway.RestApi:

    auth = lambda_.Function(
        stack, 'Authorize',
        runtime=lambda_.Runtime.PYTHON_3_9,
        code=lambda_.AssetCode.from_asset(
            path.join(os.getcwd(), 'python/lambdas'),
            exclude=["**", "!authorize.py"]
        ),
        environment={"TELEGRAM_REQUEST_HEADER": telegram_secret_header},
        handler='authorize.lambda_handler',
        layers=[dependency_layer]
    )

    authorize = apigateway.TokenAuthorizer(
        stack, 'Authorizer',
        handler=auth,
        identity_source=apigateway.IdentitySource.header('X-Telegram-Bot-Api-Secret-Token'),
    )

    apiGateway = apigateway.RestApi(
        stack, 'ApiGateway',
        default_cors_preflight_options=apigateway.CorsOptions(
            allow_credentials=True,
            allow_origins=apigateway.Cors.ALL_ORIGINS,
            allow_headers=[
                "Content-Type",
                "Authorization",
                "Content-Length",
                "X-Requested-With",
                "X-Telegram-Bot-Api-Secret-Token",
            ]
        )
    )

    apiGateway.root.add_method('ANY', authorizer=authorize)

    CfnOutput(stack, ApiGatewayEndpointStackOutput,
              value=apiGateway.url
              )

    CfnOutput(stack, ApiGatewayDomainStackOutput,
              value=apiGateway.url.split('/')[2]
              )

    CfnOutput(stack, ApiGatewayStageStackOutput,
              value=apiGateway.deployment_stage.stage_name
              )

    return apiGateway
