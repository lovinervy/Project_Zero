import subprocess
import os
import shutil
from typing import List
from string import ascii_letters
import torch

from Translator.custom_typing import SubtitleBlock, AudioMessage


def clear_ascii_letters(word):
    def return_chr(char):
        if char not in ascii_letters:
            return char
        return ''
    return ''.join(map(return_chr, word))


def text_splitter(text) -> list:
    max_len = len(text)
    if max_len < 140:
        return [text]
    text = text.split(' ')

    result = []
    cur = 0
    count = 0
    for i in range(len(text)):
        count += len(text[i])
        if count + i > 140:
            tmp = ' '.join(text[cur:i])
            cur = i
            result.append(tmp)
            count = 0
    tmp = ' '.join(text[cur:])
    result.append(tmp)
    return result


def say_in_russian(subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    if not os.path.isdir(output):
        os.makedirs(output)
    device = torch.device('cpu')

    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                              model='silero_tts',
                              language='ru',
                              speaker='ru_v3')
    model.to(device)  # gpu or cpu

    audio_messages: List[AudioMessage] = []
    for i, block in enumerate(subtitle):
        path = f'{output}/{i}.wav'
        text = clear_ascii_letters(block.text)
        expected_length = block.end - block.start
        try:
            model.save_wav(text=text,
                           speaker='xenia',
                           sample_rate=24000,
                           audio_path=path
                           )
        except ValueError:
            shutil.copy('static/silence.wav', path)

        audio_messages.append(
            AudioMessage(
                path_to_message=path,
                expected_length=expected_length,
                subtitle_block=block
            )
        )
    return audio_messages


def retell_quickly_in_russian(filepath: str, text: str) -> None:
    text = f'<speak><p><prosody rate="fast">{text}</prosody></p></speak>'

    device = torch.device('cpu')

    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                              model='silero_tts',
                              language='ru',
                              speaker='ru_v3')
    model.to(device)  # gpu or cpu

    model.save_wav(ssml_text=text,
                   speaker='xenia',
                   sample_rate=24000,
                   audio_path=filepath
                   )


def say_in_english(subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    if not os.path.isdir(output):
        os.makedirs(output)

    device = torch.device('cpu')

    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                              model='silero_tts',
                              language='en',
                              speaker='lj_v2')
    model.to(device)  # gpu or cpu

    audio_messages: List[AudioMessage] = []
    for i, block in enumerate(subtitle):
        text = text_splitter(block.text)
        path = f'{output}/{i}.wav'
        if len(text) > 1:
            filepaths = []
            for j in range(len(text)):
                filepath = f'{output}/{i}_{j}.wav'
                model.save_wav(texts=text[i],
                               sample_rate=16000
                               )
                os.rename('test_000.wav', filepath)
                filepaths.append(filepath)

            concat_files = ''
            for filepath in filepaths:
                concat_files += f"file '{filepath}'\n"
            with open('files.txt', 'w') as f:
                f.write(concat_files)
            filepaths.append('files.txt')

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', 'files.txt',
                '-acodec', 'copy',
                path
            ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            for filepath in filepaths:
                os.remove(filepath)
        else:
            model.save_wav(texts=block.text,
                           sample_rate=16000
                           )
            os.rename('test_000.wav', path)
        audio_messages.append(
            AudioMessage(path_to_message=path,
                         expected_length=block.end - block.start,
                         subtitle_block=block
                         )
        )
    return audio_messages


def clean(audio_messages: List[AudioMessage], output: str = 'output'):
    for message in audio_messages:
        os.remove(message.path_to_message)
    os.removedirs(output)
