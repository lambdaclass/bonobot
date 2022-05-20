import os

import requests


def channel_id(channel_name):
    channels = api_request('conversations.list')['channels']
    return [ch for ch in channels if ch['name'] == channel_name][0]['id']


def is_share_message(msg, expected_author):
    if not 'attachments' in msg:
        return False

    text = msg['attachments'][0].get('text')
    author = msg['attachments'][0].get('author_name', '')
    return text and (not expected_author or expected_author.lower() == author.lower())


def bot_request(resource, **data):
    headers = {'Authorization': 'Bearer ' + os.environ.get('SLACK_BOT_TOKEN')}
    requests.post('https://slack.com/api/' + resource,
                  json=data, headers=headers)


def api_request(resource, **params):
    params['token'] = os.environ.get('SLACK_API_TOKEN')
    resp = requests.get('https://slack.com/api/' + resource, params=params)
    return resp.json()
