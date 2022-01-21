import os
import random

import requests
import re
import string


class BaseBot():
    def __init__(self, name, icon_emoji, username):

        if isinstance(name, str):
            self.names = [name.lower()]
        elif isinstance(name, list):
            self.names = [name.lower() for name in name]

        self.api_token = os.environ.get('SLACK_API_TOKEN')
        self.bot_token = os.environ.get('SLACK_BOT_TOKEN')
        self.icon_emoji = icon_emoji
        self.username = username

    def is_relevant(self, type, text='', **kwargs):
        if type == 'app_mention':
            return True
        elif type == 'message':
            words = re.sub('['+string.punctuation+']', '', text.lower()).split()
            return bool(set(words) & set(self.names))

    def send_response(self, channel, text, **kwargs):
        response = self.get_message(text)
        self._bot_request('chat.postMessage', channel=channel, text=response,
                          as_user=False, icon_emoji=self.icon_emoji, username=self.username)

    def get_message(self, _text):
        raise NotImplementedError

    def _bot_request(self, resource, **data):
        headers = {'Authorization': 'Bearer ' + self.bot_token}
        requests.post('https://slack.com/api/' + resource,
                      json=data, headers=headers)


class FileBot(BaseBot):
    def __init__(self, name, icon_emoji, username, source_file):
        super().__init__(name, icon_emoji, username)

        with open(source_file) as f:
            self.messages = f.read().splitlines()

    def get_message(self, _text):
        return random.choice(self.messages)

class InchequeableBot(BaseBot):
    def __init__(self):
        super().__init__('inchequeable', ':inchequeable:', 'SlackBot')

        with open('inchequeable.txt') as f:
            self.triggers = f.read().splitlines()

    def is_relevant(self, type, text='', **kwargs):
        if type == 'message':
            return any([line.lower() in text for line in self.triggers])
        elif type == 'reaction_added':
            return kwargs['reaction'] == 'inchequeable'

    def send_response(self, type, **kwargs):
        if type == 'message':
            source = kwargs
        elif type == 'reaction_added':
            source = kwargs['item']
        self._bot_request('reactions.add', channel=source['channel'], timestamp=source['ts'], name='inchequeable')
