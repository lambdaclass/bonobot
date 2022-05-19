import logging
import os
import random
import re

from cachetools import TTLCache, cached

import bonobot.slack as slack
from bonobot.basebot import BaseBot

# TODO merge this and the base bot module


class ShareBot(BaseBot):
    def __init__(self, name, channel, emoji, username, filter_author=None):
        super().__init__(name, emoji, username)
        self.channel_id = slack.channel_id(channel)
        self.filter_author = filter_author

    def get_message(self, _text):
        messages = self.get_messages()
        return random.choice(messages)

    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def get_messages(self):
        messages = []
        cursor = None
        while True:
            resp = slack.api_request('conversations.history',
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
        self.channels = [(slack.channel_id(ch), limit)
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
                resp = slack.api_request('conversations.history',
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
