from os import path
import os
from aws_cdk import Stack, CfnOutput

from aws_cdk import aws_iam as iam
from constructs import Construct
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_opensearchservice as opensearch
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, BundlingOptions
from aws_cdk import DockerImage


class CommonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.openai_api_key = self.node.try_get_context("OPENAI_API_KEY")

        self.search_domain = opensearch.Domain(
            self, 'food',
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
        self.search_domain.grant_read_write(iam.Group.from_group_name(self, "DevGroup", "admins"))

        layer_entry = path.join(os.getcwd(), 'python/lambdas')
        self.dependency_layer = PythonLayerVersion(
            self, 'DependencyLayer',
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            entry=layer_entry,
            bundling=BundlingOptions(image=DockerImage.from_build(
                path=f"{layer_entry}/dependency",
                file='Dockerfile'
            ))
        )
