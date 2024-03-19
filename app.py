from flask import Flask, render_template, request
from miro_utils import *
from trello_utils import *
import re
# Importa a função do novo arquivo

# Sobre a API:https://developers.miro.com/reference/create-board
# lembrar de ativar o venv antes de rodar o servidor fazendo source venv/bin/activate
# para rodar o servidor, use python3 app.py


# access_token = 'eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_5wbiUEdXT7T5-7XHhwoiWMj_69M'  # Substitua pelo seu token de acesso
# # board_id = 'uXjVNwr5OJg='  # Substitua pelo ID do seu quadro

# trello_api_key = '752598cc2f3f789f11687a63d32d5a44'
# trello_token = 'ATTAf4604b615e0678c3c6d00a9427ea17c415932480f96ca903dfbfd4f55104c263723E0119'

access_token = ''
board_id = ''
trello_api_key = ''
trello_token = ''
miro_token = ''

app = Flask(__name__)


@app.route("/") 
def login():
    return render_template('/pages/login.html')

@app.route("/submit", methods=['POST'])
def submit():
    # captura o token de acesso
    miro_token = request.form['miro_token']
    trello_key = request.form['trello_key']
    trello_token = request.form['trello_token']

    access_token = miro_token

    # captura informações do miro (conectado)
    dados_acesso = extrair_dados(miro_token)

    if dados_acesso:
        boards_list = get_boards_by_team_id(dados_acesso['teamId'], access_token)
        # Passa os dados para o template
        return render_template('/pages/home.html', dados_usuario=dados_acesso, boards_list=boards_list, trello_api_key=trello_key, trello_token=trello_token, miro_token=miro_token)
    else:
        # TODO: Tratar erro
        return "Error: We couldn't get your data from Miro. Please, try again later---."

@app.route("/home", methods=['GET'])
def home():

    trello_key= request.args.get('trello_api_key')
    trello_token=request.args.get('trello_token')
    miro_token=request.args.get('miro_token')

    # captura informações do miro (conectado)
    dados_acesso = extrair_dados(access_token)
    # print(dados_acesso)

    if dados_acesso:
        boards_list = get_boards_by_team_id(dados_acesso['teamId'], access_token)
        # Passa os dados para o template
        return render_template('/pages/home.html', dados_usuario=dados_acesso, boards_list=boards_list, trello_api_key=trello_key, trello_token=trello_token, miro_token=miro_token)
    else:
        return "Error: We couldn't get your data from Miro. Please, try again later."

