from os import path
import os
from aws_cdk import (
    StackProps,
    Stack,
    CfnOutput
)
from constructs import Construct
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_apigateway as apigateway
import aws_cdk.aws_dynamodb as dynamodb
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

    def __init__(self, scope: Construct, construct_id: str, openai_api_key: str = None, **kwargs) -> None:
        self.openai_api_key = openai_api_key
        super().__init__(scope, construct_id, **kwargs)

        """
        ingestion pipeline:
        - one lambda to get venues in town
        - one lambda to get all categories and their menu items from one venue
        - parse results to individual menu items
        - create embeddings for each menu item
        - upload all menu items to OpenSearch with "enriched" flag set to False
        """

        # ========================
        # Storage Infrastructure
        # ========================
        food_search_domain = opensearch.Domain(self, 'Domain',
            version=opensearch.EngineVersion.OPENSEARCH_2_9,
            domain_name='foodfeed-opensearch',
            capacity=opensearch.CapacityConfig(
                master_nodes=2,
                master_node_instance_type='t3.small.search',
                data_nodes=1,
                data_node_instance_type='t3.small.search',
            ),
            use_unsigned_basic_auth=True
        )

        raw_venues_bucket = s3.Bucket(self, 'rawVenues')
        processed_venues_bucket = s3.Bucket(self, 'processedVenues')
        enriched_venues_bucket = s3.Bucket(self, 'enrichedVenues')  # TODO: enrichment process (read images)

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

        get_venues = lambda_.Function(self,'getVenues',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!get_venues.py"]
            ),
            handler='get_venues.lambda_handler',
            timeout=Duration.seconds(10),
            environment={
                "VENUES_ENDPOINT": "https://consumer-api.wolt.com/v1/pages/restaurants",
                "LATITUDE": "41.72484116869996",
                "LONGITUDE": "44.72807697951794",
                "RAW_VENUES_BUCKET": raw_venues_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        raw_venues_bucket.grant_read_write(get_venues)

        process_venue_items = lambda_.Function(self,'getVenueItems',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                path.join(os.getcwd(), 'python/lambdas'),
                exclude=["**", "!process_venue_items.py"]
            ),
            handler='process_venue_items.lambda_handler',
            timeout=Duration.seconds(60),
            environment={
                "BASE_HOST": "https://restaurant-api.wolt.com/v4/venues/slug/",
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
            environment={
                "OPENSEARCH_ENDPOINT": food_search_domain.domain_endpoint,
                "OPENAI_API_KEY": str(os.getenv("OPENAI_API_KEY", '')),
                "PROCESSED_VENUES_BUCKET": processed_venues_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        food_search_domain.grant_read_write(embedd_and_upload)
        processed_venues_bucket.grant_read(embedd_and_upload)

        # ========================
        # Step-Machine Definition:
        # ========================
        get_venues_task = tasks.LambdaInvoke(
            self, "Get Venues",
            lambda_function=get_venues,
            output_path="$.Payload"  # Adjust according to your Lambda's output
        )

        process_venue_task = tasks.LambdaInvoke(
            self, "Process Venue And Save Items",
            lambda_function=process_venue_items,
            input_path="$"  # Pass each object to process_venue_items
        )

        process_each_venue_task = sfn.Map(
            self, "Process Each Venue",
            max_concurrency=10,  # Adjust as needed
            items_path="$.Payload"  # Adjust according to your Lambda's output
        ).iterator(process_venue_task)

        embedd_and_upload_task = tasks.LambdaInvoke(
            self, "Embedd And Upload Items",
            lambda_function=embedd_and_upload,
            input_path="$"
        )

        # Define the State Machine
        sfn.StateMachine(
            self, "FoodIngestionStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                get_venues_task
                .next(process_each_venue_task)
                .next(embedd_and_upload_task)
            )
        )









        # ========================
        ddb = dynamodb.Table(self, 'TodosDB',
            partition_key=dynamodb.Attribute(
                name='id',
                type=dynamodb.AttributeType.STRING
            )
        )

        getTodos = lambda_.Function(self, 'getTodos',
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.AssetCode.from_asset(path.join(os.getcwd(), 'python/lambdas')),
            handler='get_todos.lambda_handler',
            environment={
                "DDB_TABLE": ddb.table_name,
                "SEARCH_ENDPOINT": food_search_domain.domain_endpoint
            },
            tracing=lambda_.Tracing.ACTIVE
        )
        ddb.grant_read_data(getTodos)

        apiGateway = apigateway.RestApi(self, 'ApiGateway',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_credentials=True,
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "PUT", "DELETE", "OPTIONS"],
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
        todos.add_method('GET', apigateway.LambdaIntegration(getTodos))

        CfnOutput(self, ApiGatewayEndpointStackOutput,
            value=apiGateway.url
        )

        CfnOutput(self, ApiGatewayDomainStackOutput,
            value=apiGateway.url.split('/')[2]
        )

        CfnOutput(self, ApiGatewayStageStackOutput,
            value=apiGateway.deployment_stage.stage_name
        )