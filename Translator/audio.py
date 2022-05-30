from typing import List

from pydub import AudioSegment, effects

from Translator.voice_v2 import retell_quickly_in_russian
from Translator.custom_typing import AudioMessage


def _speedup(path: str, text: str) -> AudioSegment:
    """
    Для ускорение аудиодорожки если не успевает в заданный лимит\n
    
    path: str   - путь до исходной аудиодорожки\n
    text: str   - слова которые произносятся в этой дорожке
    """
    retell_quickly_in_russian(path, text)
    voice = AudioSegment.from_file(path)
    return voice


def mix_translate_audio_with_original(language: str, audio_messages: List[AudioMessage], source_audio: str, output_audio: str = 'output.mp4a'):
    """
    Смешивает переведенные фразы с оригинальной аудио дорожкой\n

    lagnuage: str ---> язык у переведенных фраз\n
    audio_messages: List[AudioMessage] ---> список переведенных фраз\n
    source_audio: str ---> путь к исходной аудиодорожки\n
    output_audio: str ---> путь к выходной аудиодорожки
    """
    source_audio = AudioSegment.from_file(source_audio)

    for message in audio_messages:
        audio_message = AudioSegment.from_file(message.path_to_message)
        if len(audio_message) > message.expected_length:
            if language == 'русский':
                audio_message = _speedup(message.path_to_message, message.subtitle_block.text)
            else:
                pass
        source_audio = source_audio.overlay(audio_message,
                                            position=message.subtitle_block.start,
                                            gain_during_overlay=-10
                                            )
        source_audio.export(out_f=output_audio, format='mp3')
