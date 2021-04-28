from web import start_app


app, logger = start_app()


if __name__ == '__main__':

    logger.info("\n\nAPI v1.0 online: http://localhost:8080/dbproj/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)

