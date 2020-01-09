"""
Requires SLACK_TOKEN to be set in the environment
"""
import requests
import os
import random

TOKEN = os.environ.get('SLACK_TOKEN')
BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

if not TOKEN or not BOT_TOKEN:
    raise Exception('SLACK_TOKEN not set')

def slack_request(resource, **params):
    params['token'] = TOKEN
    resp = requests.get('https://slack.com/api/' + resource, params=params)
    return resp.json()

def bot_request(resource, **data):
    data['token'] = BOT_TOKEN
    requests.post('https://slack.com/api/' + resource, json=data)

def get_channel():
    channels = slack_request('conversations.list')['channels']
    return [ch for ch in channels if ch['name'] == 'out_of_context_bono'][0]

def get_messages(channel):
    messages = []
    cursor = None
    while True:
        resp = slack_request('conversations.history', channel=channel['id'], cursor=cursor)
        messages += [msg['attachments'][0]['text']
                     for msg in resp['messages']
                     if is_bono_message(msg)]

        if not resp['has_more']:
            break
        cursor = resp['response_metadata']['next_cursor']

    return messages

def is_bono_message(msg):
    return ('attachments' in msg
            and msg['attachments'][0].get('text')
            and msg['attachments'][0].get('author_name') == 'bono')

def get_random_bono():
    ch = get_channel()
    messages = get_messages(ch)
    return random.choice(messages)

def send_response(channel, text):
    bot_request('chat.postMessage', channel=channel, text=text,
                as_user=False, icon_emoji=':bono3:', username='BonoBot')
