from os import path
import os
from typing import Tuple

from aws_cdk import aws_iam as iam, Stack
import aws_cdk.aws_lambda as lambda_
from aws_cdk.aws_opensearchservice import Domain, CapacityConfig, EngineVersion
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, BundlingOptions
from aws_cdk import DockerImage


def setup_common(stack: Stack) -> Tuple[PythonLayerVersion, Domain]:
    search_domain = Domain(
        stack, 'food',
        version=EngineVersion.OPENSEARCH_2_9,
        domain_name='food',
        use_unsigned_basic_auth=True,
        capacity=CapacityConfig(
            master_nodes=2,
            master_node_instance_type='t3.small.search',
            data_nodes=1,
            data_node_instance_type='t3.small.search',
        )
    )
    search_domain.grant_read_write(iam.Group.from_group_name(stack, "DevGroup", "admins"))

    layer_entry = path.join(os.getcwd(), 'python/lambdas')
    dependency_layer = PythonLayerVersion(
        stack, 'DependencyLayer',
        compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
        entry=layer_entry,
        bundling=BundlingOptions(image=DockerImage.from_build(
            path=f"{layer_entry}/dependency",
            file='Dockerfile'
        ))
    )
    return dependency_layer, search_domain

