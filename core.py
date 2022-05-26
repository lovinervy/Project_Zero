from database import DB
from Translator import translator
from pytube import YouTube

def get_subs_from_youtube(url, language) -> str:
    '''
    returns the path to the saved file
    Saved file has srt format
    '''
    lngs = translator.PRIORITY_TRANSLATE[language]
    source, subs = translator.get_subs(url, lngs)
    if source != language:
        subs = translator.translate(subs, source, language)
    f = translator.save_subs(subs)
    return f


class Control_DB(DB):
    def __init__(self) -> None:
        DB.__init__(self)
    
    def valid_url(self, url: str) -> bool:
        try:
            YouTube(url)
            return True
        except:
            return False

    def check_url(self, url: str) -> int:
        '''
        if url is in database then returns youtube_id
        else adds to database and returns youtube_id
        '''
        youtube_id = self.get_youtube_id(url)
        if youtube_id:
            return youtube_id
        return self._add_youtube(url)

    def have_translate(self, url: str, language: str) -> None | tuple:
        translates = self.select_translates(self.check_url(url))
        for translate in translates:
            if language == translate[2]:
                return translate
        return None
        
    def have_translate_subs(self, url: str, language: str) -> None | tuple:
        translate = self.have_translate(url, language)
        if translate:
            return self.select_subtitles(translate[0])
        return None

    def have_translate_voice(self, url: str, language: str) -> None | tuple:
        translate = self.have_translate(url, language)
        if translate:
            return self.select_voiceovers(translate[0])
        return None

    def have_video(self, url: str) -> None | tuple:
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
        '''
        adds url to database
        '''
        youtube_id = self.insert_youtube(url)
        return youtube_id
    
