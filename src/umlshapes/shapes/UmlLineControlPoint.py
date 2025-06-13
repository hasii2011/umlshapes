
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import Point
from wx import WHITE_BRUSH

from wx.lib.ogl import LineControlPoint

from umlshapes.UmlUtils import UmlUtils

from umlshapes.frames.UmlFrame import UmlFrame

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink


class UmlLineControlPoint(LineControlPoint):

    def __init__(self, umlFrame: UmlFrame, umlLink: 'UmlLink', size: int, x: int = 0, y: int = 0, controlPointType: int = 0):

        self.logger: Logger = getLogger(__name__)
        super().__init__(
            theCanvas=umlFrame,
            object=umlLink,
            size=size,
            x=x,
            y=y,
            the_type=controlPointType
        )

        self.SetDraggable(drag=True)
        # Override parent class
        self.SetPen(UmlUtils.redSolidPen())
        self.SetBrush(WHITE_BRUSH)

    @property
    def point(self) -> Point:
        return self._point

    def __repr__(self) -> str:
        return f'UmlLineControlPoint {self.point}'

    def __str__(self) -> str:
        return self.__repr__()
