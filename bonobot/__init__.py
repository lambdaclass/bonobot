import os

import requests
from flask import Flask, request

from bonobot.basebot import FileBot
from bonobot.bonobot import BonoBot

import logging

logging.basicConfig(level=logging.DEBUG)

BOTS = {
    'bono': BonoBot(api_token=os.environ.get('BONO_API_TOKEN'),
                    bot_token=os.environ.get('BONO_BOT_TOKEN')),
    'pollo': FileBot(token=os.environ.get('POLLO_BOT_TOKEN'),
                     icon_emoji=':pollobot:', username='PolloBot',
                     source_file='pollo.txt'),
    'peron': FileBot(token=os.environ.get('POCHO_BOT_TOKEN'),
                     icon_emoji=':pochobot:', username='PochoBot',
                     source_file='pocho.txt')
}

def make_app():
    app = Flask(__name__)

    @app.route('/slackbot/<botname>', methods=['POST'])
    def bonobot_mention(botname):
        payload = request.get_json(force=True)
        logging.info("RECEIVED REQUEST %s %s", botname, payload)
        bot = BOTS[botname]

        if payload['type'] == 'url_verification':
            return {'challenge': payload['challenge']}

        if (payload['event']['type'] == 'app_mention' or
            (payload['event']['type'] == 'message' and botname in payload['event']['text'])):
            channel = payload['event']['channel']
            text = payload['event']['text']
            bot.send_response(channel, text)

        return 'ok'

    return app


if __name__ == '__main__':
    app = make_app()
    app.run(port=800)
