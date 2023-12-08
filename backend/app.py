#!/usr/bin/env python3
import os

import aws_cdk as cdk

from python.python_stack import BackendStack

app = cdk.App()
BackendStack(
    app, 'Backend',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)
app.synth()
