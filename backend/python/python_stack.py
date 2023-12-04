import json
from os import path
import os
from aws_cdk import (
    StackProps,
    Stack,
    CfnOutput
)
from aws_cdk import aws_iam as iam
from constructs import Construct
import aws_cdk.aws_lambda as lambda_
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


class PythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.openai_api_key = self.node.try_get_context('OPENAI_API_KEY')

        # ========================
        # Storage Infrastructure
        # ========================
        search_domain = opensearch.Domain(self, 'food',
            version=opensearch.EngineVersion.OPENSEARCH_2_9,
            domain_name='food',
            use_unsigned_basic_auth=True,
            capacity=opensearch.CapacityConfig(
                master_nodes=2,
                master_node_instance_type='t3.small.search',
                data_nodes=1,
                data_node_instance_type='t3.small.search',
            )
        )
        search_domain.grant_read_write(iam.Group.from_group_name(self, "DevGroup", "admins"))

        raw_venues_bucket = s3.Bucket(self, 'rawVenues')
        processed_venues_bucket = s3.Bucket(self, 'processedVenues')
        user_settings_bucket = s3.Bucket(self, 'userSettings')

        # ========================
        # Lambdas Definitions
        # ========================
        layer_entry = path.join(os.getcwd(), 'python/lambdas')
        dependency_layer = PythonLayerVersion(
            self, 'DependencyLayer',
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            entry=layer_entry,
            bundling=BundlingOptions(image=DockerImage.from_build(
                path=f"{layer_entry}/dependency",
                file='Dockerfile'
            ))
        )

        initialize_opensearch = lambda_.Function(self, 'initializeOpensearch',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!initialize_opensearch.py"]
            ),
            handler='initialize_opensearch.lambda_handler',
            timeout=Duration.seconds(30),
            environment={"OPENSEARCH_ENDPOINT": search_domain.domain_endpoint},
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        search_domain.grant_read_write(initialize_opensearch)

        get_venues = lambda_.Function(self,'getVenues',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!get_venues.py"]
            ),
            handler='get_venues.lambda_handler',
            timeout=Duration.seconds(60),
            environment={
                "OPENSEARCH_ENDPOINT": search_domain.domain_endpoint,
                "VENUES_ENDPOINT": "https://consumer-api.wolt.com/v1/pages/restaurants",
                "LATITUDE": "41.72484116869996",
                "LONGITUDE": "44.72807697951794",
                "RAW_VENUES_BUCKET": raw_venues_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        raw_venues_bucket.grant_read_write(get_venues)
        search_domain.grant_read_write(get_venues)

        process_venue_items = lambda_.Function(self,'getVenueItems',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!process_venue_items.py"]
            ),
            handler='process_venue_items.lambda_handler',
            timeout=Duration.seconds(60),
            environment={
                "WOLT_API_BASE": "https://restaurant-api.wolt.com/v4/venues/slug/",
                "VENUE_CATEGORIES_URI": "{venue}/menu/data",
                "VENUE_MENU_URI": "{venue}/menu/categories/slug/{category}",
                "RAW_VENUES_BUCKET": raw_venues_bucket.bucket_name,
                "PROCESSED_VENUES_BUCKET": processed_venues_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        raw_venues_bucket.grant_read(process_venue_items)
        processed_venues_bucket.grant_write(process_venue_items)

        embedd_and_upload = lambda_.Function(self,'embeddAndUpload',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!embedd_and_upload.py"]
            ),
            handler='embedd_and_upload.lambda_handler',
            timeout=Duration.seconds(300),
            environment={
                "OPENSEARCH_ENDPOINT": search_domain.domain_endpoint,
                "OPENAI_API_KEY": self.openai_api_key,
                "PROCESSED_VENUES_BUCKET": processed_venues_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        search_domain.grant_read_write(embedd_and_upload)
        processed_venues_bucket.grant_read(embedd_and_upload)

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

        # ========================
        # State Machine Definition:
        # ========================
        #
        # ========================
        # Ingestion
        # ========================
        initialize_opensearch_task = tasks.LambdaInvoke(
            self, "Initialize Opensearch",
            lambda_function=initialize_opensearch,
            output_path="$.Payload"
        )

        get_venues_task = tasks.LambdaInvoke(
            self, "Get Venues",
            lambda_function=get_venues,
            input_path="$.Payload",
            output_path="$.Payload"
        )

        process_venue_task = tasks.LambdaInvoke(
            self, "Process Venue And Save Items",
            lambda_function=process_venue_items,
            input_path="$"
        )

        embedd_and_upload_task = tasks.LambdaInvoke(
            self, "Embedd And Upload Items",
            lambda_function=embedd_and_upload,
            input_path="$.Payload"
        )

        process_each_venue_task = sfn.Map(
            self, "Process Each Venue",
            max_concurrency=10,
            items_path="$.Payload",
            result_selector={"s.$": "$[*].Payload"},
            output_path="$.s"
        ).iterator(
            process_venue_task
            .next(embedd_and_upload_task)
        )

        refresh_choice = (sfn.Choice(self, "Refresh?", input_path="$")
            .when(
                sfn.Condition.is_present("$.Payload[0]"),
                process_each_venue_task
            )
            .otherwise(sfn.Succeed(self, "Nothing to ingest"))
        )

        # Define the State Machine
        sfn.StateMachine(
            self, "IngestMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                initialize_opensearch_task
                .next(get_venues_task)
                .next(refresh_choice)
            )
        )

        # ========================
        # Search
        # ========================
        search_task = tasks.LambdaInvoke(
            self, "Search",
            lambda_function=search
        )
        consult_task = tasks.LambdaInvoke(
            self, "Consult",
            lambda_function=consult
        )
        sfn.StateMachine(
            self, "SearchMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                search_task
                .next(consult_task)
            )
        )











        apiGateway = apigateway.RestApi(self, 'ApiGateway',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_credentials=True,
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "PUT"],
                allow_headers=["Content-Type", "Authorization", "Content-Length", "X-Requested-With"]
            )
        )

        api = apiGateway.root.add_resource('api')

        todos = api.add_resource('todos',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_credentials=True,
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization", "Content-Length", "X-Requested-With"]
            )
        )
        # todos.add_method('GET', apigateway.LambdaIntegration(getTodos))

        CfnOutput(self, ApiGatewayEndpointStackOutput,
            value=apiGateway.url
        )

        CfnOutput(self, ApiGatewayDomainStackOutput,
            value=apiGateway.url.split('/')[2]
        )

        CfnOutput(self, ApiGatewayStageStackOutput,
            value=apiGateway.deployment_stage.stage_name
        )
