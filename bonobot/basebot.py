import random

import requests

class BaseBot():
    def __init__(self, token, icon_emoji, username):
        self.token = token
        self.icon_emoji = icon_emoji
        self.username = username

    def send_response(self, channel, text):
        response = self.get_message(text)
        self._bot_request('chat.postMessage', channel=channel, text=response,
                          as_user=False, icon_emoji=self.icon_emoji, username=self.username)

    def get_message(self, _text):
        raise NotImplementedError

    def _bot_request(self, resource, **data):
        headers = {'Authorization': 'Bearer ' + self.token}
        requests.post('https://slack.com/api/' + resource,
                      json=data, headers=headers)


class FileBot(BaseBot):
    def __init__(self, token, icon_emoji, username, source_file):
        super().__init__(token, icon_emoji, username)

        with open(source_file) as f:
            self.messages = f.read().splitlines()

    def get_message(self, _text):
        return random.choice(self.messages)
