import logging
import os

import requests
from flask import Flask, request

from bonobot.basebot import FileBot
from bonobot.sharebot import ShareBot

logging.basicConfig(level=logging.DEBUG)

# TODO add an inchequeable reaction bot
# TODO add a diego bot
# TODO add pelito bot
BOTS = [ShareBot('bono', channel='out_of_context_bono', emoji=':bono3:', username='BonoBot'),
        ShareBot('lambdabot', channel='out_of_context_lambda', emoji=':lambda:', username='LambdaBot'),
        FileBot('pollo', icon_emoji=':pollobot:', username='PolloBot', source_file='pollo.txt'),
        FileBot(['peron', 'pocho', 'el general'], icon_emoji=':pochobot:', username='PochoBot', source_file='pocho.txt')]


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
