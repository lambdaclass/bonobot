import requests
from flask import Flask, request

import bonobot.bonobot as bonobot

def make_app():
    app = Flask(__name__)

    @app.route('/bonobot',  methods=['POST'])
    def bonobot_mention():
        payload = request.json
        if payload['type'] == 'url_verification':
            return {'challenge': payload['challenge']}

        if payload['event']['type'] == 'app_mention':
            text = bonobot.get_random_bono()
            channel = payload['event']['channel']
            bonobot.send_response(channel, text)

            return 'ok'

    return app


if __name__ == '__main__':
    app = make_app()
    app.run(port=800)
