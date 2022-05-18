import os
import random
import re

import requests
from cachetools import TTLCache, cached

from bonobot.basebot import BaseBot


class ShareBot(BaseBot):
    def __init__(self, name, channel, emoji, username, filter_author=None):
        super().__init__(name, emoji, username)
        self.channel_id = self.get_channel_id(channel)['id']
        self.filter_author = filter_author

    def get_message(self, _text):
        messages = self.get_messages()
        return random.choice(messages)

    def get_channel_id(self, channel_name):
        channels = slack_request('conversations.list')['channels']
        return [ch for ch in channels if ch['name'] == channel_name][0]

    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def get_messages(self):
        messages = []
        cursor = None
        while True:
            resp = slack_request('conversations.history',
                                 channel=self.channel_id, cursor=cursor)
            messages += [msg['attachments'][0]['text']
                         for msg in resp['messages']
                         if is_share_message(msg, self.filter_author)]

            if not resp['has_more']:
                break
            cursor = resp['response_metadata']['next_cursor']

        return messages


class HaikuBot(BaseBot):
    def __init__(self, name, channels, emoji, username, limit=1000):
        super().__init__(name, emoji, username)
        self.channels = [self.get_channel_id(ch) for ch in channels]
        self.limit = limit

    def get_message(self, _text):
        phrases = self.get_phrases()
        # builds the haiku out of 3 short phrases
        return '\n'.join([random.choice(phrases),
                          random.choice(phrases),
                          random.choice(phrases)])

    def get_channel_id(self, channel_name):
        channels = slack_request('conversations.list')['channels']
        return [ch for ch in channels if ch['name'] == channel_name][0]['id']

    @cached(cache=TTLCache(maxsize=1, ttl=36000))
    def get_phrases(self):
        """
        Parse a list of unique short phrases out of slack messages from the
        configured channels.
        """
        results = set()
        for message in self.get_messages():
            # remove :emojis:
            message = re.sub(":[^\s]+:", "", message)
            phrases = message.split('\n')
            for phrase in phrases:
                phrase = phrase.strip()
                if '//' in phrase or '<' in phrase:
                    # no links, no mentions
                    continue
                elif 1 < len(phrase.split(' ')) < 8:
                    results.add(phrase)

        return list(results)

    def get_messages(self):
        "Fetch a list of up to `self.limit` messages from each channel in `self.channels`"
        result = []
        for channel in self.channels:
            messages = []
            cursor = None
            while True:
                resp = slack_request('conversations.history',
                                     channel=channel, cursor=cursor)
                messages += [msg['text'] for msg in resp['messages']]

                if not resp['has_more'] or len(messages) > self.limit:
                    break
                cursor = resp['response_metadata'].get('next_cursor')

            result += messages
        return result


def is_share_message(msg, expected_author):
    if not 'attachments' in msg:
        return False

    text = msg['attachments'][0].get('text')
    author = msg['attachments'][0].get('author_name', '')
    return text and (not expected_author or expected_author.lower() == author.lower())


def slack_request(resource, **params):
    params['token'] = os.environ.get('SLACK_API_TOKEN')
    resp = requests.get('https://slack.com/api/' + resource, params=params)
    return resp.json()
