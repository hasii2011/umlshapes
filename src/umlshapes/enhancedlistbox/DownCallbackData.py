
from dataclasses import dataclass

from umlshapes.enhancedlistbox.MoveCallbackData import MoveCallbackData


@dataclass
class DownCallbackData(MoveCallbackData):
    nextItem: str = ''
