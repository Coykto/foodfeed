import logging
from dependency.search_client import Search
from dependency.ai_client import AI
from dependency.storage_client import Storage

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")
    user_id = event["message"]["from"]["id"]
    query = event["message"]["text"]

    country = "geo"
    city = "tbilisi"

    search = Search()
    ai = AI()
    storage = Storage()

    translation, original_language = search.detect_and_translate(query)
    query = {
        "query": translation,
        "language": original_language,
        "original_query": query
    }

    user_settings = storage.get_user_settings(user_id=user_id)
    query_vector = ai.embedd_query(query["query"])
    search_result = search.search_menu(
        index_name=f"{country}.{city}.food",
        vector=query_vector,
        search_settings={
            "max_price": user_settings["max_price"],
            "min_price": user_settings["min_price"],
            "max_delivery_time": user_settings["max_delivery_time"],
            "min_rating": user_settings["min_rating"],
        },
        size=20
    )

    return {
        "search_result": search_result,
        "user_settings": user_settings,
        "query": query
    }
