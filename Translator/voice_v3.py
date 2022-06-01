import os.path
import subprocess
from typing import List
import json
import requests
# from pydub import AudioSegment

from Translator.yandex import update_token
from Translator.custom_typing import SubtitleBlock, AudioMessage


def raw_to_wav(raw_path: str, wav_path: str):
    cmd = [
        'sox',
        '-r', '8000',
        '-b', '16',
        '-e', 'signed-integer',
        '-c', '1',
        raw_path, wav_path
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    os.remove(raw_path)


def synthesize(language: str, text: str, speed: float = 1.2, is_crashed: bool = False):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    with open('config.json', 'r') as f:
        config = json.load(f)
    headers = {
        'Authorization': 'Bearer ' + config['yandex']['token'],
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'speed': speed,
        'format': 'lpcm',
        'sampleRateHertz': 8000,
        'voice': 'alena',
        'folderId': config['yandex']['folder_id']
    }
    try:
        with requests.post(url, headers=headers, data=data, stream=True) as resp:
            if resp.status_code != 200:
                raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

            for chunk in resp.iter_content(chunk_size=None):
                yield chunk
    except RuntimeError:
        if is_crashed:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
        update_token()
        synthesize(language, text, True)


def say_in_russian(subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    if not os.path.isdir(output):
        os.makedirs(output)

    audio_messages: List[AudioMessage] = []
    for i, block in enumerate(subtitle):
        raw_path = f'{output}/{i}.raw'
        wav_path = f'{output}/{i}.wav'
        expected_length = block.end - block.start
        with open(raw_path, 'wb') as f:
            for audio_content in synthesize('ru_RU', block.text):
                f.write(audio_content)
        # audio_message = AudioSegment.from_file(wav_path)
        # if len(audio_message) > expected_length:
        #     speed_up = round(len(audio_message) / expected_length, 1)
        #     if speed_up > 1.5:
        #         speed_up = 1.5
        #     with open(wav_path, 'wb') as f:
        #         for audio_content in synthesize('ru_RU', block.text, speed_up):
        #             f.write(audio_content)

        raw_to_wav(raw_path, wav_path)
        audio_messages.append(
            AudioMessage(
                path_to_message=wav_path,
                expected_length=expected_length,
                subtitle_block=block
            )
        )
    return audio_messages


def say_in_english(subtitle, output):
    pass


def clean(audio_messages: List[AudioMessage], output: str = 'output'):
    for message in audio_messages:
        os.remove(message.path_to_message)
    os.removedirs(output)
