from flask import jsonify, request, Blueprint
from psycopg2.extensions import AsIs
from . import *
from .functions import *
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4


endpoints = Blueprint('endpoints', __name__)

logger = start_logger()

#TODO em geral:
"""
-> notificaçoes para um user
    - termino de um leilao em que participou ou criou

-> terminaçao de um leilao a uma hora especifica
    - fazer um endpoint q passa por todos os leiloes e vê se ja acabou a hora
    - sempre q um user tenta licitar num leilao, chamar o endpoint acima para verifar se ja acabou
    - trigger para limpar tudo assciado a esse leilao: leilao, mensagens, historico, ...

-> Todos os utilizadores que tiverem escrito num mural passam a ser notificados acerca de mensagens escritas nesse
mesmo mural

->

"""

#Default page
@endpoints.route('/dbproj/') 
def home():
    logger.info("Home page") 
    return """
    <center>
        Projeto da cadeira de Base de Dados<br>
        FCTUC - DEI / 2020-2021
        <h1> Auction House </h1>
            <br>
            <br>
            Membros:
            <br>
            Alexandre Andrade - 2019220216
            <br>
            Tomás Mendes - 2019232272
    </center>
    """


@endpoints.route("/dbproj/user", methods=['POST', 'PUT'], strict_slashes=True)
def user():
    conn = db_connection()
    cursor = conn.cursor()
    info_user = request.get_json()

    if request.method == 'PUT': #PUT - login de utilizador
        logger.info("#### PUT - dbproj/user -> Login ####")

        try:
            cursor.execute("SELECT username, password, userid FROM utilizador WHERE username = %s", (info_user["username"], ) )
            info = cursor.fetchone()
        except:
            return {'erro' : 'SELECT username, password, userid FROM utilizador'}

        if info == None:
            logger.debug("Utilizador nao existe")
            conn.close()
            return {'erro': 'utilizador nao existe'}
        else:
            if check_password_hash(info[1], info_user["password"]):
                #verificar se este user ja tem um token na tabela authtokens
                try:
                    cursor.execute("SELECT token FROM authtokens WHERE utilizador_userid = %s", (info[2],))
                    aux = cursor.fetchone()
                except:
                    return {'erro' : 'SELECT token FROM authtokens'}
                #se nao tiver um token associado ao user, gerar token e inserir na tabela
                if aux is None:
                    while True:
                        token = str(uuid4())
                        try:
                            cursor.execute("INSERT INTO authtokens (utilizador_userid, token) VALUES (%s, %s)", (info[2], token))
                            conn.commit()
                            break;
                        except:
                            conn.rollback()
                            logger.debug(f"Token generated already existed!")
                        
                    logger.debug(f"Login: {info[0]} -> id: {info[2]}")
                    conn.close()
                    return {'authToken': token}
                else: #user ja tem um token
                    x = check_token(aux[0])
                    if x == 'Valid':
                        logger.debug("User ja fez login")
                        conn.close()
                        return {'warning': 'user ja fez login', 'authToken' : aux[0]}

                    elif x == 'Expired': # Expired
                        try:
                            token = str(uuid4())
                            cursor.execute("INSERT INTO authtokens (utilizador_userid, token) VALUES (%s, %s)", (info[2], token))
                            conn.close()
                            return {'warning': 'token has expired', 'new token' : token}
                        except:
                            return {'erro': 'An error occurred'}
                    else:
                        conn.close()
                        return {'erro': "tokens does't exist"}
            else:
                logger.debug("Erro de autenticacao")
                conn.close()
                return {'erro': 'AuthError'}

    elif request.method == 'POST': # POST - registo de utilizador
        logger.info("#### POST - dbproj/user -> Sign up ####")

        statement = "INSERT INTO utilizador (username, email, password) VALUES (%s, %s, %s);"
        values = (info_user["username"], info_user["email"], generate_password_hash(info_user["password"], method='sha256'))

        #verificar se o username ja esta registado
        get_user_querry = "SELECT userid FROM utilizador WHERE username = %s;"
        try:
            cursor.execute(get_user_querry, (info_user["username"],) )
            info = cursor.fetchone()
        except:
            conn.close()
            return{'erro' : 'SELECT userid FROM utilizador'}

        #verificar se o email ja esta registado
        try:
            cursor.execute("SELECT userid FROM utilizador WHERE email = %s;", (info_user["email"],) )
            info_aux = cursor.fetchone()
        except:
            conn.close()
            return{'erro' : 'SELECT userid FROM utilizador WHERE email = '}

        if info is None and info_aux is None: # se for None -> ainda nao existe na bd
            try:
                cursor.execute(statement, values)
                conn.commit()
                cursor.execute(get_user_querry, (info_user["username"], ) )
                info = cursor.fetchone()
                logger.debug(f"User {info[0]} created")
                conn.close()
                return {'userid': info[0]}
            except:
                conn.rollback()
                conn.close()
                return {'erro': 'Sign-up Failed'}
        elif info is not None:
            logger.debug("username ja registado")
            conn.close()
            return {'erro': 'username ja registado'}
        else:
            logger.debug("email ja registado")
            conn.close()
            return {'erro': 'email ja registado'}


