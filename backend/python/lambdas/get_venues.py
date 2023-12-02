import logging
import os
from dependency.search_client import Search
from dependency.storage_client import Storage
from dependency.wolt_client import Wolt

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def filter_out_indexed_venues(venues, index_name):
    indexed_venues = Search().indexed_venues(index_name)
    return [venue for venue in venues if venue.get('venue').get('slug') not in indexed_venues]


def lambda_handler(event, context):
    latitude = float(os.getenv('LATITUDE', 0.0))
    longitude = float(os.getenv('LONGITUDE', 0.0))

    country = "geo"
    city = "tbilisi"

    storage = Storage()
    wolt = Wolt()

    try:
        venues = wolt.get_venues(latitude, longitude)

        if not refresh:
            index_name = f"{country}.{city}.food"
            venues = filter_out_indexed_venues(venues, index_name)

        for venue in venues:
            storage.put_raw_venue(
                country=country,
                city=city,
                venue_slug=venue.get('venue').get('slug'),
                data=venue
            )

        logger.info(f"There are {len(venues)} venues to update")

    except Exception as error:
        error_msg = f"{error.__class__}: {error}"
        logger.error(error_msg)
        return {
            'statusCode': 500,
            'body': {'message': error_msg}
        }
    else:
        return {
            'Payload': [{"s": venue.get('venue').get('slug')} for venue in venues]
        }