import pyttsx3
import os


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

        ttsEngine = pyttsx3.init()
        voices = ttsEngine.getProperty('voices')
        self.support_voices = voices
        
        is_supported = False
        for num in range(len(voices)):
            if voices[num].gender == voice_gender and voices[num].languages == [lang]:
                ttsEngine.setProperty('voice', voices[num].id)
                is_supported = True
                break
        
        if not is_supported:
            raise BaseException(f'Engine not supported with language: "{lang}" and gender: "{gender}"')
        
        self.ttsEngine = ttsEngine

    def say(self, text: str, output: str = 'output') -> str:
        song = f'{self.TEMP_DATA}/{output}.mp4a'
        self.temp_files.append(song)
        self.ttsEngine.save_to_file(text, song)
        return song

    def do(self):
        self.ttsEngine.runAndWait()

    def clean(self):
        for voice in self.temp_files:
            os.remove(voice)
        self.temp_files = []

    def __add_tmp_path(self, filename: str) -> str:
        return f'{self.TEMP_DATA}/{filename}'