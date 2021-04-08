import random

import requests
from cachetools import TTLCache, cached

from bonobot.basebot import BaseBot


def is_share_message(msg, expected_author):
    if not 'attachments' in msg:
        return False

    text = msg['attachments'][0].get('text')
    author = msg['attachments'][0].get('author_name', '')
    return text and (not expected_author or expected_author.lower() == author.lower())


class ShareBot(BaseBot):
    def __init__(self, name, channel, emoji, username, filter_author=None):
        super().__init__(name, emoji, username)
        self.channel_id = self.get_channel_id(channel)['id']
        self.filter_author = filter_author

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
                         if is_share_message(msg, self.filter_author)]

            if not resp['has_more']:
                break
            cursor = resp['response_metadata']['next_cursor']

        return messages
