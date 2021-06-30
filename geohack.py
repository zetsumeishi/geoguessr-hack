#! /usr/bin/env python3
import json
import re
import webbrowser

import pycountry
import us
from geopy.geocoders import Nominatim

LANGUAGE = 'en'


def response(flow):
    """Called when a server response has been received."""

    unranked_url = r'https://www.geoguessr.com/api/v3/games/\w{16}'
    ranked_url_pattern = r'^https://game-server.geoguessr.com/api/battle-royale/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/reconnect$'  # NOQA
    challenges_url_pattern = r'https://www.geoguessr.com/api/v3/challenges/\w{16}'

    is_unranked = re.match(unranked_url, flow.request.url) is not None
    is_ranked = re.match(ranked_url_pattern, flow.request.url) is not None
    is_challenge = re.match(challenges_url_pattern, flow.request.url) is not None
    if (
        flow.request.method != 'GET'
        or not is_ranked
        and not is_unranked
        and not is_challenge
    ):
        return

    # We retrieve the response content in a dict
    response_content = json.loads(flow.response.content.decode())
    geolocator = Nominatim(user_agent='Geoguessr')
    if response_content:
        if is_unranked or is_challenge:
            game_mode = response_content['mode']
            streak_type = response_content['streakType']
            round_index = response_content['round'] - 1
            current_round = response_content['rounds'][round_index]
            latitude = current_round['lat']
            longitude = current_round['lng']
            coordinates = (latitude, longitude)
            webbrowser.get(using='google-chrome').open_new_tab(
                f'https://www.google.com/maps/place/{latitude},{longitude}',
            )
            if game_mode == 'streak':
                if streak_type == 'usstatestreak':
                    state = us.states.lookup(current_round['streakLocationCode'])
                    print(f'{state.name}, {state.abbr}')
                elif streak_type == 'countrystreak':
                    country_code = current_round['streakLocationCode']
                    country = pycountry.countries.get(alpha_2=country_code)
                    print(country.name)
            elif game_mode == 'standard':
                location = geolocator.reverse(coordinates, language=LANGUAGE)
                print(location.address)
        elif is_ranked:
            current_round = response_content['rounds'][-1]
            latitude = current_round['lat']
            longitude = current_round['lng']
            coordinates = (latitude, longitude)
            if response_content['isDistanceGame']:
                # webbrowser.get(using='google-chrome').open_new_tab(
                #     f'https://www.google.com/maps/place/{latitude},{longitude}',
                # )
                location = geolocator.reverse(coordinates, language=LANGUAGE)
                print(location.address)
            else:
                location = geolocator.reverse(coordinates, language=LANGUAGE)
                print(location.address)


def websocket_message(flow):
    message = flow.messages[-1]
    if 'StreakNewRound' in message.content:
        response = json.loads(message.content)
        geolocator = Nominatim(user_agent='Geoguessr')
        latitude = response['payload']['round']['lat']
        longitude = response['payload']['round']['lng']
        coordinates = (latitude, longitude)
        location = geolocator.reverse(coordinates, language=LANGUAGE)
        print(location.address)
