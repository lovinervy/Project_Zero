from pydub import AudioSegment, effects


def _speedup(need_len: int, audio: AudioSegment):
    """
    Для ускорение аудиодорожки если не успевает в заданный лимит
    
    need_len - продолжительность на которую надо уложиться в миллисекундах
    audio - исходная аудиодорожка 
    """
    cur = len(audio)
    need_speed = cur / need_len
    if need_speed > 1.75: need_speed = 1.75
    s = effects.speedup(audio, playback_speed=need_speed)
    return s


def mix_translate_audio_with_original(sub: dict, song_path: str, output: str = 'output.mp4a'):
    """
    Смешивает переведенные фразы с оригинальной дорожкой

    sub словарь, где ключ это название сохраненного файла в temp, а значение это
    словарь с текстом, момент произношения фразы и продолжительность озвучинваия  
    """
    main_song = AudioSegment.from_file(song_path)

    for _, v in sub.items():
        start = v['start'] * 1000
        with open('debug.txt', 'a') as f:
            f.write(f'{start} - {v}\n')
        voice = AudioSegment.from_file(v['path'])
        # if len(voice) > v['dur']:
        #     voice = _speedup(v['dur'], voice)
        main_song = main_song.overlay(voice, position=start, gain_during_overlay=-10)
    t = main_song.export(out_f=output, format='mp3')
