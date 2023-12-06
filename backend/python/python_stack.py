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


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        openai_api_key = self.node.try_get_context("OPENAI_API_KEY")
        telegram_secret_header = str(uuid4())
        telegram_token = self.node.try_get_context("TELEGRAM_TOKEN")

        dependency_layer, search_domain = setup_common(self)
        search_machine = setup_search(self, dependency_layer, search_domain, openai_api_key)
        api = setup_api(self, dependency_layer, telegram_secret_header)
        setup_ingestion(self, dependency_layer, search_domain, openai_api_key)
        setup_telegram(self, dependency_layer, api, telegram_token, telegram_secret_header, search_machine)
