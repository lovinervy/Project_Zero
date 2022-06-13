import os
from typing import List
import pyttsx3

from custom_typing import SubtitleBlock, AudioMessage


class VoiceEngine:
    def __init__(self, lang: str = 'ru_RU', gender: str = 'female', temppath: str = 'temp') -> None:
        self.TEMP_DATA = temppath
        self.temp_files = []
        if not os.path.isdir(self.TEMP_DATA):
            os.makedirs(self.TEMP_DATA)
        else:
            self.temp_files = map(self.__add_tmp_path, os.listdir(self.TEMP_DATA))
            self.clean()

        if gender.lower() == 'male':
            voice_gender = 'VoiceGenderMale'
        elif gender.lower() == 'female':
            voice_gender = 'VoiceGenderFemale'
        else:
            raise BaseException(f'Expected gender "male" or "female" but got "{gender}"')

        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        self.support_voices = voices
        
        is_supported = False
        for num in range(len(voices)):
            if voices[num].gender == voice_gender and voices[num].languages == [lang]:
                self.tts_engine.setProperty('voice', voices[num].id)
                is_supported = True
                break
        
        if not is_supported:
            raise BaseException(f'Engine not supported with language: "{lang}" and gender: "{gender}"')

    def say(self, text: str, output: str = 'output') -> str:
        song = f'{self.TEMP_DATA}/{output}.wav'
        self.temp_files.append(song)
        self.tts_engine.save_to_file(text, song)
        return song

    def do(self):
        self.tts_engine.runAndWait()

    def clean(self):
        for voice in self.temp_files:
            os.remove(voice)
        self.temp_files = []

    def __add_tmp_path(self, filename: str) -> str:
        return f'{self.TEMP_DATA}/{filename}'


def synthesize_audio_files(language: str, subtitle: List[SubtitleBlock], output: str) -> List[AudioMessage]:
    if not os.path.isdir(output):
        os.makedirs(output)

    engine = VoiceEngine(language, temppath=output)

    audio_messages: List[AudioMessage] = []
    for i, block in enumerate(subtitle):
        wav_path = engine.say(block.text, str(i))
        audio_messages.append(
            AudioMessage(
                path_to_message=wav_path,
                subtitle_block=block
            )
        )
    engine.do()
    return audio_messages


def say_in_russian(subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    return synthesize_audio_files('ru_RU', subtitle, output)


def say_in_english(subtitle: List[SubtitleBlock], output: str = 'output') -> List[AudioMessage]:
    return synthesize_audio_files('en_US', subtitle, output)


def clean(audio_messages: List[AudioMessage], output: str = 'output'):
    for message in audio_messages:
        os.remove(message.path_to_message)
    os.removedirs(output)
