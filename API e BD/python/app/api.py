import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

#TODO DAR RETURN A TOKEN
@app.route("/dbproj/user", methods=['PUT'], strict_slashes=True)
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
@app.route("/dbproj/user", methods=['POST'], strict_slashes=True)
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


def db_connection():
    db = psycopg2.connect(user="admin",
                          password="admin",
                          host="db",
                          port="5432",
                          database="projetobd")
    return db


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)

