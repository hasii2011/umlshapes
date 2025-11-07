
from typing import Union
from typing import cast

from enum import Enum

from dataclasses import dataclass

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutText import PyutText
from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.types.UmlPosition import UmlPosition

ModelObject = Union[PyutText, PyutNote, PyutActor, PyutClass, PyutUseCase, PyutLink, PyutInterface]


NOT_SET_INT: int = cast(int, None)
TAB:         str = '\t'


class AttachmentSide(Enum):
    """
    Cardinal points, taken to correspond to the attachment points of any shape
    in a Cartesian coordinate system.

    """
    LEFT   = 'Left'
    TOP    = 'Top'
    RIGHT  = 'Right'
    BOTTOM = 'Bottom'
    NONE   = 'None'

    def __str__(self):
        return str(self.name)

    @classmethod
    def toEnum(cls, strValue: str) -> 'AttachmentSide':
        """
        Converts the input string to the attachment location
        Args:
            strValue:   A serialized string value

        Returns:  The attachment side enumeration
        """
        canonicalStr: str = strValue.strip(' ')

        if canonicalStr == 'Left':
            return AttachmentSide.LEFT
        elif canonicalStr == 'Top':
            return AttachmentSide.TOP
        elif canonicalStr == 'Right':
            return AttachmentSide.RIGHT
        elif canonicalStr == 'Bottom':
            return AttachmentSide.BOTTOM
        else:
            print(f'Warning: did not recognize this attachment point: {canonicalStr}')
            return AttachmentSide.TOP


@dataclass
class LollipopCoordinates:
    startCoordinates:   UmlPosition
    endCoordinates:     UmlPosition
    lollipopLineLength: int = 0       # excluding the circle


@dataclass
class Rectangle:
    """
    A traditional description of a graphical rectangle
    """
    left:   int = 0
    top:    int = 0
    right:  int = 0
    bottom: int = 0


@dataclass
class EndPoints:
    fromPosition: UmlPosition
    toPosition:   UmlPosition


@dataclass
class LeftCoordinate:
    x: int = 0
    y: int = 0


NAME_IDX:                    int = 0
SOURCE_CARDINALITY_IDX:      int = 1
DESTINATION_CARDINALITY_IDX: int = 2
