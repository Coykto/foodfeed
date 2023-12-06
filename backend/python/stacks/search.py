import json
from os import path
import os
from aws_cdk import (
    Stack,
)
from constructs import Construct
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_opensearchservice as opensearch
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk import Duration
import aws_cdk.aws_s3 as s3

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


def setup_search(scope, dependency_layer, search_domain, openai_api_key, telegram_token) -> lambda_.Function:
    user_settings_bucket = s3.Bucket(scope, 'userSettings')

    search = lambda_.Function(
        scope, 'search',
        runtime=lambda_.Runtime.PYTHON_3_9,
        code=lambda_.AssetCode.from_asset(
            path.join(os.getcwd(), 'python/lambdas/search'),
            exclude=["**", "!search.py"]
        ),
        handler='search.lambda_handler',
        timeout=Duration.seconds(300),
        environment={
            "OPENSEARCH_ENDPOINT": search_domain.domain_endpoint,
            "OPENAI_API_KEY": openai_api_key,
            "USER_SETTINGS_BUCKET": user_settings_bucket.bucket_name,
        },
        tracing=lambda_.Tracing.ACTIVE,
        layers=[dependency_layer]
    )
    search_domain.grant_read_write(search)
    user_settings_bucket.grant_read_write(search)

    consult = lambda_.Function(
        scope, 'consult',
        runtime=lambda_.Runtime.PYTHON_3_9,
        code=lambda_.AssetCode.from_asset(
            path.join(os.getcwd(), 'python/lambdas/search'),
            exclude=["**", "!consult.py"]
        ),
        handler='consult.lambda_handler',
        timeout=Duration.seconds(300),
        environment={
            "OPENAI_API_KEY": openai_api_key,
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
        scope, 'sendSearchResult',
        runtime=lambda_.Runtime.PYTHON_3_9,
        code=lambda_.AssetCode.from_asset(
            path.join(os.getcwd(), 'python/lambdas/search'),
            exclude=["**", "!send_search_result.py"]
        ),
        environment={
            "TELEGRAM_TOKEN": telegram_token,
        },
        handler='send_search_result.lambda_handler',
        tracing=lambda_.Tracing.ACTIVE,
        layers=[dependency_layer]
    )

    # ========================
    # Search Machine:
    # ========================
    search_task = tasks.LambdaInvoke(
        scope, "Search",
        lambda_function=search,
        output_path="$.Payload",
    )
    consult_task = tasks.LambdaInvoke(
        scope, "Consult",
        lambda_function=consult,
        output_path="$.Payload"
    )
    send_result_task = tasks.LambdaInvoke(
        scope, "SendResult",
        lambda_function=send_search_result,
    )
    search_machine = sfn.StateMachine(
        scope, "SearchMachine",
        definition_body=sfn.DefinitionBody.from_chainable(
            search_task
            .next(consult_task)
            .next(send_result_task)
        )
    )
    search_machine.grant_start_execution(start_search)
    start_search.add_environment("SEARCH_MACHINE_ARN", search_machine.state_machine_arn)

    return start_search

        
