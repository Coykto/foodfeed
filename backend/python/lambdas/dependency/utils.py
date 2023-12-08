import re


def clean_string(input_string):
    if input_string is None:
        return ""
    """
    Cleans the given string by removing unicode characters representing emojis and other non-text elements.
    """
    # Using the re library to remove non-ASCII characters
    import re
    clean_str = re.sub(r'[^\x00-\x7F]+', '', input_string)
    return clean_str


def clean_tags(tags):
    return [clean_string(tag["name"]).lower() for tag in tags]


def generate_full_text(item):
    name = item["name"]
    description = item["short_description"]
    tags = ', '.join(item["tags"])
    category = item["category"]
    category_description = item["category_description"]
    venue = item["venue"]
    venue_description = item["venue_description"]

    return (
        f"Name: {name}\n"
        f"Short Description: {description}\n"
        f"Tags: {tags}\n"
        f"Category: {category} - {category_description}\n"
        f"Venue: {venue}\n - {venue_description}"
    )


def clean_float(input_string):
    pattern = re.compile(r'([-+]?\d*\.\d+|\d+)')
    numbers = pattern.findall(input_string.split("/")[0])
    floats = list(map(float, numbers))
    return sum(floats) / len(floats)