@endpoints.route("/dbproj/leilao", methods=['POST'], strict_slashes=True)
def leilao_create():
    logger.info("#### POST - dbproj/leilao -> Criar leilao ####")

    conn = db_connection()
    cursor = conn.cursor()
    info_leilao = request.get_json()
    
    result = check_token(info_leilao["userAuthToken"])

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}

    elif result == 'Valid':
        if request.method == 'POST': # POST - criar leilao
            statement = "SELECT id FROM artigos WHERE id = %s;"
            cursor.execute(statement, (info_leilao["artigoId"], ))
            artigo = cursor.fetchone()
            if artigo is None:
                conn.close()
                return {'erro': 'artigo nao existe!'}
            else:
                userid = get_userid_from_token(info_leilao["userAuthToken"])
                if userid == 0:
                    conn.close()
                    return {'erro': "user doesn't exist!"}
                try:
                    statement = "INSERT INTO leilao (titulo, descricao, precomin, data, artigos_id, utilizador_userid) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
                    cursor.execute(statement, (info_leilao["titulo"], info_leilao["descricao"], info_leilao["precomin"], info_leilao["endDate"], info_leilao["artigoId"], userid))
                    leilao_id = cursor.fetchone()
                    conn.commit()
                    conn.close()
                    return {'leilaoId': leilao_id[0]}
                except:
                    conn.rollback()
                    conn.close()
                    return {'erro': 'Erro creating auction'}

    else:
        conn.close()
        return {'erro' : "user isn\'t logged in"}


@endpoints.route("/dbproj/leiloes", methods=['GET'], strict_slashes=True)
def leiloes():
    logger.info("#### GET - dbproj/leiloes -> Listar todos os leiloes ####")

    conn = db_connection()
    cursor = conn.cursor()

    leiloes = []

    if request.method == 'GET': # GET - buscar todos os leiloes
        cursor.execute("SELECT * from leilao;")
        info = cursor.fetchall()

        for row in info:
            leiloes.append(f"leilaoId: {row[0]}, descricao: {row[2]}")
        
        conn.close()
        return jsonify(leiloes)


@endpoints.route("/dbproj/leiloes/<keyword>", methods=['GET'], strict_slashes=True)
def get_leiloes(keyword):
    logger.info("#### GET - dbproj/leiloes/<keyword> -> Procurar por id ou na descriçao ####")

    conn = db_connection()
    cursor = conn.cursor()

    leiloes = []

    # GET - buscar todos os leiloes
    if request.method == 'GET':

        info = None

        try:
            keyword = int(keyword)
        except:
            pass

        if type(keyword)!=str:
            cursor.execute("SELECT leilao.id, leilao.descricao, artigos.id from leilao, artigos WHERE artigos_id = artigos.id AND artigos.id = %s;", (keyword, ))
            info = cursor.fetchall()

        # leilao com id 'keyword' nao existe, procurar na descricao
        if info is None:
            cursor.execute("SELECT leilao.id, leilao.descricao, artigos.nome from leilao, artigos WHERE artigos_id = artigos.id AND artigos.nome = %s;", (keyword, ))
            info = cursor.fetchall()

            for row in info:
                if str(keyword) == str(row[2]):
                    leiloes.append((row[0], row[1]))
            conn.close()
            if leiloes != []:
                return jsonify(leiloes)
            else:
                return {'erro': f"Nao encontrado nenhum leilao com artigo com nome {keyword}"}
        else:
            for row in info:
                if str(keyword) == str(row[2]):
                    leiloes.append((row[0], row[1]))
            
            conn.close()
            if leiloes != []:
                return jsonify(leiloes)
            else:
                return {'erro': f"Nao encontrado nenhum leilao com artigo com id {keyword}"}


