index_settings = {
    "settings": {"index.knn": True},
    "aliases": {
        "food": {}
    },
    "mappings": {
        "properties": {
            # venue data
            "venue": {"type": "keyword"},
            "venue_slug": {"type": "keyword"},
            "venue_description": {"type": "keyword"},
            "venue_tags": {"type": "keyword"},
            "venue_rating": {"type": "float"},
            "venue_image": {"type": "keyword"},
            "estimate": {"type": "float"},

            # category data
            "category": {"type": "keyword"},
            "category_slug": {"type": "keyword"},
            "category_description": {"type": "keyword"},
            "category_image": {"type": "keyword"},

            # item data
            "image": {"type": "keyword"},
            "price": {"type": "integer"},
            "enabled": {"type": "boolean"},
            "tags": {"type": "keyword"},
            "name": {"type": "keyword"},
            "description": {"type": "text"},
            "full_slug": {"type": "keyword"},
            "full_description": {"type": "text"},

            # AI data
            "vector": {"type": "knn_vector", "dimension": 1536},
            "calories": {"type": "float"},
            "fat": {"type": "float"},
            "carbohydrates": {"type": "float"},
            "protein": {"type": "float"},
            "ingredients": {"type": "keyword"},
            "fiber": {"type": "float"},
            "sugar": {"type": "float"},
            "enriched": {"type": "boolean"}
        }
    }
}