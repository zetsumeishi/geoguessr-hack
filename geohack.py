#! /usr/bin/env python3
import json
import re
from geopy.geocoders import Nominatim
import webbrowser
import asyncio
from cachetools import LRUCache

cache = LRUCache(maxsize=100)

LANGUAGE = 'en'

loop = asyncio.get_event_loop()

adventure_pattern = re.compile(r'^https:\/\/www\.geoguessr\.com\/api\/v4\/adventures\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\/move\/(\d+)')  # NOQA
standard_pattern = re.compile(r'^https:\/\/www\.geoguessr\.com\/api\/v3\/(games|challenges)\/[A-Za-z0-9]{16}')  # NOQA

async def display_location(location):
    address = location.raw['address']
    for key, value in sorted(address.items()):
        # Only display useful information, ignore the rest
        if 'ISO3166' not in key and key not in ['postcode', 'country_code']:
            key = ' '.join(key.split('_'))
            print(f'\033[1m{key.title()}\033[0m: {value.title()}')
    print('\n')

async def get_location(coordinates):
    cached_location = cache.get(coordinates)
    if cached_location:
        return cached_location
    geolocator = Nominatim(user_agent='Geoguessr')
    try:
        location = await loop.run_in_executor(
            None,
            lambda: geolocator.reverse(coordinates, language='en', addressdetails=True)
        )
    except Exception as e:
        print(f'An error occurred with third party (Nominatim) API.\nError: {e}')
    cache[coordinates] = location
    return location

async def response(flow):
    url = flow.request.pretty_url

    if flow.response.status_code == 200:
        if re.match(standard_pattern, url) and flow.request.method == 'GET':
            response_content = json.loads(flow.response.content.decode())
            # You have to check for the "creator" key because in daily challenge, one request matches
            # the RegExp before the game starts and doesn't contain a "rounds" key.
            if 'creator' not in response_content and response_content['rounds']:
                lat = response_content['rounds'][-1]['lat']
                lng = response_content['rounds'][-1]['lng']
                coordinates = (lat, lng)
                location = await get_location(coordinates)
                await display_location(location)
        elif re.match(adventure_pattern, url) and flow.request.method == 'POST':
            match = re.match(adventure_pattern, url)
            node_id = int(match.group(1))
            response_content = json.loads(flow.response.content.decode())
            for level in response_content.get('levels', []):
                for node in level.get('nodes', []):
                    if node['id'] == node_id and 'game' in node:
                        lat = node['game']['location']['lat']
                        lng = node['game']['location']['lng']
                        coordinates = (lat, lng)
                        location = await get_location(coordinates)
                        await display_location(location)
    if re.match(std_pattern, url) and flow.request.method == 'GET':
        response_content = json.loads(flow.response.content.decode())
        lat = response_content['rounds'][-1]['lat']
        lng = response_content['rounds'][-1]['lng']
        coordinates = (lat, lng)
        location = geolocator.reverse(coordinates, language='en', addressdetails=True)
        display_location(location)

    if re.match(adventure_pattern, url) and flow.request.method == 'POST':
        match = re.match(adventure_pattern, url)
        node_id = int(match.group(1))
        response_content = json.loads(flow.response.content.decode())
        for level in response_content.get('levels', []):
            for node in level.get('nodes', []):
                if node['id'] == node_id and 'game' in node:
                    lat = node['game']['location']['lat']
                    lng = node['game']['location']['lng']
                    coordinates = (lat, lng)
                    location = geolocator.reverse(coordinates, language='en', addressdetails=True)
                    display_location(location)

async def websocket_message(flow):
    message = flow.websocket.messages[-1]
    message_content = json.loads(message.content.decode())
    if 'code' in message_content and message_content['code'] == 'NewRound':
        round = message_content['battleRoyaleGameState']['rounds'][-1]
        coordinates = (round['lat'], round['lng'])
        location = await get_location(coordinates)
        await display_location(location)