@endpoints.route("/dbproj/leilao/<leilao_id>", methods=['GET', 'PUT', 'POST'], strict_slashes=True)
def leilao(leilao_id):
    conn = db_connection()
    cursor = conn.cursor()

    try:
        statement = "SELECT * from leilao WHERE id = %s;"
        cursor.execute(statement, (leilao_id, ))
        info = cursor.fetchone()
    except:
        conn.close()
        return {'erro' : "couldn't fetch auction"}

    if info is None:
        conn.close()
        return {'erro': f"auction with id = {leilao_id} doesn't exist!"}

    # GET - buscar todos os leiloes
    if request.method == 'GET':
        logger.info("#### GET - dbproj/leilao/<leilao_id> -> Procurar leilao por id ####")
        mensagens = []
        
        #get mensagens de outra tabela
        statement = "SELECT comentario, resposta, utilizador_userid FROM comentario WHERE leilao_id = %s;"
        try:
            cursor.execute(statement, (leilao_id, ))
            info_mensagens = cursor.fetchall()
        except:
            return {'erro' : "Couldn't get messages"}

        for row in info_mensagens:
            cursor.execute("SELECT * FROM get_username_from_id(%s);", (row[2], ))
            user = cursor.fetchone()
            mensagens.append([f"Comentário de {user[0]}:", f"- {row[0]}", "Resposta:", f"- {'' if row[1] is None else row[1]}"])
        
        conn.close()

        return {
                'leilaoId': info[0],
                'titulo': info[1],
                'descricao' : info[2],
                'precomin' : info[3],
                'precoatual' : info[4],
                'endDate' : info[5],
                'mensagens' : mensagens
                }

    # PUT - editar um leilao
    elif request.method == 'PUT':
        logger.info("#### PUT - dbproj/leilao/<leilao_id> -> Atualizar leilao por id ####")
        info = request.get_json()

        editable_columns=["titulo", "descricao", "precomin", "data"]
        columns = []
        information = []
        result = check_token(info["userAuthToken"])

        if result == 'Expired':
            conn.close()
            return {'erro' : 'token expired'}

        elif result == 'Valid':
            userid = get_userid_from_token(info["userAuthToken"])
            if userid == 0:
                return {'erro': "user doesn't exist!"}

            try:   
                statement = "SELECT utilizador_userid FROM leilao WHERE id = %s;"
                cursor.execute(statement, (leilao_id))
                leilao_userid = cursor.fetchone()
            except:
                conn.close()
                return {'error': "SELECT utilizador_userid FROM leilao"}

            if (leilao_userid[0] != userid):
                conn.close()
                return {'error': "You aren't the owner of this auction!"}
            else:
                try:
                    for key in info.keys():
                        if key == 'userAuthToken':
                            continue
                        if key in editable_columns:
                            columns.append(AsIs(key))
                            information.append(info[key])
                    if len(columns) != 1:
                        statement = "UPDATE leilao SET %s = %s WHERE id = %s;"
                        cursor.execute(statement, (tuple(columns), tuple(information), leilao_id))
                    else:
                        statement = "UPDATE leilao SET %s = %s WHERE id = %s;"
                        cursor.execute(statement, (columns[0], information[0], leilao_id))
                    conn.commit()
                    conn.close
                    return {'Success': "auction updated!"}
                except:
                    conn.rollback()
                    conn.close()
                    return {'erro': "Something happened..."}

        else:
            conn.close()
            return {'erro' : "user isn\'t logged in"}
    
    #POST - escrever uma mensagem no leilao
    elif request.method == 'POST':
        info_leilao = request.get_json()

        statement = "INSERT INTO comentario (comentario, leilao_id, utilizador_userid) VALUES (%s, %s, %s);"

        userid = get_userid_from_token(info_leilao['authToken'])
        if userid == 0:
            return {'erro': "user doesn't exist!"}

        try:
            cursor.execute(statement, (info_leilao['mensagem'], leilao_id, userid))
            conn.commit()
            conn.close()
            return {f'leilao {leilao_id}' : 'Message added'}
        except:
            conn.rollback()
            conn.close()
            return {'erro' : 'Erro adding message'}
    

