from flask import Flask, jsonify, request
import psycopg2, logging, time, os, datetime, sys
from dotenv import load_dotenv


TOKEN_DURATION = 5 # duraçao do token em horas


def check_token(token):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT time_created FROM authtokens WHERE token = %s", (token, ))
    info = cursor.fetchone()
    token_time = []

    #info[0] = "2021-04-28 18:14:43.925712"
    # se o token existir na tabela, verificar se esta valido
    print(str(info[0]))
    if info is not None: 
        token_time = str(info[0]).split('.')[0].split(' ') # "2021-04-28 18:14:43.925712" -> "2021-04-28 18:14:43" -> ["2021-04-28", "18:14:43"]
        token_time[0] = token_time.split('-') # ["2021", "04", "28"]
        token_time[1] = token_time.split(':') # ["18", "14", "43"]

        time_aux = datetime.datetime(int(token_time[0][0]), int(token_time[0][1]),int(token_time[0][2]), int(token_time[1][0]),int(token_time[1][1]),int(token_time[1][2]))
        time_now = datetime.datetime.now()
        
        # verificar se o token ja expirou
        if time_aux - time_now > datetime.deltatime(hours = TOKEN_DURATION):
            cursor.execute( "DELETE FROM authtokens WHERE token = %s", (token, ) )
            return 'Expired'
        else:
            return 'Valid'
    else:
        return 'Erro'


def print_exception(err):
    err_type, err_obj, traceback = sys.exc_info()
    line_num = traceback.tb_lineno

    print(f'ERRRO: {err}\nLINE {line_num}\nTraceback: {traceback}\nTYPE:{err_type}')


def db_connection():
    load_dotenv()
    
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_database = os.getenv('DB_database')

    db = psycopg2.connect(user=DB_USER,password=DB_PASSWORD,host="db",port="5432",database=DB_database)

    return db


def start_logger():
    #Setup Logger
    logging.basicConfig(filename='logs/log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Format
    # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s','%H:%M:%S')

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def start_app():
    # start flask web server
    app = Flask(__name__)

    from .endpoints import endpoints
    app.register_blueprint(endpoints, url_prefix='/')
  
    return app
