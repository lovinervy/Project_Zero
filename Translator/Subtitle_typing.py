from dataclasses import dataclass
from typing import List, NamedTuple


@dataclass
class Subtitle_block:
    """"start" and "end" objects in milliseconds"""
    start   : int
    end     : int
    text    : str



