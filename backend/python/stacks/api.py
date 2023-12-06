from os import path
import os
from typing import Tuple

from aws_cdk import CfnOutput
from uuid import uuid4

import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_apigateway as apigateway

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


def setup_api(self, dependency_layer) -> Tuple[apigateway.Resource, str]:
        telegram_secret_header = str(uuid4())

        auth = lambda_.Function(
            self, 'Authorize',
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
            self, 'Authorizer',
            handler=auth,
            identity_source=apigateway.IdentitySource.header('X-Telegram-Bot-Api-Secret-Token'),
        )

        apiGateway = apigateway.RestApi(self, 'ApiGateway',
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

        api = apiGateway.root.add_resource('api')
        api.add_method('ANY', authorizer=authorize)

        CfnOutput(self, ApiGatewayEndpointStackOutput,
            value=apiGateway.url
        )

        CfnOutput(self, ApiGatewayDomainStackOutput,
            value=apiGateway.url.split('/')[2]
        )

        CfnOutput(self, ApiGatewayStageStackOutput,
            value=apiGateway.deployment_stage.stage_name
        )

        return api, telegram_secret_header
