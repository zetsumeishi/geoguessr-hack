#! /usr/bin/env python3
import asyncio
import json

from cachetools import LRUCache
from geopy.geocoders import Nominatim

cache = LRUCache(maxsize=100)

LANGUAGE = 'en'

loop = asyncio.get_event_loop()

METADATA_URL = 'https://maps.googleapis.com/$rpc/google.internal.maps.mapsjs.v1.MapsJsInternalService/GetMetadata'  # NOQA


async def display_location(location):
    address = location.raw['address']
    for key, value in sorted(address.items()):
        # Only display useful information, ignore the rest
        if 'ISO3166' not in key and key not in ['postcode', 'country_code']:
            key = ' '.join(key.split('_'))
            print(f'\033[1m{key.title()}\033[0m: {value.title()}')
    print('\n')


async def get_location(coordinates):
    trimmed_coordinates = (round(coordinates[0], 1), round(coordinates[1], 1))
    cached_location = cache.get(trimmed_coordinates)

    if cached_location:
        return cached_location, True

    geolocator = Nominatim(user_agent='Geoguessr')
    try:
        location = await loop.run_in_executor(
            None,
            lambda: geolocator.reverse(coordinates, language='en', addressdetails=True),
        )
    except Exception as e:
        print(f'An error occurred with third party (Nominatim) API.\nError: {e}')

    cache[trimmed_coordinates] = location

    return location, False


async def response(flow):
    url = flow.request.pretty_url

    if flow.response.status_code == 200:
        if url == METADATA_URL and flow.response.content and flow.request.method == 'POST':
            response_content = json.loads(flow.response.content)
            lat = response_content[1][0][5][0][1][0][2]
            lng = response_content[1][0][5][0][1][0][3]
            location, cache_hit = await get_location((lat, lng))
            if not cache_hit:
                await display_location(location)
