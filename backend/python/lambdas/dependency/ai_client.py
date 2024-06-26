import json
from typing import List

import openai
from .config.settings import settings


class AI:
    def __init__(self):
        self.client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self.embed_model = settings.OPENAI_EMBED_MODEL or "text-embedding-ada-002"

    def embedd_items(
        self,
        items: List[dict],
        embedd_field: str,
        enriched: bool = False,
    ) -> List[dict]:
        embeds = self._embedd(items, embedd_field)
        for index, item in enumerate(items):
            item["vector"] = embeds[index]
            item["enriched"] = enriched
        return items

    def embedd_query(self, query: str) -> List[float]:
        return self._embedd([{"query": query}], "query")[0]

    def _embedd(self, items, embedd_field, max_attempts: int = 3, attempt: int = 0):
        try:
            res = self.client.embeddings.create(
                input=[item[embedd_field] for item in items],
                model=self.embed_model
            )
            return [record.embedding for record in res.data]
        except Exception as e:
            if attempt == max_attempts:
                raise e
            return self._embedd(
                items,
                embedd_field,
                max_attempts,
                attempt + 1
            )

    def chat(self, primer, user_content, model: str = "gpt-4"):
        res = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7
        )
        return res.choices[0].message.content

    def enrich(
        self,
        item_full_text: str,
        item_url: str,
        enricher_settings: dict,
        max_attempts: int = 3,
        attempt: int = 0,
    ) -> dict:
        try:
            return json.loads(
                self.chat(
                    primer=enricher_settings["primer"],
                    user_content=[
                        {
                            "type": "text",
                            "text": item_full_text,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": item_url,
                                "detail": "low"
                            },
                        },
                    ],
                    model=enricher_settings["model"]
                )
            )
        except json.decoder.JSONDecodeError as e:
            if attempt >= max_attempts:
                raise e
            return self.enrich(
                item_full_text,
                item_url,
                enricher_settings,
                max_attempts,
                attempt + 1
            )
