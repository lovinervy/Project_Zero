from Translator import audio, subs, voice
from deep_translator import GoogleTranslator
from time import time
from pytube import YouTube
import subprocess
import os


DOWNLOAD_PATH = 'download'
OUTPUT_PATH = 'output'
SUBS_PATH = 'subtitles'
VIDEO_PATH = 'video'
AUDIO_PATH = 'audio'


if not os.path.isdir(DOWNLOAD_PATH):    # Create download path
    os.makedirs(DOWNLOAD_PATH)
if not os.path.isdir(OUTPUT_PATH):      # Create output path
    os.makedirs(OUTPUT_PATH)
if not os.path.isdir(SUBS_PATH):        # Create subtitles path
    os.makedirs(SUBS_PATH)
if not os.path.isdir(VIDEO_PATH):       # Create videos path
    os.makedirs(VIDEO_PATH)
if not os.path.isdir(AUDIO_PATH):       # Create audios path
    os.makedirs(AUDIO_PATH)


CONVERT_CODE = {
    'en'    : 'en_US',
    'a.en'  : 'en_US',
    'ru'    : 'ru_RU',
    'a.ru'  : 'ru_RU',
}


SUPPORTED_LANGUAGES = [
    'English',
    'Русский',
    # 'Башҡортса'
]

PRIORITY_TRANSLATE = {
    'english':      ['english', 'russian', ],
    'русский':      ['russian', 'english', ],
    # 'Башҡортса':    ['Bashkir', 'Russian', 'English'],
}


LANGUAGES_CODE = {
    'en_US' : 'english',
    'ru_RU' : 'русский',
}


def get_support_subs(url: str) -> list:
    s = subs.Subs(url)
    languages = s.get_support_languages()
    if languages:
        return True
    return False


def download_yt_content(url) -> tuple[str]:
    yt = YouTube(url)
    videos: list[classmethod] = yt.streams.filter(progressive=False)
    max_resolution: int = 0
    for v in videos:
        if v.resolution:
            resolution = int(v.resolution[:-1])
        else:
            resolution = 0
        if resolution > max_resolution:
            max_resolution = resolution
            video: classmethod = v

    filename = f"{int(time() // 1)}.mp4"
    video: str = video.download(output_path=VIDEO_PATH, filename=filename)
    if video[len(video) - 5:] == '.webm':
        audio = video.split('/')[-1][:-5] + '.mp4'
    else:
        audio: str = video.split('/')[-1]

    audio: str = yt.streams.get_audio_only().download(output_path=AUDIO_PATH, filename=filename)

    video = f'{VIDEO_PATH}/' + video.split(f'/{VIDEO_PATH}/')[-1]
    audio = f'{AUDIO_PATH}/' + audio.split(f'/{AUDIO_PATH}/')[-1]

    return (video, audio)


def modify_voice(language: str, subs: dict, song: str):
    t = int(time() // 1)
    file = os.path.abspath('')
    s = song[len(file):-4]
    TEMP_FILEPATH = f'.{s}{t}'

    for k, v in LANGUAGES_CODE.items():
        if v == language:
            voice_engine = voice.VoiceEngine(lang=k, temppath=TEMP_FILEPATH)
            break
    
    for k, v in subs.items():
        subs[k]['path'] = voice_engine.say(v['text'], f'{k}')
    voice_engine.do()
    new_song = song[:-4] + language + '.mp4'
    audio.mix_translate_audio_with_original(subs, song, new_song)
    voice_engine.clean()
    os.removedirs(TEMP_FILEPATH)
    return new_song


def get_subs(url: str, need_langs: list):
    """
    if not preffered subs, get preffered second subs
    if not seconds subs get any not autogen subtitles
    else get any subs 
    """
    S = subs.Subs(url)
    languages = S.get_support_languages()
    access_language = ''
    if not languages:
        return ('Not any subs', None)

    for need_lang in need_langs:
        for lang in languages:
            if need_lang == lang.name.lower():
                access_language = need_lang
                code = lang.code
                break
            if access_language: break
    
    if not access_language:
        for lang in languages:
            if not lang.code.startswith('a.'):
                access_language = lang.name.lower()
                code = lang.code
                break
    if not access_language:
        for lang in languages:
            access_language = lang.name.split(' ')[0].lower()
            code = lang.code

    S.set_lang(code)
    sub = S.get_subs_with_filter()
    return (access_language, sub)


def save_subs(caption: dict) -> str:
    t = int(time() // 1)
    caption = subs.dict_to_srt(caption)
    filepath = f'{SUBS_PATH}/{t}.srt'
    with open(filepath, 'w') as f:
        f.write(caption)
    return filepath


def get_dict_subs_from_data(filepath: str):
    with open(filepath, 'r') as f:
        srt = f.read()
    
    dict_subs = subs.srt_to_dict(srt)
    return dict_subs


def merge_video_audio(video: str, audio: str):
    t = int(time() // 1)
    save_video = f'{OUTPUT_PATH}/{t}.mp4'
    cmd = [
        'ffmpeg',
        '-i', video,
        '-i', audio,
        '-vcodec:', 'copy',
        save_video
    ]
    worker = subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return save_video

def merge_video_subs(video: str, audio: str, subs: str):
    t = int(time() // 1)
    save_video = f'{OUTPUT_PATH}/{t}.mp4'
    cmd = [
        'ffmpeg',
        '-i', video,
        '-i', audio,
        '-i', subs,
        '-c', 'copy',
        '-c:s', 'mov_text',
        save_video
    ]
    worker = subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return save_video


def translate(sub: dict, source: str, target: str):
    key = {
        'русский': 'ru',
        'english': 'en' 
    }
    languages = GoogleTranslator().get_supported_languages(as_dict=True)
    source = languages.get(source, 'auto')
    tr = GoogleTranslator(
        source=source,
        target=key[target],
    )
    for k, v in sub.items():
        text = tr.translate(v['text'])
        sub[k]['text'] = text
    return sub
