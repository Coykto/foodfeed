from aws_cdk import Stack
from uuid import uuid4

from constructs import Construct

from python.stacks.common import setup_common
from python.stacks.search import setup_search
from python.stacks.api import setup_api
from python.stacks.ingestion import setup_ingestion
from python.stacks.telegram import setup_telegram

ApiGatewayEndpointStackOutput = 'ApiEndpoint'
ApiGatewayDomainStackOutput = 'ApiDomain'
ApiGatewayStageStackOutput = 'ApiStage'


class PythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.openai_api_key = self.node.try_get_context("OPENAI_API_KEY")
        self.telegram_secret_header = str(uuid4())
        self.telegram_token = self.node.try_get_context("TELEGRAM_TOKEN")

        dependency_layer, search_domain = setup_common(self)
        start_search = setup_search(self, dependency_layer, search_domain, self.openai_api_key, self.telegram_token)
        api, telegram_secret_header = setup_api(self, dependency_layer,)
        setup_ingestion(self, dependency_layer, search_domain, self.openai_api_key)
        setup_telegram(self, api, self.telegram_token, telegram_secret_header, dependency_layer)
