
from typing import List
from typing import NewType
from typing import Union
from typing import cast

from dataclasses import dataclass

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutText import PyutText
from pyutmodelv2.PyutUseCase import PyutUseCase

from wx.lib.ogl import Shape

ModelObject = Union[PyutText, PyutNote, PyutActor, PyutClass, PyutUseCase, None]


NOT_SET_INT:     int   = cast(int, None)

UML_CONTROL_POINT_SIZE: int = 4         # Make this a preference


@dataclass
class LeftCoordinate:
    x: int = 0
    y: int = 0


UmlShapes = NewType('UmlShapes', List[Shape])
