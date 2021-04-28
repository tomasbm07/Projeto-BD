import logging, time, os
from flask import Flask, jsonify, request
import psycopg2, logging, time
from dotenv import load_dotenv


def db_connection():
  load_dotenv()
  DB_USER = os.getenv('DB_USER')
  DB_PASSWORD = os.getenv('DB_PASSWORD')
  DB_database = os.getenv('DB_database')
  db = psycopg2.connect(user=DB_USER,password=DB_PASSWORD,host="db",port="5432",database=DB_database)

  return db


def start_app():
  # start flask web server
  app = Flask(__name__)

  from .endpoints import endpoints
  app.register_blueprint(endpoints, url_prefix='/')

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
  
  return app, logger

