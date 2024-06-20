import requests
import json
import os
import dotenv
from constants import *
import logging

dotenv.load_dotenv()

api_key = os.environ['TRELLO_API_KEY']
token = os.environ['TRELLO_TOKEN']
boards_id = os.environ['TRELLO_BOARDS_ID'].split(",")
boards = None

def get_whitelist_boards_id():
    get_boards()
    return_list = []
    for board in boards:
        if board["id"] in boards_id or boards_id == "all":
            return_list.append(board["id"])
    return return_list


def get_boards():
    global boards
    """Fetch all boards for the account and print their names and IDs."""
    url = f"https://api.trello.com/1/members/me/boards?key={api_key}&token={token}"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        boards = response.json()
        #for board in boards:
            #print(f"Board Name: {board['name']}, Board ID: {board['id']}")
    else:
        print(f"Failed to retrieve boards. Status code: {response.status_code}")
        print(response.text)

def get_one_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={api_key}&token={token}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def get_all_lists_from_boards():
    boards_list = []
    for board_id in get_whitelist_boards_id():
        # Base URL for Trello API
        base_url = "https://api.trello.com/1/"

        # Endpoint for getting all lists on the board
        url = f"{base_url}boards/{board_id}/lists"

        # Parameters for the API request
        query = {
            'key': api_key,
            'token': token
        }

        # Make a GET request to retrieve all lists on the board
        response = requests.get(url, params=query)

        # Check if the request was successful
        if response.status_code == 200:
            boards_list += response.json()
        else:
            print("Failed to retrieve lists. Status code:", response.status_code)
    if boards_list != []:
        return boards_list
    else:
        print("Failed to retrieve lists from every whitelist board.")
        return boards_list

def get_card_from_url(url):
    json_url = url + '.json'
    query = {
        'key': api_key,
        'token': token
    }
    response = requests.get(json_url, params=query)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def add_to_name_at_start(card, addition):
    card_id = card['id']
    url = f"https://api.trello.com/1/cards/{card_id}"


    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': api_key,
    'token': token,
    'name': addition + card['name'] 
    }

    response = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

def add_to_name(card, addition):
    card_id = card['id']
    url = f"https://api.trello.com/1/cards/{card_id}"


    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': api_key,
    'token': token,
    'name': card['name'] + addition
    }

    response = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

def add_to_desc(card, addition):
    card_id = card['id']
    url = f"https://api.trello.com/1/cards/{card_id}"


    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': api_key,
    'token': token,
    'desc': card['desc'] + addition
    }

    response = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

def edit_from_desc(card, old_value, new_value):
    card_id = card['id']
    url = f"https://api.trello.com/1/cards/{card_id}"


    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': api_key,
    'token': token,
    'desc': card['desc'].replace(old_value , new_value, 1)
    }

    response = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def edit_from_name(card, old_value, new_value):
    card_id = card['id']
    url = f"https://api.trello.com/1/cards/{card_id}"


    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': api_key,
    'token': token,
    'name': card['name'].replace(old_value , new_value, 1)
    }

    response = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def add_image_to_card(card_id, image_path):
    files = {'file': open(image_path, 'rb')}
    attachment_url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    requests.post(attachment_url, files=files, params={'key': api_key, 'token': token})
    logging.info("Card created with image attached")


def get_all_cards_from_boards():
    base_url = "https://api.trello.com/1/"
    headers = {"Accept": "application/json"}

    lists = get_all_lists_from_boards()

    all_cards = []

    # For each list, get all cards
    for list_ in lists:
        list_id = list_['id']
        cards_url = f"{base_url}lists/{list_id}/cards?key={api_key}&token={token}"
        cards_response = requests.get(cards_url, headers=headers)
        if cards_response.status_code == 200:
            cards = cards_response.json()
            all_cards.extend(cards)
        else:
            print(f"Failed to retrieve cards. Status code: {cards_response.status_code}")

    return all_cards

def create_n_put_label(card, label_name, label_color = "sky"):
    url = "https://api.trello.com/1/labels"
    querystring = {
        "key": api_key,
        "token": token,
        "name": label_name,
        "color": label_color,
        "idBoard": card["idBoard"]
    }

    response = requests.post(url, params=querystring)
    card_id = card["id"]


    if response.status_code == 200:
        value = None
        for key, value_ in response.json().items():
            if key == "id":
                value = value_

        url_2 = f"https://api.trello.com/1/cards/{card_id}/idLabels"

        query = {
        'key': api_key,
        'token': token,
        'value': value
        }

        response_2 = requests.request(
        "POST",
        url_2,
        params=query
        )

        if response_2.status_code == 200:
            return response_2.json()
        else:
            return None
    else:
        return None


def edit_label_name(label_id, new_name):
    url = f"https://api.trello.com/1/labels/{label_id}"
    querystring = {
        "key": api_key,
        "token": token,
        "name": new_name
    }

    response = requests.put(url, params=querystring)

    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        return None

def create_card(list_id, card_name):
    url = "https://api.trello.com/1/cards"

    headers = {
    "Accept": "application/json"
    }

    query = {
    'name': card_name,
    'idList': list_id,
    'key': api_key,
    'token': token
    }

    response = requests.request(
    "POST",
    url,
    headers=headers,
    params=query
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Use the function to get all cards from the specified board
get_boards()

# Print out the cards (for demonstration, you might want to process this data differently)
#print(json.dumps(cards, indent=4))  # This will print the cards data in a nicely formatted JSON string

# Your callback URL where Trello will send notifications
def change_card_list(card_id, idList):
    url = f'https://api.trello.com/1/cards/{card_id}/idList'
    params = {'key': api_key, 'token': token}
    data = {'value': idList}
    response = requests.put(url, params=params, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_user_id_by_name(username):
    url = f'https://api.trello.com/1/members/{username}'
    params = {'key': api_key, 'token': token}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        user_data = response.json()
        return user_data['id']
    else:
        return None

def trello_str_to_list(code_str):
        code = code_str.split(" ")
        i = 0
        while i < len(code):
            code[i] = int(code[i])
            i += 1
        assert len(code) == 4
        return code

def get_commands_set(str_):
    command_begings = str_.split("[" + TRELLO_CALL_CMD + " ")
    command_begings.pop(0)
    result = list()
    for beging in command_begings:
        split_close = beging.split("]")
        if len(split_close) > 1:
            if not "[" in split_close[0]:
                result.append(split_close[0])
    return result

def update_boards():
    global boards
    get_boards()
    return boards

def get_boards_var():
    global boards
    return boards





