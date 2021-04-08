import random

import requests
from cachetools import TTLCache, cached

from bonobot.basebot import BaseBot


def is_bono_message(msg):
    return ('attachments' in msg and
            msg['attachments'][0].get('text'))


class ShareBot(BaseBot):
    def __init__(self, name, channel, emoji, username):
        super().__init__(name, emoji, username)
        self.channel_id = self.get_channel_id(channel)['id']

    def get_message(self, _text):
        messages = self.get_messages()
        return random.choice(messages)

    def slack_request(self, resource, **params):
        params['token'] = self.api_token
        resp = requests.get('https://slack.com/api/' + resource, params=params)
        return resp.json()

    def get_channel_id(self, channel_name):
        channels = self.slack_request('conversations.list')['channels']
        return [ch for ch in channels if ch['name'] == channel_name][0]

    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def get_messages(self):
        messages = []
        cursor = None
        while True:
            resp = self.slack_request('conversations.history',
                                      channel=self.channel_id, cursor=cursor)
            messages += [msg['attachments'][0]['text']
                         for msg in resp['messages']
                         if is_bono_message(msg)]

            if not resp['has_more']:
                break
            cursor = resp['response_metadata']['next_cursor']

        return messages
