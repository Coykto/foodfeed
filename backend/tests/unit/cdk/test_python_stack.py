import aws_cdk as core
import aws_cdk.assertions as assertions

from python.python_stack import PythonStack

def test_resources_created():
    app = core.App()
    stack = PythonStack(app, "python")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::S3::Bucket", 1)
    template.resource_count_is("AWS::Lambda::Function", 5)
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    template.resource_count_is("AWS::OpenSearchService::Domain", 1)
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
