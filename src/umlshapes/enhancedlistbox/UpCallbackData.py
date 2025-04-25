
from dataclasses import dataclass

from umlshapes.enhancedlistbox.MoveCallbackData import MoveCallbackData


@dataclass
class UpCallbackData(MoveCallbackData):
    previousItem: str = ''
