import requests
from flask import Flask, request

import bonobot

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

    return 'Hello, World!'
