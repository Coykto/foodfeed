import aws_cdk as core
import aws_cdk.assertions as assertions

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../../python"))
from python.python_stack import BackendStack


def test_resources_created():
    app = core.App(
        context={
            'OPENAI_API_KEY': "openai_api_key",
            'TELEGRAM_TOKEN': "telegram_token",
        }
    )
    stack = BackendStack(app, "python")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::S3::Bucket", 4)
    template.resource_count_is("AWS::Lambda::Function", 14)
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
