import datetime
import time
import re
from html import unescape
from typing import List
import xml.etree.ElementTree as ElementTree

from pytube import YouTube, Caption

from Translator.custom_typing import SubtitleBlock


class Subs:
    def __init__(self, url: str) -> None:
        self.yt: YouTube = YouTube(url)
        try:
            self.yt.streams
        except:
            self.yt.streams
        self.subs: str = ''

    def _get_subs(self, lang: str = 'ru') -> str:
        """Get XML format caption"""
        caption: Caption = self.yt.captions[lang]
        return caption.xml_captions

    def get_support_languages(self) -> dict[Caption]:
        lang: dict[Caption] = self.yt.captions
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
            caption = unescape(re.sub(r'\s+', ' ', text.replace('\n', ' ')))
            try:
                duration = int(line.attrib['d'])
            except:
                duration = 0
            start_time_ms = int(line.attrib['t'])
            end_time_ms = start_time_ms + duration
            sequence_number = i + 1
            sub_line = '{seq}\n{start} --> {end}\n{text}\n'.format(
                seq=sequence_number,
                start=self._ms_to_srt_time(start_time_ms),
                end=self._ms_to_srt_time(end_time_ms),
                text=caption
            )
            segments.append(sub_line)
        return '\n'.join(segments).strip()

    @staticmethod
    def get_duration(line) -> int:
        try:
            return int(line.attrib['d'])
        except:
            return 0

    def xml_to_list(self) -> List[SubtitleBlock]:
        tree: ElementTree.Element = ElementTree.fromstring(self.subs)
        root = tree.find('body')
        subtitle: List[SubtitleBlock] = []
        for line in list(root):
            text = line.text or ''
            duration = self.get_duration(line)
            start_time_ms = int(line.attrib['t'])
            if not text and list(line) != []:
                text = ''
                line = list(line)
                for sub_line in line:
                    text += sub_line.text

            caption = unescape(re.sub(r'\s+', ' ', text.replace('\n', ' ')))
            if re.sub(r'\s+', '', caption) and caption != '[Music]':
                block = SubtitleBlock(
                    start=start_time_ms,
                    end=start_time_ms + duration,
                    text=caption
                )
                subtitle.append(block)
        return subtitle

    @staticmethod
    def dublicate(text: str) -> str:
        text = text.split(' ')
        new_text = []
        for i in range(len(text) - 1):
            if text[i] == text[i + 1]:
                continue
            else:
                new_text.append(text[i])
        new_text.append(text[-1])
        text = ' '.join(new_text)
        return text

    def format_subtitle(self) -> List[SubtitleBlock]:
        subtitle: List[SubtitleBlock] = self.xml_to_list()
        counter = 0
        segments: List[SubtitleBlock] = []
        tmp = subtitle.pop(counter)
        segments.append(tmp)
        for i in range(len(subtitle)):
            end = subtitle[i].end
            if subtitle[i].start - end < 120 and \
                    segments[counter].text[-1] not in ('.', '-', '!', '?'):
                segments[counter].text += ' ' + subtitle[i].text
                segments[counter].end = subtitle[i].end
            else:
                counter += 1
                segments.append(subtitle[i])
        return segments


def list_to_srt(subtitle: List[SubtitleBlock]):
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

    segments: List[str] = []
    for i, block in enumerate(subtitle):
        start = int_to_srt_time_format(block.start)
        stop = int_to_srt_time_format(block.end)
        text = block.text
        srt = f'{int(i) + 1}\n{start} --> {stop}\n{text}\n'
        segments.append(srt)
    return '\n'.join(segments).strip()


def srt_to_list(srt: str) -> list[SubtitleBlock]:
    def time_ms(srt_time: str) -> int:
        srt_time = srt_time.replace(',', '.').split(':')
        time_delta = datetime.timedelta(
            hours=float(srt_time[0]),
            minutes=float(srt_time[1]),
            seconds=float(srt_time[2])
        )
        return int((time_delta.total_seconds() * 1000) // 1)

    subtitle: List[SubtitleBlock] = []

    caption = srt.split('\n')

    counter = 1
    i = 0
    while i < len(caption):
        if str(counter) == caption[i]:
            times = caption[i + 1].split(' --> ')
            subtitle.append(
                SubtitleBlock(
                    start=time_ms(times[0]),
                    end=time_ms(times[1]),
                    text=caption[i + 2]
                )
            )
            i += 2
            counter += 1
        i += 1
    return subtitle
