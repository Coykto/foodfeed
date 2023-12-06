from os import path
import os
from aws_cdk import (
    Stack,
    CfnOutput
)
from uuid import uuid4

from constructs import Construct
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_apigateway as apigateway
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


class ApiStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str, dependency_layer: PythonLayerVersion,
        start_search_lambda: lambda_.Function,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.telegram_secret_header = str(uuid4())

        auth = lambda_.Function(
            self, 'Authorize',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!authorize.py"]
            ),
            environment={"TELEGRAM_REQUEST_HEADER": self.telegram_secret_header},
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
        api.add_method(
            'POST',
            apigateway.LambdaIntegration(start_search_lambda),
            authorizer=authorize
        )
        self.api_gateway_url = apiGateway.url

        CfnOutput(self, ApiGatewayEndpointStackOutput,
            value=apiGateway.url
        )

        CfnOutput(self, ApiGatewayDomainStackOutput,
            value=apiGateway.url.split('/')[2]
        )

        CfnOutput(self, ApiGatewayStageStackOutput,
            value=apiGateway.deployment_stage.stage_name
        )

