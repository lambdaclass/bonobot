import random
import requests
import os
import re


def get_messages(channels, limit=100):
    result = []
    for channel_name in channels:
        messages = []
        channel = get_channel_id(channel_name)
        cursor = None
        while True:
            resp = slack_request('conversations.history',
                                 channel=channel, cursor=cursor)
            messages += [msg['text'] for msg in resp['messages']]

            if not resp['has_more'] or len(messages) > limit:
                break
            cursor = resp['response_metadata'].get('next_cursor')

        result += messages
    return result


def get_channel_id(channel_name):
    channels = slack_request('conversations.list')['channels']
    return [ch for ch in channels if ch['name'] == channel_name][0]['id']


def slack_request(resource, **params):
    params['token'] = os.environ.get('SLACK_API_TOKEN')
    resp = requests.get('https://slack.com/api/' + resource, params=params)
    return resp.json()


def extract_phrases(messages):
    results = set()
    for message in messages:
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


def random_haiku(phrases):
    return '\n'.join([random.choice(phrases), random.choice(phrases), random.choice(phrases)])
