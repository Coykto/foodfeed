import logging
from dependency.consultant_client import Consultant
from dependency.storage_client import Storage
from dependency.utils import clean_string
from dependency.search_client import Search


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    search_result = event["search_result"]
    user_settings = event["user_settings"]
    query = event["query"]
    user_id = user_settings["user_id"]

    consultant = Consultant(user_settings)
    consultation = consultant.consult(search_result, query, user_settings)

    item_url = f"https://wolt.com/en/geo/tbilisi/venue/{consultation['slug']}"
    reason = clean_string(consultation["reason"])
    desc, _ = Search.detect_and_translate(clean_string(consultation["desc"]))

    if len(user_settings["previous_orders"]) >= user_settings["previous_orders_max_length"]:
        user_settings["previous_orders"] = user_settings["previous_orders"][1:] + [{"desc": desc}]
    else:
        user_settings["previous_orders"].append({"desc": desc})

    storage = Storage()
    storage.put_user_settings(user_id=user_id, data=user_settings)

    return {
        "url": item_url,
        "reason": reason,
        "user_id": user_id,
    }
