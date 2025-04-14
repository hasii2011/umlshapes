
from typing import List
from typing import NewType
from typing import Tuple
from typing import cast

from dataclasses import dataclass

from umlshapes.types.Common import NOT_SET_INT
from umlshapes.types.UmlSize import UmlSize

DELIMITER: str = ','


@dataclass
class UmlRect(UmlSize):
    """
    Represents a Rectangle by location and size
    """
    left: int = NOT_SET_INT
    top:  int = NOT_SET_INT

    @classmethod
    def deSerialize(cls, value: str) -> 'UmlRect':

        values: List[str] = value.split(sep=DELIMITER)

        assert len(values) == 4, 'Incorrectly formatted `Rect` values'

        rect: UmlRect = UmlRect()
        rect.top    = int(values[0])
        rect.left   = int(values[1])
        rect.width  = int(values[2])
        rect.height = int(values[3])

        return rect

    def __str__(self):

        sizeStr: str = super().__str__()
        return f'{self.left}{DELIMITER}{self.top}{DELIMITER}{sizeStr}'

    def __repr__(self):
        return self.__str__()

    @classmethod
    def toTuple(cls, rect: 'UmlRect') -> Tuple[int, int, int, int]:
        return rect.left, rect.top, rect.width, rect.height


UmlRects = NewType('UmlRects', List[UmlRect])


NO_RECT: UmlRect = cast(UmlRect, None)
