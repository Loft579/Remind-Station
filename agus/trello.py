import requests
import dotenv
from constants import *
import logging

dotenv.load_dotenv()

api_key = os.environ['TRELLO_API_KEY']
token = os.environ['TRELLO_TOKEN']
board_id = os.environ['TRELLO_BOARD_ID']

def get_all_cards():
    base_url = "https://api.trello.com/1/"
    headers = {"Accept": "application/json"}

    # Get all lists on the board
    lists_url = f"{base_url}boards/{board_id}/lists?key={api_key}&token={token}"
    lists_response = requests.get(lists_url, headers=headers)

    lists_response.raise_for_status()
    
    lists = lists_response.json()

    all_cards = []

    # For each list, get all cards
    for list_ in lists:
        list_id = list_['id']
        cards_url = f"{base_url}lists/{list_id}/cards?key={api_key}&token={token}"
        cards_response = requests.get(cards_url, headers=headers)
        cards_response.raise_for_status()
        cards = cards_response.json()
        all_cards.extend(cards)

    return all_cards


def get_one_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={api_key}&token={token}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def edit_from_desc(card, old_value, new_value):
    card_id = card['id']
    url = f"https://api.trello.com/1/cards/{card_id}"


    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': api_key,
    'token': token,
    'desc': card['desc'].replace(old_value , new_value)
    }

    response = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )

    response.raise_for_status()
