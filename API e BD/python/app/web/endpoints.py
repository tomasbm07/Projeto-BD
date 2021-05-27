from flask import Flask, jsonify, request, Blueprint
import psycopg2, logging, time
#from . import db_connection, check_token, start_logger
from . import *
from .functions import *
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid1


endpoints = Blueprint('endpoints', __name__)

logger = start_logger()


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

        cursor.execute("SELECT username, password, userid FROM utilizador WHERE username = %s", (info_user["username"], ) )
        info = cursor.fetchone()
        if info == None:
            logger.debug("Utilizador nao existe")
            conn.close()
            return {'erro': 'utilizador nao existe'}
        else:
            if check_password_hash(info[1], info_user["password"]):
                #verificar se este user ja tem um token na tabela authtokens
                cursor.execute("SELECT token FROM authtokens WHERE userid = %s", (info[2],))
                aux = cursor.fetchone()
                #se nao tiver um token associado ao user, gerar token e inserir na tabela
                if aux is None:
                    token = str(uuid1())
                    values = (info[2], token)
                    cursor.execute("INSERT INTO authtokens (userid, token) VALUES (%s, %s)", values)
                    cursor.execute("COMMIT;")
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
                        conn.close()
                        return {'warning': 'token has expired'}
                    else:
                        conn.close()
                        return {'erro': "tokens does't exist"}
            else:
                logger.debug("Erro de autenticacao")
                conn.close()
                return {'erro': 'AuthError'}

    else: # POST - registo de utilizador
        logger.info("#### POST - dbproj/user -> Sign up ####")

        statement = """INSERT INTO utilizador (username, email, password) VALUES (%s, %s, %s);"""
        values = (info_user["username"], info_user["email"], generate_password_hash(info_user["password"], method='sha256'))

        #verificar se o username ja esta registado
        get_user_querry = "SELECT userid FROM utilizador WHERE username = %s;"
        cursor.execute(get_user_querry, (info_user["username"],) )
        info = cursor.fetchone()

        #verificar se o email ja esta registado
        cursor.execute("SELECT userid FROM utilizador WHERE email = %s;", (info_user["email"],) )
        info_aux = cursor.fetchone()

        if info is None and info_aux is None: # se for None -> ainda nao existe na bd
            cursor.execute(statement, values)
            cursor.execute("commit;")
            cursor.execute(get_user_querry, (info_user["username"], ) )
            info = cursor.fetchone()
            logger.debug(f"User {info[0]} created")
            conn.close()
            return {'userid': info[0]}
        elif info is not None:
            logger.debug("username ja registado")
            conn.close()
            return {'erro': 'username ja registado'}
        else:
            logger.debug("email ja registado")
            conn.close()
            return {'erro': 'email ja registado'}
        conn.close()


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
            statement = """SELECT id FROM artigos WHERE id = %s;"""
            cursor.execute(statement, (info_leilao["artigoId"], ))
            artigo = cursor.fetchone()
            if artigo is None:
                return {'erro': 'artigo nao existe!'}
            else:
                userid = get_user_from_token(info_leilao["userAuthToken"])

                statement = "INSERT INTO leilao (titulo, descricao, precomin, data, artigos_artigoid, utilizador_userid) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
                cursor.execute(statement, (info_leilao["titulo"], info_leilao["descricao"], info_leilao["precoMinimo"], info_leilao["endDate"], info_leilao["artigoId"], userid))
                leilao_id = cursor.fetchone()
                cursor.execute("commit;")
                return {'leilaoId': leilao_id[0]}


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
            cursor.execute("""SELECT leilao.id, leilao.descricao, artigos.id from leilao, artigos WHERE artigos_artigoid = artigos.id AND artigos.id = %s;""", (keyword, ))
            info = cursor.fetchall();

        # leilao com id 'keyword' nao existe, procurar na descricao
        if info is None:
            cursor.execute("""SELECT leilao.id, leilao.descricao, artigos.nome from leilao, artigos WHERE artigos_artigoid = artigos.id AND artigos.nome = %s;""", (keyword, ))
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
                return {'erro': f"Nao encontrado nenhum leilao com artigo de EAN {keyword}"}

            


#TODO: fazer este endpoint
@endpoints.route("/dbproj/leilao/<leilao_id>", methods=['GET', 'PUT'], strict_slashes=True)
def leilao(leilao_id):
    conn = db_connection()
    cursor = conn.cursor()

    statement = "SELECT * from leilao WHERE id = %s;"
    cursor.execute(statement, (leilao_id, ))
    info = cursor.fetchone()

    # GET - buscar todos os leiloes
    if request.method == 'GET':
        logger.info("#### GET - dbproj/leilao/<leilao_id> -> Procurar leilao por id ####")
        mensagens = []
        
        #get mensagens de outra tabela
        statement = "SELECT comentario, resposta, utilizador_userid FROM comentario WHERE leilao_id = %s;"
        cursor.execute(statement, (leilao_id, ))
        info_mensagens = cursor.fetchall()

        for row in info_mensagens:
            cursor.execute("SELECT * FROM get_username_from_id(%s);", (row[2], ))
            user = cursor.fetchone()
            mensagens.append([f"Comentário de {user[0]}:", f"{row[0]}", f"Resposta: {row[1]}"])
        
        conn.close()
        #mensagens = ['boas', 'ola', 'hehexD']
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
    else:
        logger.info("#### PUT - dbproj/leilao/<leilao_id> -> Atualizar leilao por id ####")
        info_leilao = request.get_json()


        return {}
    

@endpoints.route("/dbproj/licitar/<leilao_id>/<amount>", methods=['GET'], strict_slashes=True)
def leilao_bid(leilao_id, amount):
    logger.info("#### GET - dbproj/<leilao_id>/<amount> -> Atualizar leilao por id ####")

    conn = db_connection()
    cursor = conn.cursor()
    token = request.get_json()

    result = check_token(token["userAuthToken"])

    if result == 'Expired':
        conn.close()
        return {'erro' : 'token expired'}

    elif result == 'Valid':
        
        statement = "SELECT precoatual FROM leilao WHERE %s = id;"
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

        if (amount <= int(preco[0])):
            conn.close()
            return {'erro': "insert an amount bigger then the current bid!"}
        else:
            userid = get_user_from_token(token["userAuthToken"])
            statement = "INSERT INTO licitacao (valor, leilao_id, utilizador_userid) VALUES (%s, %s, %s);"
            cursor.execute(statement, (amount, leilao_id, userid))
            cursor.execute("commit;")
            conn.close()
            return {'Sucesso': "true"}

    else:
        conn.close()
        return {'erro' : "user isn\'t logged in"}
