import os.path
import subprocess
from typing import List
import json
import requests

from Translator.yandex import update_token
from Translator.custom_typing import SubtitleBlock, AudioMessage


# Need yandex tokens. Specify yandex.folder_id and yandex.oauth in config.json


def raw_to_wav(raw_path: str, wav_path: str):
    cmd = [
        'sox',
        '-r', '16000',
        '-b', '16',
        '-e', 'signed-integer',
        '-c', '1',
        raw_path, wav_path
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT)
    os.remove(raw_path)


def synthesize(language: str, text: str, speed: float = 1.2, is_crashed: bool = False):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    with open('config.json', 'r') as f:
        config = json.load(f)
    headers = {
        'Authorization': 'Bearer ' + config['yandex']['token'],
    }
    v = 'john' if language == 'en-US' else 'alena'
    data = {
        'text': text,
        'lang': language,
        'speed': speed,
        'sampleRateHertz': 16000,
        'voice': v,
        'folderId': config['yandex']['folder_id']
    }
    try:
        with requests.post(url, headers=headers, data=data, stream=True) as resp:
            if resp.status_code != 200:
                raise RuntimeError("Invalid response received: code: %d, message: %s" % (
                    resp.status_code, resp.text))

            for chunk in resp.iter_content(chunk_size=None):
                yield chunk
    except RuntimeError:
        if is_crashed:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (
                resp.status_code, resp.text))
        update_token()
        synthesize(language, text, True)


def synthesize_audio_files(language: str, subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    if not os.path.isdir(output):
        os.makedirs(output)

    audio_messages: List[AudioMessage] = []
    for i, block in enumerate(subtitle):
        wav_path = f'{output}/{i}.wav'
        with open(wav_path, 'wb') as f:
            for audio_content in synthesize(language, block.text):
                f.write(audio_content)
        audio_messages.append(
            AudioMessage(
                path_to_message=wav_path,
                subtitle_block=block
            )
        )
    return audio_messages


def say_in_russian(subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    return synthesize_audio_files('ru-RU', subtitle, output)


def say_in_english(subtitle, output) -> List[AudioMessage]:
    return synthesize_audio_files('en-US', subtitle, output)


def clean(audio_messages: List[AudioMessage], output: str = 'output'):
    for message in audio_messages:
        os.remove(message.path_to_message)
    os.removedirs(output)
