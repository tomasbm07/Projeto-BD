from web import start_app, start_logger
from time import sleep


app = start_app()
logger = start_logger()


if __name__ == '__main__':
    sleep(1)

    logger.info("API online: http://localhost:8080/dbproj/")
    app.run(host="0.0.0.0", debug=True, threaded=True)
