from typing import Union

from pytube import YouTube

from database import Database
from Translator import translator
from Translator.subs import srt_to_list
from Translator.custom_typing import SubtitleBlock, PathToFile


def get_subs_from_youtube(url: str, language: str) -> str:
    """
    returns the path to the subtitle in local disk
    """
    languages = translator.PRIORITY_TRANSLATE[language]
    source, subtitle = translator.get_subs(url, languages)
    if source != language:
        subtitle = translator.translate(subtitle, source, language)
    path_to_subtitle = translator.save_subs(subtitle)
    return path_to_subtitle

def valid_url(url: str) -> bool:
    try:
        url = url.split('&')[0]
        YouTube(url)
        return True
    except:
        return False

class ControlDatabase(Database):
    def __init__(self) -> None:
        super().__init__()

    def check_url(self, url: str) -> int:
        """
        if url is in database then returns youtube_id
        else added to database and returns youtube_id
        """
        youtube_id = self.get_youtube_id(url)
        if youtube_id:
            return youtube_id
        return self._add_youtube(url)

    def have_translate(self, url: str, language: str) -> Union[None, tuple]:
        translates = self.select_translates(self.check_url(url))
        for translate in translates:
            if language == translate[2]:
                return translate
        return None

    def have_translate_subs(self, url: str, language: str) -> Union[None, tuple]:
        translate = self.have_translate(url, language)
        if translate:
            return self.select_subtitles(translate[0])
        return None

    def have_translate_voice(self, url: str, language: str) -> Union[None, tuple]:
        translate = self.have_translate(url, language)
        if translate:
            return self.select_voiceovers(translate[0])
        return None

    def have_video(self, url: str) -> Union[None, tuple]:
        video = self.select_video(self.check_url(url))
        if video:
            return video
        return None

    def add_translate(self, url, language):
        youtube_id = self.check_url(url)
        return self.insert_translates(youtube_id, language)

    def add_subtitles(self, url: str, language: str, name: str):
        subs = self.have_translate_subs(url, language)
        if subs:
            self.update_subtitles(subs[0], name)
            return

        translate = self.have_translate(url, language)
        if translate:
            self.insert_subtitles(translate[0], name)
            return

        translate_id = self.add_translate(url, language)
        self.insert_subtitles(translate_id, name)

    def add_voiceover(self, url: str, language: str, name: str):
        voice = self.have_translate_voice(url, language)
        if voice:
            self.update_voiceovers(voice[0], name)
            return

        translate = self.have_translate(url, language)
        if translate:
            self.insert_voiceovers(translate[0], name)
            return

        translated_id = self.add_translate(url, language)
        self.insert_voiceovers(translated_id, name)

    def add_video(self, url: str, name: str):
        youtube_id = self.check_url(url)
        self.insert_video(youtube_id, name)

    def _add_youtube(self, url):
        """
        adds url to database
        """
        youtube_id = self.insert_youtube(url)
        return youtube_id


class TranslateHelper:
    """
    Класс для облегчения получения видео с переведенной аудиодорожкой или
    субтитрой. Достаточно указать требуемые параметры при инициализации класса
    и запустить функцию execute().
    """

    def __init__(self, translate_to: str, url: str, language: str) -> None:
        self.control = ControlDatabase()
        self.url = url
        self.language = language
        self.translate = translate_to

        # Получаем существующие видео и аудио на локальном диске по данному url
        video_data = self.control.have_video(url)
        audio_data = self.control.have_translate_voice(url, 'default')

        # Если есть данные на локальном диске, то используем их, иначе скачиваем из ютуба
        if video_data and audio_data:
            video_path = video_data[2]
            audio_path = audio_data[2]
            self.content = PathToFile(video=video_path, audio=audio_path)
        else:
            self.content = translator.download_yt_content(url)
            self.control.add_video(url, self.content.video)
            self.control.add_voiceover(url, 'default', self.content.audio)

    def execute(self) -> str:
        """
        Функиця для получения видео, с установленными параметрами при
        инициализации класса
        """
        return self.merging()

    def get_audio(self) -> str:
        """
        Функция для получения пути до директории с аудиодорожкой
        удовлетворяющей параметрам url и language, которая была
        установлена при инициализации класса. В случае, если не находит
        удовлетворяющую условиям, генерирует новую аудиодорожку путем
        генерации голоса с требуемым языком и наложением к оригинальной
        дорожке.
        """
        audio = self.control.have_translate_voice(self.url, self.language)
        if audio is not None:
            return audio[2]
        subtitle = self.get_subtitle()
        subtitle_blocks = self.subs_convert_to_blocks(subtitle)
        audio = translator.modify_voice(
            self.language, subtitle_blocks, self.content.audio)
        self.control.add_voiceover(self.url, self.language, audio)
        return audio

    def get_subtitle(self) -> str:
        """
        Функция для получения пути до директории с субтитром
        удовлетворяющей параметрам url и language, которая была
        установлена при инициализации класса. В случае, если не находит
        удовлетворяющую условиям, ищет максимально подходящий вариант
        субтитра, переводит её на требуемый язык и генерирует новые субтитры.
        """
        subs = self.control.have_translate_subs(self.url, self.language)
        if subs is not None:
            return subs[2]
        subs = self.download_subtitile()
        return subs

    def download_subtitile(self) -> str:
        """
        Функция для скачивания субтитры с сервиса ютуб по параметрам url и language,
        которые были установлены во время инициализации класса
        """
        subs = get_subs_from_youtube(self.url, self.language)
        self.control.add_subtitles(self.url, self.language, subs)
        return subs

    def subs_convert_to_blocks(self, subs_path: str) -> list[SubtitleBlock]:
        """
        Функция для конвертации srt субтитра в список из блоков субтитр,
        входным параметром является путь до субтитра на локальном диске
        """
        with open(subs_path, "r", encoding="utf-8") as text:
            srt_subs = text.read()
            subtitle = srt_to_list(srt_subs)
            return subtitle

    def merging(self) -> str:
        """
        Функция для объединения видео и аудио дорожки, а также субтитра,
        зависит от того какой параметр был установлен в translate_to во время
        инициализации класса
        """
        self.content.audio = self.get_audio()
        if self.translate == "Voice":
            return translator.merge_video_audio(self.content)
        elif self.translate == "Subs":
            return translator.merge_video_subs(self.content, self.get_subtitle())
        else:
            raise AttributeError(
                f"expected 'Voice' or 'Subs', was {self.translate}")
