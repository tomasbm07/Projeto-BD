from flask import Flask, jsonify, request, Blueprint
import psycopg2, logging, time
from . import db_connection


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


#TODO DAR RETURN A TOKEN
@endpoints.route("/dbproj/user", methods=['PUT'], strict_slashes=True)
def login():
    conn = db_connection()
    cursor = conn.cursor()

    info_user = request.get_json()

    statement = """SELECT COUNT(username)
                   FROM utilizador
                   WHERE username=%s AND password=%s;"""

    values = (info_user["username"], info_user["password"])

    cursor.execute(statement, values)
    validation = cursor.fetchone()

    if validation[0] == 1:
        info = "Autenticado!"
    else:
        info = "Combinacao de username e password inexistente, tente outra vez"

    conn.close()
    return jsonify(info)


#TODO VERIFICAR DAR CATCH AOS ERROS (UTILIZADOR JA EXISTENTE E QUNADO NAO E CUMPRIDO REQUISITOS DA BD)
@endpoints.route("/dbproj/user", methods=['POST'], strict_slashes=True)
def signup():
    conn = db_connection()
    cursor = conn.cursor()

    info_user = request.get_json()

    statement = """INSERT INTO utilizador (username, email, password)
                   VALUES (%s, %s, %s);"""

    values = (info_user["username"], info_user["email"], info_user["password"])

    try:
        cursor.execute(statement, values)
        conn.commit()
        info = "Registado com sucesso!"
    except:
        info = "Informacoes com sintaxe incorreta!"

    conn.close()
    return jsonify(info)

