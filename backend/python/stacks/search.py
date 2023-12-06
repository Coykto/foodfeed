from os import path
import os
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import Duration, Stack
import aws_cdk.aws_s3 as s3
from aws_cdk.aws_opensearchservice import Domain
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


def setup_search(
    stack: Stack,
    dependency_layer: PythonLayerVersion,
    search_domain: Domain,
    openai_api_key: str,
    telegram_token: str,
) -> sfn.StateMachine:
    user_settings_bucket = s3.Bucket(stack, 'userSettings')

    search = lambda_.Function(
        stack, 'search',
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
        stack, 'consult',
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
        stack, 'sendSearchResult',
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
        stack, "Search",
        lambda_function=search,
        output_path="$.Payload",
    )
    consult_task = tasks.LambdaInvoke(
        stack, "Consult",
        lambda_function=consult,
        output_path="$.Payload"
    )
    send_result_task = tasks.LambdaInvoke(
        stack, "SendResult",
        lambda_function=send_search_result,
    )
    search_machine = sfn.StateMachine(
        stack, "SearchMachine",
        definition_body=sfn.DefinitionBody.from_chainable(
            search_task
            .next(consult_task)
            .next(send_result_task)
        )
    )
    return search_machine
