import requests
import json


def update_token() -> None:
    with open('config.json', 'r') as f:
        data = json.load(f)
    oauth = data['yandex']['oauth']

    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    body = {
        'yandexPassportOauthToken': oauth
    }
    resp = requests.post(url, json=body)
    if resp.status_code != 200:
        raise RuntimeError(
            f'Invalid response received: code: {resp.status_code}, message: {resp.text}')

    content = json.loads(resp.content)
    data['yandex']['token'] = content['iamToken']
    with open('config.json', 'w') as f:
        json.dump(data, f)
