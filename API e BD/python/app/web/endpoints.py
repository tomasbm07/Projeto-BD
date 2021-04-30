from flask import Flask, jsonify, request, Blueprint
import psycopg2, logging, time
from . import db_connection, check_token, start_logger
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
					return {'authToken': token}
				else:
					logger.debug("User ja fez login")
					return {'warning': 'user ja fez login', 'authToken' : aux[0]}
			else:
				logger.debug("Erro de autenticacao")
				return {'erro': 'AuthError'}

		conn.close()

	else: # POST - registo de utilizador
		logger.info("#### POST - dbproj/user -> Sign up ####")

		statement = """INSERT INTO utilizador (username, email, password)
					   VALUES (%s, %s, %s);"""

		values = ( info_user["username"], info_user["email"], generate_password_hash(info_user["password"], method='sha256') )

		get_user_querry = "SELECT userid FROM utilizador WHERE username = %s;"

		cursor.execute(get_user_querry, (info_user["username"],) )
		info = cursor.fetchone()

		cursor.execute("SELECT userid FROM utilizador WHERE email = %s;", (info_user["email"],) )
		info_aux = cursor.fetchone()

		if info is None and info_aux is None: # se for None -> ainda nao existe na bd
			cursor.execute(statement, values)
			cursor.execute("commit;")
			cursor.execute(get_user_querry, (info_user["username"], ) )
			info = cursor.fetchone()
			logger.debug(f"User {info[0]} created")
			return {'userid': info[0]}
		elif info is not None:
			logger.debug("username ja registado")
			return {'erro': 'username ja registado'}
		else:
			logger.debug("email ja registado")
			return {'erro': 'email ja registado'}

		conn.close()


#TODO: fazer este endpoint
@endpoints.route("/dbproj/leilao", methods=['POST'], strict_slashes=True)
def leilao_create():
	logger.info("#### POST - dbproj/leilao -> Criar leilao ####")

	conn = db_connection()
	cursor = conn.cursor()
	info_leilao = request.get_json()
	
	result = check_token()

	if result == 'Expired':
		return {'erro' : 'token expired'}

	elif result == 'Valid':
		if request.method == 'POST': # POST - criar leilao
			pass

	else: 
		return {'erro' : "user isn\'t logged in"}



@endpoints.route("/dbproj/leiloes", methods=['GET'], strict_slashes=True)
def leiloes():
	logger.info("#### GET - dbproj/leiloes -> Listar todos os leiloes ####")

	conn = db_connection()
	cursor = conn.cursor()

	leiloes = []

	if request.method == 'GET': # GET - buscar todos os leiloes
		cursor.execute("""SELECT * from leilao;""")
		info = cursor.fetchall();

		for row in info:
			leiloes.append(row)

		return jsonify(leiloes)


@endpoints.route("/dbproj/leiloes/<keyword>", methods=['GET'], strict_slashes=True)
def get_leiloes(keyword):
	logger.info("#### GET - dbproj/leiloes/<keyword> -> Procurar por id ou na descriçao ####")

	conn = db_connection()
	cursor = conn.cursor()

	leiloes = []

	# GET - buscar todos os leiloes
	if request.method == 'GET':
		cursor.execute("""SELECT id, descricao from leilao WHERE id = %s;""", (keyword, ))
		info = cursor.fetchone();

		# leilao com id 'keyword' nao existe, procurar na descricao
		if info is None:
			cursor.execute("""SELECT id, descricao from leilao;""")
			info = cursor.fetchall()

			for row in info:
				if keyword in row[1]:
					leiloes.append((row[0], row[1]))

			return jsonify(leiloes)



#TODO: fazer este endpoint
@endpoints.route("/dbproj/leilao/<leilao_id>", methods=['GET', 'PUT'], strict_slashes=True)
def leilao(leilao_id):
	conn = db_connection()
	cursor = conn.cursor()
	info_leilao = request.get_json()

	# GET - buscar todos os leiloes
	if request.method == 'GET':
		logger.info("#### GET - dbproj/leilao/<leilao_id> -> Procurar leilao por id ####")
		return {}

	# PUT - editar um leilao
	else:
		logger.info("#### PUT - dbproj/leilao/<leilao_id> -> Atualizar leilao por id ####")
		return {}
	


#TODO: fazer este endpoint
@endpoints.route("/dbproj/licitar/<leilao_id>/<amount>", methods=['GET'], strict_slashes=True)
def leilao_bid(leilao_id, amount):
	logger.info("#### GET - dbproj/<leilao_id>/<amount> -> Atualizar leilao por id ####")

	conn = db_connection()
	cursor = conn.cursor()


	return {}

