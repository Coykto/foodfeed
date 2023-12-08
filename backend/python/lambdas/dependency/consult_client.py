import json
from typing import List, Dict
from .config.consultants_settings import consultants
from .wolt_client import Wolt
from .ai_client import AI


class ImaginedVenue(Exception):
    pass


class Consultant:

    def __init__(self, user_settings: Dict):
        self.user_settings = user_settings
        self.settings = consultants[user_settings["consultant"]]
        self.wolt = Wolt()
        self.ai = AI()

    def _filter_menu_items(self, menu_items: List) -> List:
        return [item for item in menu_items if self.wolt.check_venue(item["venue_slug"])]

    def _augment_query(self, query: str, menu_items: List, previous_orders: List) -> str:
        items_description = [
            f'{idx + 1}. {item["full_description"]}\nslug: {item["full_slug"]}'
            for idx, item in enumerate(self._filter_menu_items(menu_items))
        ]
        previous_orders = [f'{idx + 1}. {item["desc"]}' for idx, item in enumerate(previous_orders)]

        menu = "Menu Items:\n" + "\n\n---\n\n".join(items_description) + "\n\n-----\n\n"
        previous_orders = "Previous Orders:\n" + "\n\n---\n\n".join(previous_orders) + "\n\n-----\n\n"

        return f"{menu}{previous_orders}{query}"

    def _consult_ai(self, primer, query, max_attempts: int = 3, attempt: int = 0):
        try:
            ai_response = self.ai.chat(primer, query)
            venue_slug = ai_response["slug"].split("/")[0]
            if not self.wolt.check_venue(venue_slug):
                raise ImaginedVenue(f"The venue is likely imagined: `{venue_slug}`")
            return ai_response
        except (json.decoder.JSONDecodeError, ImaginedVenue, ValueError) as e:
            attempt += 1
            if attempt > max_attempts:
                raise e
            return self._consult_ai(primer, query, max_attempts, attempt)

    def consult(self, menu_items: List, query: Dict, user_settings: Dict):
        augmented_query = self._augment_query(query["query"], menu_items, user_settings["previous_orders"])
        primer = self.settings["primer"].replace("$LANGUAGE", query["language"])

        return self._consult_ai(primer, augmented_query)


