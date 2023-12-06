import json
from os import path
import os
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


class SearchStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        dependency_layer: PythonLayerVersion,
        search_domain: opensearch.Domain,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.openai_api_key = self.node.try_get_context("OPENAI_API_KEY")
        self.telegram_token = self.node.try_get_context("TELEGRAM_TOKEN")

        user_settings_bucket = s3.Bucket(self, 'userSettings')

        start_search = lambda_.Function(
            self, 'startSearch',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!start_search.py"]
            ),
            handler='start_search.lambda_handler',
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )

        search = lambda_.Function(
            self, 'search',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!search.py"]
            ),
            handler='search.lambda_handler',
            timeout=Duration.seconds(300),
            environment={
                "OPENSEARCH_ENDPOINT": search_domain.domain_endpoint,
                "OPENAI_API_KEY": self.openai_api_key,
                "USER_SETTINGS_BUCKET":  user_settings_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        search_domain.grant_read_write(search)
        user_settings_bucket.grant_read_write(search)

        consult = lambda_.Function(
            self, 'consult',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!consult.py"]
            ),
            handler='consult.lambda_handler',
            timeout=Duration.seconds(300),
            environment={
                "OPENAI_API_KEY": self.openai_api_key,
                "USER_SETTINGS_BUCKET": user_settings_bucket.bucket_name,
                "VENUE_DETAILS_URI": "https://consumer-api.wolt.com/order-xp/web/v1/venue/slug/{venue_slug}/dynamic/",
                "LATITUDE": "41.72484116869996",
                "LONGITUDE": "44.72807697951794",
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        user_settings_bucket.grant_read_write(consult)

        send_search_result = lambda_.Function(
            self, 'sendSearchResult',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!send_search_result.py"]
            ),
            environment={
                "TELEGRAM_TOKEN": self.telegram_token,
            },
            handler='send_search_result.lambda_handler',
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )


        # ========================
        # Search Machine:
        # ========================
        search_task = tasks.LambdaInvoke(
            self, "Search",
            lambda_function=search,
            output_path="$.Payload",
        )
        consult_task = tasks.LambdaInvoke(
            self, "Consult",
            lambda_function=consult,
            output_path="$.Payload"
        )
        send_result_task = tasks.LambdaInvoke(
            self, "SendResult",
            lambda_function=send_search_result,
        )
        self.search_machine = sfn.StateMachine(
            self, "SearchMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                search_task
                .next(consult_task)
                .next(send_result_task)
            )
        )
        self.search_machine.grant_start_execution(start_search)
        start_search.add_environment("SEARCH_MACHINE_ARN", self.search_machine.state_machine_arn)
