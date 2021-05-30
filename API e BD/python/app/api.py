from web import start_app, start_logger
import logging
from time import sleep


if __name__ == '__main__':
    #Config Logger
    logging.basicConfig(filename='logs/log_file.log')

    app = start_app()
    logger = start_logger()

    sleep(1) # sleep to let db start before print

    logger.info("API online: http://localhost:8080/dbproj/")
    app.run(host="0.0.0.0", debug=True, threaded=True)