# @app.route("/user_stories/<selected_id>")
@app.route('/user_stories', methods=['GET'])
def user_stories():

    access_token = request.args.get('access_token')
    trello_api_key = request.args.get('trello_api_key')
    trello_token = request.args.get('trello_token')

    # print('----------')
    # print(trello_api_key)
    # print('----------')


    selected_id = request.args.get('selected_id')
    board_name = request.args.get('board_name')
    user_stories_created = []
    # captura informações do miro (conectado)
    dados_acesso_boards = extrair_dados_boards(access_token)
    # print(dados_acesso_boards)
    # print(board_name)

    
    extrair_dados(access_token)

    # print(selected_id)
    # captura os frames do board
    frames_list = get_frames(access_token, selected_id)


    list_of_stickers_personas = []
    list_of_stickers_features = []
    list_of_stickers_pbi = []
    for frame in frames_list:
        # print(frame)
        match frame.title:
            case "Personas":
                list_of_stickers_personas = get_stickers_by_frame(access_token, selected_id, frame)
            case "Features":
                list_of_stickers_features = get_stickers_by_frame(access_token, selected_id, frame)
            case "Product Backlog Items":
                list_of_stickers_pbi = get_stickers_by_frame(access_token, selected_id, frame)

    
    # # Preciso capturar as conexões dos stickers
    # stickers_conectados = encontra_stickers_conectados(connect_to_miro(access_token, selected_id)['data'])
    # for sticker in stickers_conectados:
    #     print(sticker)
    #     print(sticker[0]['text'])
    #     print(limpar_texto_connections(sticker[1]['text']))
    #     print('---')
    
    for sticker in list_of_stickers_personas:
        # print('\n')
        # print(f'Sticker: {sticker.content}')
        # print('---')

        # capturar os stickers conectados ao sticker atual (de personas)
        todos_stickers_conectados = encontrar_stickers_conectados_ao_sticker_completo(connect_to_miro(access_token, selected_id)['data'], sticker.id)

        # print('Level 1 - In features')
        nome = sticker.content
        id_geral = sticker.id

        for sticker in todos_stickers_conectados:
            # print('\t'+nome + ' conectado a ' + sticker['text'].replace("<p>", "").replace("</p>", ""))
            # capturar os stickers conectados ao sticker atual
            conectados_ao_level_2 = encontrar_stickers_conectados_ao_sticker_completo(connect_to_miro(access_token, selected_id)['data'], sticker['id'])

            # print('\nLevel 2')
            for sticker_lvl2 in conectados_ao_level_2:
                # para n˜çao repetir a conexão
                if(sticker_lvl2['id'] != id_geral):
                    # print('\t\t'+sticker['text'].replace("<p>", "").replace("</p>", "") + ' conectado a ' + sticker_lvl2['text'].replace("<p>", "").replace("</p>", ""))
                    # print('Como '+nome+' eu gostaria de '+sticker_lvl2['text'].replace("<p>", "").replace("</p>", "")+' para poder '+sticker['text'].replace("<p>", "").replace("</p>", ""))
                    user_stories_created.append('Como '+nome+' eu gostaria de '+sticker_lvl2['text'].replace("<p>", "").replace("</p>", "")+' para poder '+sticker['text'].replace("<p>", "").replace("</p>", ""))
        # print('::::')
        # print('\nFim da leitura das user stories')

    # TRELLO
    # print('Exportando para Trello')
    # print(f'Trello token: {trello_token}')
    # print(f'Trello key: {trello_api_key}')

    auth(trello_api_key, trello_token)
    # print(f"Resultado - ",verifica_board('752598cc2f3f789f11687a63d32d5a44', 'ATTAf4604b615e0678c3c6d00a9427ea17c415932480f96ca903dfbfd4f55104c263723E0119', board_name))

    if not (verifica_board(trello_api_key, trello_token, board_name)):
        # print("Criando board")
        response = create_a_board(board_name, trello_api_key, trello_token)
        if(response!= None):
            print("Board criado com sucesso")
        else:
            print('Erro ao criar board')
    else:
        print("Board já existe")

    board = get_board_by_name(trello_api_key, trello_token, board_name)

    # Cria labels para as personas para usar nos cards
    list_of_labels_persona = []

    colors = ['blue', 'green', 'orange', 'red', 'purple', 'yellow', 'black', 'sky', 'pink', 'lime']
    for i, persona in enumerate(list_of_stickers_personas):
        color_index = i % len(colors)  # Isso garante que o índice sempre esteja dentro do intervalo de cores disponíveis
        list_of_labels_persona.append(create_a_label('persona: '+persona.content, board['id'], trello_api_key, trello_token, color=colors[0]))
        # trocar 0 por color_index se quiser pegar cores diversas. 0 define azul
    list_of_labels_features = []
    for j, feature in enumerate(list_of_stickers_features):
        color_index = j % len(colors)
        list_of_labels_features.append(create_a_label(feature.content, board['id'], trello_api_key, trello_token, color=colors[1]))
        # trocar 1 por color_index se quiser pegar cores diversas. 1 define green

    # print('\nLabels criadas')
    # print(list_of_labels_persona)

    # print('\nLabels de features')
    # print(list_of_labels_features)

    lists_in_a_board = get_lists_on_a_board(board['id'], trello_api_key, trello_token)

    # print('\nLists in a board')
    data = json.loads(lists_in_a_board)
    cards_on_the_board = get_cards_on_a_board(trello_api_key, trello_token, board['id'])

    # # Todo: Como organizar os cards para passar o label correto?
    for item in data:
        if(item['name'] == 'To Do'):
            # print(user_stories_created)
            for story in user_stories_created:
                create_a_card(story, item['id'], trello_api_key, trello_token, list_of_labels_persona, list_of_labels_features, cards_on_the_board)


    return render_template('/pages/user_stories.html', stickers_personas=list_of_stickers_personas, stickers_features=list_of_stickers_features, stickers_pbi=list_of_stickers_pbi, dados_usuario=extrair_dados(access_token), user_stories_created = user_stories_created, board_name=board_name)


@app.route("/export_to_trello", methods=['GET'])
def export_to_trello():
    dados_usuario_json = request.args.get('dados_usuario')
    dados_usuario = json.loads(dados_usuario_json)
    # print('Dados de acesso!')
    # print(dados_usuario['user'])
    # dados_acesso = extrair_dados(access_token)
    # print('Exporting to Trello')
    return render_template('/pages/export_to_trello.html', dados_usuario=dados_usuario)


@app.route("/about")
def about():
    dados_acesso = extrair_dados(access_token)
    return render_template("/pages/about.html", dados_usuario=dados_acesso)





