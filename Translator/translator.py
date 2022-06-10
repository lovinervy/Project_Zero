from time import time
from typing import List, Tuple, Union
import subprocess
import os

from deep_translator import GoogleTranslator
from pytube import YouTube, Stream

from Translator import audio, subs, voice_v3
from Translator.custom_typing import PathToFile, SubtitleBlock


RU_A_RU_RU_RU_ = {
    'en': 'en_US',
    'a.en': 'en_US',
    'ru': 'ru_RU',
    'a.ru': 'ru_RU',
}

DOWNLOAD_PATH = 'download'
OUTPUT_PATH = 'output'
SUBS_PATH = 'subtitles'
VIDEO_PATH = 'video'
AUDIO_PATH = 'audio'

if not os.path.isdir(DOWNLOAD_PATH):  # Create download path
    os.makedirs(DOWNLOAD_PATH)
if not os.path.isdir(OUTPUT_PATH):  # Create output path
    os.makedirs(OUTPUT_PATH)
if not os.path.isdir(SUBS_PATH):  # Create subtitles path
    os.makedirs(SUBS_PATH)
if not os.path.isdir(VIDEO_PATH):  # Create videos path
    os.makedirs(VIDEO_PATH)
if not os.path.isdir(AUDIO_PATH):  # Create audios path
    os.makedirs(AUDIO_PATH)

CONVERT_CODE = RU_A_RU_RU_RU_

SUPPORTED_LANGUAGES = (
    'English',
    'Русский',
    # 'Башҡортса'
)

PRIORITY_TRANSLATE = {
    'english': ['english', 'russian', ],
    'русский': ['russian', 'english', ],
    # 'Башҡортса':    ['Bashkir', 'Russian', 'English'],
}

LANGUAGES_CODE = {
    'en_US': 'english',
    'ru_RU': 'русский',
}


def get_support_subs(url: str) -> bool:
    s = subs.Subs(url)
    languages = s.get_support_languages()
    if languages:
        return True
    return False


def download_yt_content(url) -> PathToFile:
    yt = YouTube(url)
    videos: List[Stream] = yt.streams.filter(progressive=False)
    max_resolution: int = 0
    for v in videos:
        if v.resolution:
            resolution = int(v.resolution[:-1])
        else:
            resolution = 0
        if resolution > max_resolution:
            max_resolution = resolution
            video: Stream = v

    video_name = f"{int(time() // 1)}.mp4"
    audio_name = f"{int(time() // 1)}.aac"
    video_path: str = video.download(output_path=VIDEO_PATH, filename=video_name)
    audio_path: str = yt.streams.get_audio_only().download(output_path=AUDIO_PATH, filename=audio_name)
    cmd = [
        'ffmpeg',
        '-i', audio_path,
        audio_path[:-3] + 'wav'
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    os.remove(audio_path)
    video_path = f'{VIDEO_PATH}/' + video_path.split(f'/{VIDEO_PATH}/')[-1]
    audio_path = f'{AUDIO_PATH}/' + audio_path.split(f'/{AUDIO_PATH}/')[-1][:-3] + 'wav'

    return PathToFile(video_path, audio_path)


def modify_voice(language: str, subtitle: List[SubtitleBlock], song: str) -> str:
    """return path to audio file in local disk"""
    t = int(time() // 1)
    file = os.path.abspath('')
    s = song[len(file):-4]
    filepath = f'.{s}{t}'

    if language == 'русский':
        audio_messages = voice_v3.say_in_russian(subtitle, filepath)
    elif language == 'english':
        audio_messages = voice_v3.say_in_english(subtitle, filepath)
    else:
        raise BaseException(f"Not language: {language}")
    new_song = f'{song[:-4]}{language}.aac'
    audio.mix_translate_audio_with_original(language, audio_messages, song, new_song)
    voice_v3.clean(audio_messages, filepath)
    return new_song


def get_subs(url: str, need_langs: list) -> Union[Tuple[str, None], Tuple[str, List[SubtitleBlock]]]:
    """
    if not preferred subs, get any not autogen subtitles
    else get any subs
    return: access language and subtitle
    """
    subs_format = subs.Subs(url)
    languages = subs_format.get_support_languages()
    access_language = ''
    if not languages:
        return 'Not any subs', None

    for need_lang in need_langs:
        for lang in languages:
            if need_lang == lang.name.lower():
                access_language = need_lang
                code = lang.code
                break
            if access_language:
                break

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

    subs_format.set_lang(code)
    subtitle = subs_format.format_subtitle()
    return access_language, subtitle


def save_subs(subtitle: List[SubtitleBlock]) -> str:
    t = int(time() // 1)
    caption = subs.list_to_srt(subtitle)
    filepath = f'{SUBS_PATH}/{t}.srt'
    with open(filepath, 'w') as f:
        f.write(caption)
    return filepath


def get_dict_subs_from_data(filepath: str) -> List[SubtitleBlock]:
    with open(filepath, 'r') as f:
        srt = f.read()

    subtitle = subs.srt_to_list(srt)
    return subtitle


def merge_video_audio(path: PathToFile):
    t = int(time() // 1)
    save_video = f'{OUTPUT_PATH}/{t}.mp4'
    cmd = [
        'ffmpeg',
        '-i', path.video,
        '-i', path.audio,
        '-vcodec:', 'copy',
        save_video
    ]
    worker = subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return save_video


def merge_video_subs(path: PathToFile, subs_path: str):
    t = int(time() // 1)
    save_video = f'{OUTPUT_PATH}/{t}.mp4'
    cmd = [
        'ffmpeg',
        '-i', path.video,
        '-i', path.audio,
        '-i', subs_path,
        '-c', 'copy',
        '-c:s', 'mov_text',
        save_video
    ]
    worker = subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return save_video


def translate(subtitle: List[SubtitleBlock], source: str, target: str) -> List[SubtitleBlock]:
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
    for i, block in enumerate(subtitle):
        text = tr.translate(block.text)
        subtitle[i].text = text
    return subtitle
