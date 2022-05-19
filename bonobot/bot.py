import logging
import os
import random
import re
import string

from cachetools import TTLCache, cached

import bonobot.slack as slack


class BaseBot():
    def __init__(self, name, icon_emoji, username):

        if isinstance(name, str):
            self.names = [name.lower()]
        elif isinstance(name, list):
            self.names = [name.lower() for name in name]

        self.icon_emoji = icon_emoji
        self.username = username

    def is_relevant(self, type, text='', **kwargs):
        if type == 'app_mention':
            return True
        elif type == 'message':
            words = re.sub('[' + string.punctuation + ']', '', text.lower()).split()
            return bool(set(words) & set(self.names))

    def send_response(self, channel, text, **kwargs):
        response = self.get_message(text)
        slack.bot_request('chat.postMessage', channel=channel, text=response,
                          as_user=False, icon_emoji=self.icon_emoji, username=self.username)

    def get_message(self, _text):
        raise NotImplementedError


class FileBot(BaseBot):
    "When mentioned, Replies with a random message from an input text file."

    def __init__(self, name, icon_emoji, username, source_file):
        super().__init__(name, icon_emoji, username)

        with open(source_file) as f:
            self.messages = f.read().splitlines()

    def get_message(self, _text):
        return random.choice(self.messages)


class InchequeableBot(BaseBot):
    """
    Adds an :inchequeable: emoji reaction to any message that contains any of the trigger phrases
    from the input text file. Also adds +1 to any :inchequeable: reaction from another user.
    """

    def __init__(self):
        super().__init__('inchequeable', ':inchequeable:', 'SlackBot')

        with open('inchequeable.txt') as f:
            self.triggers = f.read().splitlines()

    def is_relevant(self, type, text='', **kwargs):
        if type == 'message':
            lowcase_text = text.lower()
            return any([line.lower() in lowcase_text for line in self.triggers])
        elif type == 'reaction_added':
            return kwargs['reaction'] == 'inchequeable'

    def send_response(self, type, **kwargs):
        if type == 'message':
            source = kwargs
        elif type == 'reaction_added':
            source = kwargs['item']
        slack.bot_request('reactions.add', channel=source['channel'], timestamp=source['ts'], name='inchequeable')


class ShareBot(BaseBot):
    "When mentioned, replies with a random message taken from the messages shared to a given channel."

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
    "When mentioned, replies with 3-line haikus from phrases found in the given channels."

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
