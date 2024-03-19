import requests
import json
from html import unescape
import re
from model.board import Board
from model.frame import Frame
from model.sticker import Sticker
# from board import Board



# capturar informações do miro
def extrair_dados(access_token):

    url = f"https://api.miro.com/v1/oauth-token"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        dados_extraidos = response.json()
        print(dados_extraidos)
        # print(response.json())
        # Extrai o nome do campo createdBy
        dados_extraidos = {
            'createdBy': response.json()['createdBy']['name'],
            'organization': response.json()['organization']['name'],
            'user': response.json()['user']['name'],
            'team': response.json()['team']['name'],
            'teamId': response.json()['team']['id'],
        }
        return dados_extraidos
    else:
        print(f"Erro ao acessar a API do Miro: {response.status_code}")
        return None

def extrair_dados_boards(access_token):

    url = f"https://api.miro.com/v1/oauth-token"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        dados_extraidos = response.json()
        # print(response.json())
        # Extrai o nome do campo createdBy
        dados_extraidos = {
            'team': response.json()['team']['name'],
        }
        return dados_extraidos
    else:
        print(f"Erro ao acessar a API do Miro: {response.status_code}")
        return None


def get_boards_by_team_id(teamId, access_token):
    url = f"https://api.miro.com/v1/teams/{teamId}/boards"
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # print(response.json())
        # Extrai o nome do campo createdBy
        # campos_desejados_lista = [{
        # "id": item['id'],
        # "type": item['type'],
        # "name": item['name'],
        # "description": item['description'],
        # "createdAt": item['createdAt'],
        # "createdBy": item['createdBy']
        # } for item in response.json()['data']]
        # print(campos_desejados_lista)
        # Criar uma lista de objetos Board a partir dos dados
        boards_lista = [Board(item['id'], item['type'], item['name'], item['description'], item['createdAt'], item['createdBy']) for item in response.json()['data']]

        # return campos_desejados_lista
        return boards_lista
    else:
        print(f"Erro ao acessar a API do Miro: {response.status_code}")
        return None




def extrair_e_limpar_texto_stickers(stickers):
    # Extrair os textos
    stickers_textos = [sticker['text'] for sticker in stickers['data'] if sticker['type'] == 'sticker']
    # Remover tags HTML e decodificar entidades HTML
    textos_limpos = [unescape(re.sub(r'<[^>]+>', '', texto)) for texto in stickers_textos]
    # print('lele')
    # print(textos_limpos)
    return textos_limpos


def connect_to_miro(access_token, board_id):
    url = f"https://api.miro.com/v1/boards/{board_id}/widgets?type=sticker"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao acessar a API do Miro: {response.status_code}")
        return None


def get_stickers(access_token, board_id):
    dados = ''
    stickers = connect_to_miro(access_token, board_id)
    # Processar os stickers aqui
    # print(stickers)
    if (stickers):
        dados = stickers
    return dados


def encontra_stickers_conectados(widgets):
    """
    Encontra pares de stickers conectados com base nas linhas de conexão entre eles.

    :param widgets: Lista de todos os widgets (incluindo stickers e linhas) de um quadro Miro.
    :return: Lista de tuplas, onde cada tupla contém os dados dos stickers conectados.
    """
    # Separar stickers e linhas
    stickers = {widget['id']: widget for widget in widgets if widget['type'] == 'sticker'}
    lines = [widget for widget in widgets if widget['type'] == 'line']

    # Inicializar lista para guardar pares de stickers conectados
    connected_pairs = []

    # Iterar sobre cada linha para encontrar stickers conectados
    for line in lines:
        # print(line)
        start_id = line['startWidget']['id']
        # print(start_id)
        end_id = line['endWidget']['id']
        # print(end_id)
        # Verificar se tanto o início quanto o fim da linha correspondem a stickers
        if start_id in stickers and end_id in stickers:
            # Adicionar o par de stickers conectados à lista
            start_sticker = stickers[start_id]
            end_sticker = stickers[end_id]
            connected_pairs.append((start_sticker, end_sticker))
    # print('Pares')
    # print(connected_pairs)
    return connected_pairs


def limpar_texto_connections(texto):
    # Substituir quebras de linha e outras sequências de espaço por um único espaço
    texto_sem_html = unescape(re.sub(r'<[^>]+>', '', texto))
    texto_limpo = re.sub(r'\s+', ' ', texto_sem_html)
    # print(texto)
    return texto_limpo


