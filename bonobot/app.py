import logging
import os

import requests
from flask import Flask, request

from bonobot.bot import FileBot, HaikuBot, InchequeableBot, ShareBot

logging.basicConfig(level=logging.DEBUG)

BOTS = [ShareBot('bono', channel='out_of_context_bono', emoji=':bono3:', username='BonoBot'),
        ShareBot('lambda', channel='out_of_context_lambda', emoji=':lambda:', username='LambdaBot'),
        ShareBot('pelito', channel='out_of_context_lambda', emoji=':pelito:', username='PelitoBot', filter_author='Mario Rugiero'),
        FileBot('pollo', icon_emoji=':pollobot:', username='PolloBot', source_file='pollo.txt'),
        FileBot(['peron', 'pocho', 'el general'], icon_emoji=':pochobot:', username='PochoBot', source_file='pocho.txt'),
        FileBot('diego', icon_emoji=':lastima-no:', username="DiegoBot", source_file='diego.txt'),
        FileBot('moria', icon_emoji=':moria:', username="MoriaBot", source_file='moria.txt'),
        HaikuBot("haiku", {"java": 300, "random": 1500, "economia": 200}, ":basho:", "HaikuBot"),
        InchequeableBot()]


def make_app():
    app = Flask(__name__)

    @app.route('/slackbot/bot', methods=['POST'])
    def bonobot_mention():
        payload = request.get_json(force=True)
        logging.info("RECEIVED REQUEST %s", payload)

        if payload['type'] == 'url_verification':
            return {'challenge': payload['challenge']}

        event = payload['event']
        for bot in BOTS:
            if bot.is_relevant(**event):
                bot.send_response(**event)

        return 'ok'

    return app


if __name__ == '__main__':
    app = make_app()
    app.run(port=800)