@endpoints.route("/dbproj/licitar/<leilao_id>/<amount>", methods=['GET'], strict_slashes=True)
def leilao_bid(leilao_id, amount):
    logger.info("#### GET - dbproj/<leilao_id>/<amount> -> Licitar pelo id do leilao ####")

    conn = db_connection()
    cursor = conn.cursor()
    token = request.get_json()

    result = check_token(token["userAuthToken"])

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}

    elif result == 'Valid':
        
        statement = "SELECT precoatual, precomin FROM leilao WHERE %s = id;"
        cursor.execute(statement, (leilao_id,))
        preco = cursor.fetchone()
       
        if preco is None:
            conn.close()
            return {'erro': "auction doesn\'t exist!"}

        try:
            amount = int(amount)
        except:
            conn.close()
            return {'erro': "amount inserted isn\'t valid!"}

        if amount < int(preco[1]):
            conn.close()
            return {'erro': f"bid must be at least {preco[1]}"}
        elif (amount <= int(preco[0])):
            conn.close()
            return {'erro': "insert an amount bigger then the current bid!"}
        else:
            userid = get_userid_from_token(token["userAuthToken"])
            if userid == 0:
                return {'erro': "user doesn't exist!"}
            statement = "INSERT INTO licitacao (valor, leilao_id, utilizador_userid) VALUES (%s, %s, %s);"
            try:
                cursor.execute(statement, (amount, leilao_id, userid))
                conn.commit()
            except:
                conn.rollback()
                conn.close()
                return {'erro': "couldn't insert value"}
            conn.close()
            return {'Sucess': f"You made a bid on auction {leilao_id}"}

    else:
        conn.close()
        return {'erro' : "user isn\'t logged in"}


@endpoints.route("/dbproj/leiloes/user", methods=['GET'], strict_slashes=True)
def user_auctions():
    logger.info("#### GET - dbproj/leiloes/user -> Listar leiloes em que o utilizador tenha atividade ####")

    conn = db_connection()
    cursor = conn.cursor()
    token = request.get_json()

    result = check_token(token["userAuthToken"])
    leiloes = []

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}

    elif result == 'Valid':
        userid = get_userid_from_token(token["userAuthToken"])
        if userid == 0:
            return {'erro': "user doesn't exist!"}

        statement = "SELECT distinct leilao.titulo, leilao.descricao, precoatual, leilao.data from leilao, licitacao where leilao.id = leilao_id AND licitacao.utilizador_userid = %s OR leilao.utilizador_userid = %s;"
        try:
            cursor.execute(statement, (userid, userid))
            info = cursor.fetchall()
        except:
            conn.close()
            return {'erro': 'getting leilao'}

        conn.close()

        if info == []:
            return {'erro': "user doesn\'t participate in any auction!"}

        for row in info:
            leiloes.append(f"titulo: {row[0]}, descricao: {row[1]}, precoatual: {row[2]}, endDate: {row[3]}")

        return jsonify(leiloes)

    else:
        conn.close()
        return {'erro' : "user isn\'t logged in"}


@endpoints.route("/dbproj/inbox", methods=['GET'], strict_slashes=True)
def user_messages():
    logger.info("#### GET - dbproj/inbox -> Listar mensagens de um utilizador ####")

    conn = db_connection()
    cursor = conn.cursor()
    token = request.get_json()

    result = check_token(token["userAuthToken"])

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}

    elif result == 'Valid':
        mensagens = []
        userid = get_userid_from_token(token["userAuthToken"])
        if userid == 0:
            return {'erro': "user doesn't exist!"}

        statement = "SELECT mensagem, leilao_id from mensagens where utilizador_userid = %s;"

        try:
            cursor.execute(statement, (userid,))
            info = cursor.fetchall()
        except:
            conn.close()
            return {'erro': 'getting messages'}

        conn.close()

        if info == []:
            return {'erro': "user doesn\'t have any message!"}

        for row in info:
            mensagens.append(f"{row[0]} in auction {row[1]}")

        return jsonify(mensagens)

    else:
        conn.close()
        return {'erro' : "user isn't logged in"}


