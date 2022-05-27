import datetime

import time
import re
from html import unescape
from pytube import YouTube
import xml.etree.ElementTree as ElementTree

class Subs:
    def __init__(self, url: str) -> None:

        self.yt: classmethod = YouTube(url)
        try:
            self.yt.streams
        except:
            self.yt.streams
        self.subs: str = ''

    def _get_subs(self, lang: str = 'ru') -> dict:
        caption: dict = self.yt.captions[lang]
        return caption.xml_captions

    def get_support_languages(self) -> list:
        lang: dict[classmethod] = self.yt.captions
        return lang

    def set_lang(self, lang: str) -> None:
        if lang in self.get_support_languages():
            # XML document
            self.subs: str = self._get_subs(lang=lang)
        else:
            raise BaseException('Invalid lang key', lang)

    @staticmethod
    def _ms_to_srt_time(t: int) -> str:
        sec: int = t // 1000
        ms: int = t % 1000
        time_fmt = time.strftime('%H:%M:%S', time.gmtime(sec))
        return f'{time_fmt},{ms}'

    def xml_to_srt(self) -> str:
        tree = ElementTree.fromstring(self.subs)
        root = tree.find('body')

        segments = []
        for i, line in enumerate(list(root)):
            text = line.text or ''
            caption = unescape(re.sub(r'\s+', ' ' ,text.replace('\n', ' ')))
            try:
                duration = int(line.attrib['d'])
            except:
                duration = 0
            start_time_ms = int(line.attrib['t'])
            end_time_ms = start_time_ms + duration
            sequence_number = i + 1
            sub_line = '{seq}\n{start} --> {end}\n{text}\n'.format(
                seq = sequence_number,
                start = self._ms_to_srt_time(start_time_ms),
                end = self._ms_to_srt_time(end_time_ms),
                text = caption
            )
            segments.append(sub_line)
        return '\n'.join(segments).strip()

    @staticmethod
    def get_duration(line) -> int:
        try:
            dur = int(line.attrib['d'])
        except:
            dur = 0
        return dur

    def xml_to_dict(self) -> dict:
        tree = ElementTree.fromstring(self.subs)
        root = tree.find('body')

        segments = {}
        count = 0
        for line in list(root):
            text = line.text or ''
            duration = self.get_duration(line)
            start_time_ms = int(line.attrib['t'])
            if not text and list(line) != []:
                text = ''
                line = list(line)
                for subline in line:
                    text += subline.text

            caption = unescape(re.sub(r'\s+', ' ' ,text.replace('\n', ' ')))
            if re.sub(r'\s+', '', caption) and caption != '[Music]':
                segments[str(count)] = {
                    'start': start_time_ms,
                    'dur': duration,
                    'end': start_time_ms + duration,
                    'text': caption
                }
                count += 1
            elif int(count) > 0 and segments.get(int(count)-1, {'dur' : 0})['dur'] > duration:
                    segments[int(count)-1]['dur'] += duration
        return segments

    @staticmethod
    def dublicate(text: str) -> str:
        text = text.split(' ')
        new_text = []
        for i in range(len(text) - 1):
            if text[i] == text[i+1]:
                continue
            else:
                new_text.append(text[i])
        new_text.append(text[-1])
        text = ' '.join(new_text)
        return text

    def get_subs_with_filter(self) -> dict:
        caption = self.xml_to_dict()
        counter = 0
        segments = {}
        tmp = caption.pop(str(counter))
        segments[str(counter)] = tmp

        for i in caption.keys():
            end = segments[str(counter)]['end']
            if caption[i]['start'] - end < 120 and \
                segments[str(counter)]['text'][-1] not in ('.', '-', '!', '?'):
                text = caption[i]['text']
                segments[str(counter)]['text'] += f' {text}'
                segments[str(counter)]['dur'] += caption[i]['dur'] 
                segments[str(counter)]['end'] = caption[i]['end']
            else:
                counter += 1
                segments[str(counter)] = caption.get(i)
        return segments


def dict_to_srt(caption: dict):
    def int_to_srt_time_format(d: int) -> str:
        """Convert decimal durations into proper srt format.

        :rtype: str
        :returns:
            SubRip Subtitle (str) formatted time duration.

        float_to_srt_time_format(3890) -> '00:00:03,890'
        """
        fraction, whole = d % 1000, d // 1000
        time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
        # ms = f"{fraction:.3f}".replace("0.", "")
        return time_fmt + str(fraction)

    segments = []
    for i in caption.keys():
        start = caption[i]['start']
        stop = caption[i]['end']

        start = int_to_srt_time_format(start)
        stop = int_to_srt_time_format(stop)
        
        text = caption[i]['text']
        srt = f'{int(i)+1}\n{start} --> {stop}\n{text}\n'
        segments.append(srt)
    return '\n'.join(segments).strip()


def srt_to_dict(srt: str) -> dict:
    def time_sec(time: str) -> float:
        time = time.replace(',', '.').split(':')
        time = datetime.timedelta(
            hours=float(time[0]),
            minutes=float(time[1]),
            seconds=float(time[2])
            )
        return time.total_seconds()


    data = {}

    caption = srt.split('\n')

    counter = 1
    i = 0
    while i < len(caption):
        if str(counter) == caption[i]:
            times = caption[i + 1].split(' --> ')
            data[counter] = {}
            data[counter] = {
                'start': time_sec(times[0]),
                'dur': time_sec(times[1]) - time_sec(times[0]),
                'end': time_sec(times[1]),
                'text': caption[i + 2]
            }
            i += 2
            counter += 1
        i += 1
    return data
