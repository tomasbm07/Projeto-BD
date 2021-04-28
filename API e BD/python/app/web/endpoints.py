from flask import Flask, jsonify, request, Blueprint
import psycopg2, logging, time
from . import db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid1


endpoints = Blueprint('auth', __name__)


#Default page
@endpoints.route('/dbproj/') 
def home(): 
	return """
	<center>
		Projeto da cadeira de Base de Dados<br>
		FCTUC - DEI / 2020-2021
		<h1> Auction Houe </h1>
			<br>
			<br>
			Membros:
			<br>
			Alexandre Andrade - 20192
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

		cursor.execute("SELECT username, password, userid FROM utilizador WHERE username = %s", (info_user["username"], ) )
		info = cursor.fetchone()
		if info == None:
			return {'erro': 'utilizador nao existe'}
		else:
			if check_password_hash(info[1], info_user["password"]):
				token = str(uuid1())
				values = (info[2], token)
				cursor.execute("INSERT INTO authtokens (userid, token) VALUES (%s, %s)", values)
				cursor.execute("commit;")
				return {'authToken': token}
			else:
				return {'erro': 'AuthError'}

		conn.close()

	else: # POST - registo de utilizador
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
			return {'userid': info[0]}
		elif info is not None:
			return {'erro': 'username ja registado'}
		else:
			return {'erro': 'email ja registado'}

		conn.close()


#TODO: fazer este endpoint
@endpoints.route("/dbproj/leilao", methods=['POST'], strict_slashes=True)
def leilao_create():
	conn = db_connection()
	cursor = conn.cursor()
	info_leilao = request.get_json()

	if request.method == 'POST': # POST - criar leilao
		pass


@endpoints.route("/dbproj/leiloes", methods=['GET'], strict_slashes=True)
def leiloes():
	conn = db_connection()
	cursor = conn.cursor()

	leiloes = []

	if request.method == 'GET': # GET - buscar todos os leiloes
		cursor.execute("""SELECT * from leilao;""")
		info = cursor.fetchall();

		for row in info:
			leiloes.append(row)

		return jsonify(leiloes)


#TODO: fazer este endpoint da forma certa, pq n esta :)
@endpoints.route("/dbproj/leiloes/<keyword>", methods=['GET'], strict_slashes=True)
def get_leiloes(keyword):
	conn = db_connection()
	cursor = conn.cursor()

	leilao = []

	if request.method == 'GET': # GET - buscar todos os leiloes
		cursor.execute("""SELECT * from leilao WHERE id = %s;""", (leilao_id, ))
		info = cursor.fetchone();

		if info is None:
			return {"erro": "leilao nao existe"}
		else:
			leilao = info[0]
			return {"id": leilao[0], "descricao": leilao[2]}


#TODO: fazer este endpoint
@endpoints.route("/dbproj/leilao/<leilao_id>", methods=['GET', 'PUT'], strict_slashes=True)
def leilao(leilao_id):
	conn = db_connection()
	cursor = conn.cursor()
	info_leilao = request.get_json()

	if request.method == 'GET': # GET - buscar todos os leiloes
		pass
		
	else: # PUT - editar um leilao
		pass
	pass


#TODO: fazer este endpoint
@endpoints.route("/dbproj/licitar/<leilao_id>/<amount>", methods=['GET'], strict_slashes=True)
def leilao_bid(leilao_id, amount):
	conn = db_connection()
	cursor = conn.cursor()


	pass