@endpoints.route("/dbproj/<leilao_id>/messages", methods=['PUT', 'GET'], strict_slashes=True)
def respond_messages(leilao_id):

    conn = db_connection()
    cursor = conn.cursor()
    info = request.get_json()

    result = check_token(info["userAuthToken"])

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}
    elif result == 'Erro':
        conn.close()
        return {'erro' : "user isn't logged in"}

    userid = get_userid_from_token(info["userAuthToken"])
    if userid == 0:
        return {'erro': "user doesn't exist!"}

    try:   
        statement = "SELECT utilizador_userid FROM leilao WHERE id = %s;"
        cursor.execute(statement, (leilao_id,))
        leilao_userid = cursor.fetchone()
    except:
        conn.close()
        return {'error': "SELECT utilizador_userid FROM leilao"}
    
    if leilao_userid is None:
        return {'erro' : 'Auction doesnt exist'}

    if (leilao_userid[0] != userid):
        conn.close()
        return {'error': "You aren't the owner of this auction!"}
    

    # PUT - responder a uma mensagem
    if request.method == 'PUT':
        logger.info("#### PUT - dbproj/<leilao_id>/messages -> Responder a mensagens de um leilao ####")

        statement = "UPDATE comentario SET resposta = %s WHERE id = %s;"
        try:
            cursor.execute(statement, (info['resposta'], info['idComentario']))
            conn.commit()
            conn.close()
        except:
            conn.rollback()
            conn.close()
            return {'erro' : 'Erro inserting response'}
        
        return {'Sucess' : f"You added a responde to comment with id {info['idComentario']}"}
       
    # GET - buscar todas as mensagens
    elif request.method == 'GET':
        logger.info("#### GET - dbproj/<leilao_id>/messages -> Buscar todas as mensagens de um leilao ####")
        mensagens = []
        try:
            statement = "SELECT id, comentario, resposta FROM comentario WHERE leilao_id = %s;"
            cursor.execute(statement, (leilao_id, ))
            info = cursor.fetchall()
        except:
            return {'erro' : 'Erro getting comentarios'}
        
        for row in info:
            mensagens.append([f"id: {row[0]}", f"comentario: {row[1]}", f"resposta: {'' if row[2] == None else row[2]}"])
        
        return jsonify(mensagens)


@endpoints.route("/dbproj/user/profile", methods=['PUT', 'GET'], strict_slashes=True)
def user_profile():

    conn = db_connection()
    cursor = conn.cursor()
    info = request.get_json()

    result = check_token(info["userAuthToken"])

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}
    elif result == 'Erro':
        conn.close()
        return {'erro' : "user isn't logged in"}

    userid = get_userid_from_token(info["userAuthToken"])
    if userid == 0:
        return {'erro': "user doesn't exist!"}

    #Atualizar dados do perfil
    if request.method == 'PUT':
        logger.info("#### PUT - dbproj/user/profile -> Atualizar dados do perfil ####")

        editable_columns = ['nome', 'morada']
        columns = []
        information = []
        
        statement = "UPDATE utilizador SET %s = %s WHERE userid = %s;"
        try:
            for key in info.keys():
                if key == 'userAuthToken':
                    continue
                if key in editable_columns:
                    columns.append(AsIs(key))
                    information.append(info[key])
            if len(columns) != 1:
                cursor.execute(statement, (tuple(columns), tuple(information), userid))
            else:
                cursor.execute(statement, (columns[0], information[0], userid))
            conn.commit()
            conn.close
            return {'Success': "profile updated!"}
        except:
            conn.rollback()
            conn.close()
            return {'erro': "Something happened..."}
    #Ver dados do perfil
    elif request.method == 'GET':
        logger.info("#### GET - dbproj/user/profile -> Ver dados do perfil ####")

        statement = "SELECT userid, username, email, nome, morada FROM utilizador WHERE userid = %s;"

        try:
            cursor.execute(statement, (userid,))
            info = cursor.fetchone()
            conn.close()
            return {
                'userid' : info[0],
                'username' : info[1],
                'email' : info[2],
                'nome' : info[3],
                'morada' : info[4]
            }
        except:
            conn.close()
            return {'erro' : "Couldn't get profile"}

