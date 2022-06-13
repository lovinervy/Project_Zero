from dataclasses import dataclass
from typing import List, NamedTuple


@dataclass
class SubtitleBlock:
    """
    start: int ---> start show subtitle block in milliseconds\n
    end: int ---> end show subtitle block int milliseconds\n
    text: str ---> text to be displayed
    """
    start: int
    end: int
    text: str


@dataclass
class PathToFile:
    """
    video: str ---> path to video file in local disk\n
    audio: str ---> path to audio file in local disk
    """
    video: str
    audio: str


class AudioMessage(NamedTuple):
    """
    path_to_message: str ---> path to audio file in local disk\n
    subtitle_block: SubtitleBlock ---> class SubtitleBlock
    """
    path_to_message: str
    subtitle_block: SubtitleBlock
