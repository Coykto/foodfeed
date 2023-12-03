import logging
from dependency.search_client import Search
from dependency.ai_client import AI

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    query = event.get("query", event.get("q"))
    max_price = event.get("max_price", 3000)
    if query is None:
        return {
            'statusCode': 400,
            'body': {'message': 'query is required'}
        }

    country = "geo"
    city = "tbilisi"

    search = Search()
    ai = AI()

    query_vector = ai.embedd_query(query)
    search_result = search.search_menu(
        index_name=f"{country}.{city}.food",
        vector=query_vector,
        max_price=max_price,
        size=20
    )

    return {'Payload': search_result}