def remover_tags_html(array_entrada):
    # Remove as tags <p> e </p> de cada elemento do array
    array_saida = [(texto.replace('<p>', '').replace('</p>', ''), descricao) for texto, descricao in array_entrada]
    return array_saida


def gerar_user_stories_corrigidas(conexoes):
    user_stories_corrigidas = []
    id = 0
    for texto_array in conexoes:
        id=id+1
        # Extrair e ajustar a parte 1
        parte_1 = texto_array[0].replace("Persona: ", "")

        # Encontrar e dividir o texto baseado em "para"
        encontrar_para = texto_array[1].find(' para')
        if encontrar_para != -1:
            # Considerar o espaço antes de "para" para a Parte 2
            parte_2 = texto_array[1][:encontrar_para]
            parte_3 = texto_array[1][encontrar_para + 5:]  # +5 para pular " para"
        else:
            parte_2 = texto_array[1]
            parte_3 = ''

        # Gerar a User Story com as partes ajustadas
        user_story = f"US #{id}: Como {parte_1}, eu gostaria de {parte_2} para poder {parte_3}".strip()
        user_stories_corrigidas.append(user_story)

    return user_stories_corrigidas




#  NOVOS


# Capturar os frames do board e devolve uma lista de frames
def get_frames(access_token, board_id):
    dados = ''
    url = f"https://api.miro.com/v2/boards/{board_id}/items?type=frame"
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)
    # print(response.json()['data'])
    # for item in response.json()['data']:
    #     print(item['id'])
    #     print(item['data']['title'])

    if response.status_code == 200:
        # Criar uma lista de objetos frame a partir dos dados
        frames_lista = [Frame(item['id'], item['data']['title']) for item in response.json()['data']]

        # print(frames_lista)
        # return campos_desejados_lista
        return frames_lista
    else:
        print(f"Erro ao acessar a API do Miro: {response.status_code}")
        return None


def get_stickers_by_frame(access_token, board_id, frame):
    url = f"https://api.miro.com/v2/boards/{board_id}/items?parent_item_id={frame.id}&type=sticky_note"
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    }

    # print("\n\nFRAME "+frame.title)
    response = requests.get(url, headers=headers)
    # print(response.json()['data'])
    # for item in response.json()['data']:
    #     print(item['id'])
    #     print(limpar_texto_connections(item['data']['content']))

    if response.status_code == 200:
        # Criar uma lista de objetos frame a partir dos dados
        stickers_lista = [Sticker(item['id'], item['data']['content'].replace('<p>', '').replace('</p>', ''), frame.title) for item in response.json()['data']]

        # print(stickers_lista)
        # return campos_desejados_lista
        return stickers_lista
    else:
        print(f"Erro ao acessar a API do Miro: {response.status_code}")
        return None

# def get_sticker_by_id()
    
def criar_mapa_conexoes(widgets):
    """
    Cria um mapa de conexões entre stickers com base nas linhas de conexão entre eles.

    :param widgets: Lista de todos os widgets (incluindo stickers e linhas) de um quadro Miro.
    :return: Dicionário onde cada chave é o ID de um sticker e o valor é uma lista de stickers conectados.
    """
    stickers = {widget['id']: widget for widget in widgets if widget['type'] == 'sticker'}
    lines = [widget for widget in widgets if widget['type'] == 'line']

    conexoes = {}

    for line in lines:
        start_id = line.get('startWidget', {}).get('id')
        end_id = line.get('endWidget', {}).get('id')

        if start_id in stickers and end_id in stickers:
            if start_id not in conexoes:
                conexoes[start_id] = []
            if end_id not in conexoes:
                conexoes[end_id] = []

            conexoes[start_id].append(stickers[end_id])
            conexoes[end_id].append(stickers[start_id])

    return conexoes

def encontrar_stickers_conectados_a(widgets, sticker_id):
    """
    Encontra todos os stickers conectados a um sticker específico.

    :param widgets: Lista de todos os widgets de um quadro Miro.
    :param sticker_id: ID do sticker do qual queremos encontrar os conectados.
    :return: Lista de stickers conectados ao sticker especificado.
    """
    conexoes = criar_mapa_conexoes(widgets)
    return conexoes.get(sticker_id, [])


