import random
import requests
import os
from syltippy import syllabize
import re


def get_messages(channel_name, limit=100):
    channel = get_channel_id(channel_name)
    messages = []
    cursor = None
    while True:
        resp = slack_request('conversations.history',
                             channel=channel, cursor=cursor)
        messages += [msg['text'] for msg in resp['messages']]

        if not resp['has_more'] or len(messages) > limit:
            break
        cursor = resp['response_metadata'].get('next_cursor')

    return messages


def get_channel_id(channel_name):
    channels = slack_request('conversations.list')['channels']
    return [ch for ch in channels if ch['name'] == channel_name][0]['id']


def slack_request(resource, **params):
    params['token'] = os.environ.get('SLACK_API_TOKEN')
    resp = requests.get('https://slack.com/api/' + resource, params=params)
    return resp.json()


# def extract_phrases(messages):
#     five = []
#     seven = []
#     for message in messages:
#         # FIXME remove :something: and <something>
#         message = re.sub("[\<\:].*?[\>\:]", "", message)
#         phrases = message.replace('.', '\n').replace(';', '\n').split('\n')
#         for phrase in phrases:
#             phrase = phrase.strip()
#             syllables = len(syllabize(phrase)[0])
#             if syllables == 5:
#                 five.append(phrase)
#             elif syllables == 7:
#                 seven.append(phrase)
#     return five, seven


# def random_haiku(five, seven):
#     return '\n'.join([random.choice(five), random.choice(seven), random.choice(five)])

def extract_phrases(messages):
    results = set()
    for message in messages:
        # FIXME properly remove links
        # remove :something: and <something>
        message = re.sub(":[^\s]+:", "", message)
        phrases = message.split('\n')
        for phrase in phrases:
            phrase = phrase.strip()
            if '//' in phrase or '<' in phrase:
                continue
            elif 1 < len(phrase.split(' ')) < 8:
                results.add(phrase)

    return list(results)


def random_haiku(phrases):
    # phrases = sorted([random.choice(phrases), random.choice(phrases), random.choice(phrases)], key=len)
    # return '\n'.join([phrases[1], phrases[2], phrases[0]])
    return '\n'.join([random.choice(phrases), random.choice(phrases), random.choice(phrases)])
