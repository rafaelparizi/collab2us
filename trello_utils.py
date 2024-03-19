
# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json
import re

def auth(api_key, api_token):
    url = "https://api.trello.com/1/members/me/boards"
    headers = {
        "Accept": "application/json"
    }
    query = {
    'key': api_key,
    'token': api_token
    }
    response = requests.request("GET",url,headers=headers,params=query)

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    # data = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
    # print(data["name"])
    # for board in json.loads(response.text):
    #     print('------')
    #     print(board['name'])

    return response.json()

def verifica_board(api_key, api_token, board_name):
    url = "https://api.trello.com/1/members/me/boards"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': api_key,
        'token': api_token
    }
    response = requests.request("GET",url,headers=headers,params=query)
    
    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    data = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
    # print(data["name"])
    for board in json.loads(response.text):
        # print('------')
        # print(board['name'])
        if board['name'] == board_name:
            return True
    return False

def create_a_board(name, api_key, api_token):
    url = "https://api.trello.com/1/boards/"

    query = {
        'name': name,
        'key': api_key,
        'token': api_token
    }

    response = requests.request("POST",url,params=query)
    
    return response.json()
    # print(response.text)

def get_lists_on_a_board(board_id, api_key, api_token):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"

    headers = {
    "Accept": "application/json"
    }

    query = {
        'key': api_key,
        'token': api_token
    }

    response = requests.request(
    "GET",
    url,
    headers=headers,
    params=query
    )

    # print('\nListas do board')
    return json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))


def get_board_by_name(api_key, api_token, board_name):
    print(board_name)
    url = "https://api.trello.com/1/members/me/boards"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': api_key,
        'token': api_token
    }
    response = requests.request("GET",url,headers=headers,params=query)
    # print(f"Aqui o response: {response.text}")

    for board in json.loads(response.text):
        if (board_name == board['name']):
            return board
        
def get_cards_on_a_board(api_key, api_token, board_id):

    url = f"https://api.trello.com/1/boards/{board_id}/cards"

    query = {
        'key': api_key,
        'token': api_token
    }

    response = requests.request(
        "GET",
        url,
        params=query
    )

    return json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))

def create_a_label(name, idBoard, api_key, api_token,color="blue"):

    url = "https://api.trello.com/1/labels"

    # yellow, purple, blue, red, green, orange, black, sky, pink, lime

    query = {
    'name': name,
    'color': color,
    'idBoard': idBoard,
    'key': api_key,
    'token': api_token
    }

    response = requests.request(
    "POST",
    url,
    params=query
    )

    return response.json()

def create_a_card(story, list_id, api_key, api_token, list_of_labels_persona, list_of_labels_features, cards_on_the_board):

    # Expressão regular com grupos de captura para <x>, <y>, e <z>
    padrao = r"Como (.+?) eu gostaria de (.+?) para poder (.+?)$"

    # Buscando na frase usando o padrão definido
    resultado = re.search(padrao, story)

    if resultado:
        persona, pbi, feature = resultado.groups()
        # print(f"Persona: {persona}, y: {pbi}, z: {feature}")
        idLabels = ''
        for label in list_of_labels_persona:
            if persona in label['name']:
                idLabels = label['id']
                # print(f"Label: {label['color']} {idLabels}")
        
        for label in list_of_labels_features:
            if feature in label['name']:
                idLabels =  label['id'] + ',' + idLabels
                # print(f"Label: {label['color']} {idLabels}")

        cards = json.loads(cards_on_the_board)
        for card in cards:
            # print(f"Card: {card}")
            if card['name'] == pbi:
                print(f"Card já existe: {card['name']}")
                return
        
        if(idLabels != ''):
            url = "https://api.trello.com/1/cards"

            headers = {
            "Accept": "application/json"
            }

            query = {
                'name': pbi,
                'idList': list_id,
                'key': api_key,
                'token': api_token,
                'idLabels': idLabels,
                'desc': f"Como {persona} eu gostaria de {pbi} para poder {feature}"
            }

            response = requests.request(
            "POST",
            url,
            headers=headers,
            params=query
            )
            print('Card criado com sucesso')
            # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        else:
            print("Erro ao processar a user story.")


