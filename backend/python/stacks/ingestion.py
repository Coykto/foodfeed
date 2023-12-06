import os
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import Duration
import aws_cdk.aws_s3 as s3


def setup_ingestion(scope, dependency_layer, search_domain, openai_api_key):
        raw_venues_bucket = s3.Bucket(scope, 'rawVenues')
        processed_venues_bucket = s3.Bucket(scope, 'processedVenues')

        initialize_opensearch = lambda_.Function(
            scope, 'initializeOpensearch',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), 'python/lambdas/ingestion'),
                exclude=["**", "!initialize_opensearch.py"]
            ),
            handler='initialize_opensearch.lambda_handler',
            timeout=Duration.seconds(30),
            environment={"OPENSEARCH_ENDPOINT": search_domain.domain_endpoint},
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        search_domain.grant_read_write(initialize_opensearch)

        get_venues = lambda_.Function(
            scope,'getVenues',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), 'python/lambdas/ingestion'),
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

        process_venue_items = lambda_.Function(
            scope,'getVenueItems',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), 'python/lambdas/ingestion'),
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

        embedd_and_upload = lambda_.Function(
            scope,'embeddAndUpload',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.AssetCode.from_asset(
                os.path.join(os.getcwd(), 'python/lambdas/ingestion'),
                exclude=["**", "!embedd_and_upload.py"]
            ),
            handler='embedd_and_upload.lambda_handler',
            timeout=Duration.seconds(300),
            environment={
                "OPENSEARCH_ENDPOINT": search_domain.domain_endpoint,
                "OPENAI_API_KEY": openai_api_key,
                "PROCESSED_VENUES_BUCKET": processed_venues_bucket.bucket_name,
            },
            tracing=lambda_.Tracing.ACTIVE,
            layers=[dependency_layer]
        )
        search_domain.grant_read_write(embedd_and_upload)
        processed_venues_bucket.grant_read(embedd_and_upload)

        # ========================
        # State Machine Definition:
        # ========================
        initialize_opensearch_task = tasks.LambdaInvoke(
            scope, "Initialize Opensearch",
            lambda_function=initialize_opensearch,
            output_path="$.Payload"
        )

        get_venues_task = tasks.LambdaInvoke(
            scope, "Get Venues",
            lambda_function=get_venues,
            input_path="$.Payload",
            output_path="$.Payload"
        )

        process_venue_task = tasks.LambdaInvoke(
            scope, "Process Venue And Save Items",
            lambda_function=process_venue_items,
            input_path="$"
        )

        embedd_and_upload_task = tasks.LambdaInvoke(
            scope, "Embedd And Upload Items",
            lambda_function=embedd_and_upload,
            input_path="$.Payload"
        )

        process_each_venue_task = sfn.Map(
            scope, "Process Each Venue",
            max_concurrency=10,
            items_path="$.Payload",
            result_selector={"s.$": "$[*].Payload"},
            output_path="$.s"
        ).iterator(
            process_venue_task
            .next(embedd_and_upload_task)
        )

        refresh_choice = (sfn.Choice(scope, "Refresh?", input_path="$")
            .when(
                sfn.Condition.is_present("$.Payload[0]"),
                process_each_venue_task
            )
            .otherwise(sfn.Succeed(scope, "Nothing to ingest"))
        )

        sfn.StateMachine(
            scope, "IngestMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                initialize_opensearch_task
                .next(get_venues_task)
                .next(refresh_choice)
            )
        )


