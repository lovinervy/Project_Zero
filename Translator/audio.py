from pydub import AudioSegment, effects
from Translator.voice_v2 import retell_quickly_in_russia

def _speedup(audiopath: str, text: str):
    """
    Для ускорение аудиодорожки если не успевает в заданный лимит
    
    audiopath   - путь до исходной аудиодорожки
    text        - слова которые произносятся в этой дорожке  
    """
    retell_quickly_in_russia(audiopath, text)
    voice = AudioSegment.from_file(audiopath)
    return voice


def mix_translate_audio_with_original(language: str, sub: dict, song_path: str, output: str = 'output.mp4a'):
    """
    Смешивает переведенные фразы с оригинальной дорожкой

    sub словарь, где ключ это название сохраненного файла в temp, а значение это
    словарь с текстом, момент произношения фразы и продолжительность озвучинваия  
    """
    main_song = AudioSegment.from_file(song_path)

    for k, v in sub.items():
        start = v['start'] * 1000
        voice = AudioSegment.from_file(v['path'])
        if len(voice) > (v['end'] - v['start']) * 1000 + 100:
            with open('debug.txt', 'a') as f:
                f.write(f"{k} Len voice:{len(voice)}, Need len: {(v['end'] - v['start']) * 1000}\n")
            if language == 'русский':
                voice = _speedup(v['path'], v['text'])
            else:
                pass
        main_song = main_song.overlay(voice, position=start, gain_during_overlay=-10)
    t = main_song.export(out_f=output, format='mp3')