def encontrar_stickers_conectados_ao_sticker(widgets, sticker_id):
    """
    Dado um sticker, encontra todos os stickers conectados a ele.

    :param widgets: Lista de todos os widgets (incluindo stickers e linhas) de um quadro Miro.
    :param sticker_id: ID do sticker para o qual encontrar stickers conectados.
    :return: Lista de IDs dos stickers conectados ao sticker especificado.
    """
    # Primeiro, obtenha todos os pares de stickers conectados
    connected_pairs = encontra_stickers_conectados(widgets)
    
    # Inicializar a lista para guardar os IDs dos stickers conectados
    connected_sticker_ids = []

    # Iterar sobre os pares conectados para encontrar conexões que envolvem o sticker de interesse
    for start_sticker, end_sticker in connected_pairs:
        # Se o sticker de interesse for o sticker de partida, adicione o sticker de chegada à lista
        if start_sticker['id'] == sticker_id:
            connected_sticker_ids.append(end_sticker['id'])
        # Se o sticker de interesse for o sticker de chegada, adicione o sticker de partida à lista
        elif end_sticker['id'] == sticker_id:
            connected_sticker_ids.append(start_sticker['id'])

    return connected_sticker_ids

def encontrar_todos_stickers_conectados(widgets, sticker_id_inicial):
    """
    Encontra todos os stickers conectados ao sticker fornecido, direta ou indiretamente.

    :param widgets: Lista de todos os widgets (incluindo stickers e linhas) de um quadro Miro.
    :param sticker_id_inicial: ID do sticker inicial.
    :return: Conjunto de IDs dos stickers conectados ao sticker inicial, incluindo conexões indiretas.
    """
    # Obter todos os pares de stickers conectados
    connected_pairs = encontra_stickers_conectados(widgets)

    # Inicializar uma fila com o sticker inicial e um conjunto para manter o controle dos visitados
    a_visitar = [sticker_id_inicial]
    visitados = set()

    # Enquanto houver stickers na fila para verificar...
    while a_visitar:
        sticker_atual = a_visitar.pop(0)  # Remove e retorna o primeiro elemento da fila
        visitados.add(sticker_atual)  # Marcar o sticker atual como visitado

        # Para cada par conectado, verificar se o sticker atual está conectado a outros
        for start_sticker, end_sticker in connected_pairs:
            if sticker_atual == start_sticker['id'] and end_sticker['id'] not in visitados:
                # Se o sticker conectado não foi visitado, adicione à fila e ao conjunto de visitados
                a_visitar.append(end_sticker['id'])
                visitados.add(end_sticker['id'])
            elif sticker_atual == end_sticker['id'] and start_sticker['id'] not in visitados:
                # Mesmo que acima, mas verificando a outra direção da conexão
                a_visitar.append(start_sticker['id'])
                visitados.add(start_sticker['id'])

    # Retorna todos os stickers visitados, excluindo o sticker inicial se necessário
    visitados.remove(sticker_id_inicial)  # Opcional, depende se você quer incluir o inicial na lista de resultados
    return visitados

def encontrar_stickers_conectados_ao_sticker_completo(widgets, sticker_id):
    """
    Dado um sticker, encontra todos os stickers conectados a ele e retorna os objetos sticker completos.

    :param widgets: Lista de todos os widgets (incluindo stickers e linhas) de um quadro Miro.
    :param sticker_id: ID do sticker para o qual encontrar stickers conectados.
    :return: Lista dos objetos stickers conectados ao sticker especificado.
    """
    # Primeiro, obtenha todos os pares de stickers conectados
    connected_pairs = encontra_stickers_conectados(widgets)
    
    # Inicializar a lista para guardar os objetos dos stickers conectados
    connected_stickers = []

    # Iterar sobre os pares conectados para encontrar conexões que envolvem o sticker de interesse
    for start_sticker, end_sticker in connected_pairs:
        # Se o sticker de interesse for o sticker de partida, adicione o sticker de chegada à lista
        if start_sticker['id'] == sticker_id:
            connected_stickers.append(end_sticker)
        # Se o sticker de interesse for o sticker de chegada, adicione o sticker de partida à lista
        elif end_sticker['id'] == sticker_id:
            connected_stickers.append(start_sticker)

    return connected_stickers


