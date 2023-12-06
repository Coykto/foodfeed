#!/usr/bin/env python3
import os

import aws_cdk as cdk

from python.stacks.common import CommonStack
from python.stacks.api import ApiStack
from python.stacks.search import SearchStack
from python.stacks.telegram import TelegramStack
from python.stacks.ingestion import IngestionStack

app = cdk.App()
common_stack = CommonStack(
    app, 'CommonBackend',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)
search_stack = SearchStack(
    app, 'SearchBackend',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    dependency_layer=common_stack.dependency_layer,
    search_domain=common_stack.search_domain,
)
api_stack = ApiStack(
    app, 'ApiBackend',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    dependency_layer=common_stack.dependency_layer,
    start_search_lambda=search_stack.start_search,
)
ingestion_stack = IngestionStack(
    app, 'IngestionBackend',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    dependency_layer=common_stack.dependency_layer,
    search_domain=common_stack.search_domain,
)
telegram_stack = TelegramStack(
    app, 'TelegramBackend',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
    telegram_api_token=search_stack.telegram_token,
    telegram_secret_header=api_stack.telegram_secret_header,
    dependency_layer=common_stack.dependency_layer,
)

app.synth()
