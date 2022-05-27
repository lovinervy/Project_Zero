import subprocess
import os
import torch


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


def say_in_russia(subs: dict, output: str = 'output')-> dict:
    if not os.path.isdir(output):
        os.makedirs(output)
    language = 'ru'
    model_id = 'ru_v3'
    sample_rate = 24000
    speaker = 'xenia'
    device = torch.device('cpu')

    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_tts',
                                        language=language,
                                        speaker=model_id)
    model.to(device)  # gpu or cpu

    for k, v in subs.items():
        subs[k]['path'] = f'{output}/{k}.wav'
        model.save_wav(text=v['text'],
            speaker=speaker,
            sample_rate=sample_rate,
            audio_path = f'{output}/{k}.wav'
            )
    return subs


def retell_quickly_in_russia(filepath: str, text: str) -> None:
    text = f'<speak><p><prosody rate="fast">{text}</prosody></p></speak>'

    language = 'ru'
    model_id = 'ru_v3'
    sample_rate = 24000
    speaker = 'xenia'
    device = torch.device('cpu')

    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_tts',
                                        language=language,
                                        speaker=model_id)
    model.to(device)  # gpu or cpu

    model.save_wav(ssml_text=text,
        speaker=speaker,
        sample_rate=sample_rate,
        audio_path = filepath
        )
    

def say_in_english(subs: dict, output: str = 'output') -> dict:
    if not os.path.isdir(output):
        os.makedirs(output)
    language = 'en'
    model_id = 'lj_v2'
    sample_rate = 16000
    speaker = 'xenia'
    device = torch.device('cpu')
    model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                        model='silero_tts',
                                        language=language,
                                        speaker=model_id)
    model.to(device)  # gpu or cpu

    for k, v in subs.items():
        text = text_splitter(v['text'])
        if len(text) > 1:
            files = []
            for i in range(len(text)):
                filename = f'{output}/{k}_{i}.wav'
                model.save_wav(texts=text[i],
                    sample_rate=sample_rate,
                    )
                os.rename('test_000.wav', filename)
                files.append(filename)
            f = ''
            for i in files:
                f += f"file '{i}'\n"
            with open('files.txt', 'w') as t:
                t.write(f)
            files.append('files.txt')
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', 'files.txt',
                '-acodec', 'copy',
                f'{output}/{k}.wav'
            ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            for i in files:
                os.remove(i)
        else:
            model.save_wav(texts=text.pop(),
                sample_rate=sample_rate,
                )
            os.rename('test_000.wav', f'{output}/{k}.wav')
        subs[k]['path'] = f'{output}/{k}.wav'
    return subs
    

def clean(subs: dict, output: str = 'output'):
    for k in subs.keys():
        os.remove(f'{subs[k]["path"]}')
    os.removedirs(output)
