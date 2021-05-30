from flask import Flask, jsonify, request
import psycopg2, datetime
from . import *


TOKEN_DURATION = 5 # duraçao do token em horas

def get_userid_from_token(token):
    conn = db_connection()
    cursor = conn.cursor()
    statement = "SELECT utilizador_userid FROM authtokens WHERE token = %s;"
    try:
        cursor.execute(statement, (token, ))
        userid = cursor.fetchone()
        conn.close()
        return userid[0]
    except:
        conn.close()
        return 0


def check_token(token):
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT time_created FROM authtokens WHERE token = %s", (token, ))
        info = cursor.fetchone()
    except:
        conn.close()
        return 'Erro'

    token_time = []

    #info[0] = "2021-04-28 18:14:43.925712"
    # se o token existir na tabela, verificar se esta valido
    if info is not None: 
        token_time = (str(info[0])).split('.')[0].split(' ') # "2021-04-28 18:14:43.925712" -> "2021-04-28 18:14:43" -> ["2021-04-28", "18:14:43"]
        token_time[0] = token_time[0].split('-') # ["2021", "04", "28"]
        token_time[1] = token_time[1].split(':') # ["18", "14", "43"]

        time_aux = datetime.datetime(int(token_time[0][0]), int(token_time[0][1]),int(token_time[0][2]), int(token_time[1][0]),int(token_time[1][1]),int(token_time[1][2]))
        time_now = datetime.datetime.now()
        
        # verificar se o token ja expirou
        if time_now - time_aux > datetime.timedelta(hours = TOKEN_DURATION):
            try:
                cursor.execute("DELETE FROM authtokens WHERE token = %s", (token, ))
                conn.commit()
                conn.close()
                return 'Expired'
            except:
                conn.rollback()
                conn.close()
                return 'Erro'
        else:
            conn.close()
            return 'Valid'
    else:
        conn.close()
        return 'Erro'
