import logging
import os
import random
import re

import requests
from cachetools import TTLCache, cached

from bonobot.basebot import BaseBot

# TODO merge this and the base bot module


class ShareBot(BaseBot):
    def __init__(self, name, channel, emoji, username, filter_author=None):
        super().__init__(name, emoji, username)
        self.channel_id = slack_channel_id(channel)
        self.filter_author = filter_author

    def get_message(self, _text):
        messages = self.get_messages()
        return random.choice(messages)

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
    def __init__(self, name, channels, emoji, username):
        """
        channels is a channel name -> max phrases dict, used to control the amount
        of phrases to consider per each of the channels loaded.
        """
        super().__init__(name, emoji, username)
        self.channels = [(slack_channel_id(ch), limit)
                         for ch, limit in channels.items()]

    def get_message(self, _text):
        phrases = self.get_phrases()
        # builds the haiku out of 3 short phrases
        return '\n'.join([random.choice(phrases),
                          random.choice(phrases),
                          random.choice(phrases)])

    @cached(cache=TTLCache(maxsize=1, ttl=36000))
    def get_phrases(self):
        results = set()
        for channel, channel_limit in self.channels:
            phrases = set()
            cursor = None
            while True:
                resp = slack_request('conversations.history',
                                     channel=channel, cursor=cursor, limit=200)
                phrases.update(*[self.parse_phrases(msg['text'])
                                 for msg in resp['messages']])

                if not resp['has_more'] or len(phrases) > channel_limit:
                    break
                cursor = resp['response_metadata'].get('next_cursor')

            logging.info("Saved %s phrases for channel %s", len(phrases), channel)
            results.update(phrases)
        return list(results)

    def parse_phrases(self, message):
        # remove :emojis:
        message = re.sub(":[^\s]+:", "", message)
        phrases = message.split('\n')
        results = []
        for phrase in phrases:
            phrase = phrase.strip()
            if '//' in phrase or '<' in phrase:
                # no links, no mentions
                continue
            elif 1 < len(phrase.split(' ')) < 8:
                results.append(phrase)

        return results


# TODO move to a slack api module
def slack_channel_id(channel_name):
    channels = slack_request('conversations.list')['channels']
    return [ch for ch in channels if ch['name'] == channel_name][0]['id']


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
