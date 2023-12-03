index_settings = {
    "settings": {"index.knn": True},
    "aliases": {
        "food": {}
    },
    "mappings": {
        "properties": {
            # venue data
            "estimate": {"type": "float"},
            "venue": {"type": "keyword"},
            "venue_description": {"type": "keyword"},
            "venue_image": {"type": "keyword"},
            "venue_rating": {"type": "float"},
            "venue_slug": {"type": "keyword"},
            "venue_tags": {"type": "keyword"},

            # category data
            "category": {"type": "keyword"},
            "category_slug": {"type": "keyword"},
            "category_description": {"type": "keyword"},
            "category_image": {"type": "keyword"},

            # item data
            "description": {"type": "text"},
            "enabled": {"type": "boolean"},
            "full_description": {"type": "text"},
            "full_slug": {"type": "keyword"},
            "image": {"type": "keyword"},
            "name": {"type": "keyword"},
            "price": {"type": "integer"},
            "tags": {"type": "keyword"},

            # AI data
            "calories": {"type": "float"},
            "carbohydrates": {"type": "float"},
            "enriched": {"type": "boolean"},
            "fat": {"type": "float"},
            "fiber": {"type": "float"},
            "ingredients": {"type": "keyword"},
            "protein": {"type": "float"},
            "sugar": {"type": "float"},
            "vector": {"type": "knn_vector", "dimension": 1536},
        }
    }
}