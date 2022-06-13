from typing import List

from pydub import AudioSegment

from Translator.custom_typing import AudioMessage


def mix_translate_audio_with_original(audio_messages: List[AudioMessage], source_audio: str, output_audio: str):
    """
    Смешивает переведенные фразы с оригинальной аудио дорожкой\n
    audio_messages: List[AudioMessage] ---> список переведенных фраз\n
    source_audio: str ---> путь к исходной аудиодорожки\n
    output_audio: str ---> путь к выходной аудиодорожки
    """
    source_audio = AudioSegment.from_wav(source_audio)
    for message in audio_messages:
        audio_message = AudioSegment.from_wav(message.path_to_message)
        source_audio = source_audio.overlay(audio_message,
                                            position=message.subtitle_block.start,
                                            gain_during_overlay=-10
                                            )
        source_audio.export(out_f=output_audio, format='wav')
