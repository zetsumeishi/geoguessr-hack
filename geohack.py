#! /usr/bin/env python3
import json
import re

from geopy.geocoders import Nominatim

LANGUAGE = 'en'


def display_location(location):
    address = location.raw['address']
    for key, value in sorted(address.items()):
        # Only display useful information, ignore the rest
        if 'ISO3166' not in key and key not in ['postcode', 'country_code']:
            key = ' '.join(key.split('_'))
            print(f'\033[1m{key.title()}\033[0m: {value.title()}')
    print('\n')


def response(flow):
    url = flow.request.pretty_url
    adventure_pattern = r'^https:\/\/www\.geoguessr\.com\/api\/v4\/adventures\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\/move\/(\d+)'  # NOQA
    std_pattern = (
        r'^https:\/\/www\.geoguessr\.com\/api\/v3\/(games|challenges)\/[A-Za-z0-9]{16}'  # NOQA
    )

    geolocator = Nominatim(user_agent='Geoguessr')
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


def websocket_message(flow):
    """When playing in multiplayer, communication with the server is done via WebSockets"""
    message = flow.websocket.messages[-1]
    message_content = json.loads(message.content.decode())
    geolocator = Nominatim(user_agent='Geoguessr')
    if 'battleRoyaleGameState' in message_content and message_content['battleRoyaleGameState']:
        round = message_content['battleRoyaleGameState']['rounds'][-1]
        lat = round['lat']
        lng = round['lng']
        coordinates = (lat, lng)
        location = geolocator.reverse(coordinates, language='en', addressdetails=True)
        display_location(location)
