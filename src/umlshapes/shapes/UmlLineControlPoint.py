
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger


from enum import Enum

from wx import Point
from wx import WHITE_BRUSH

from wx.lib.ogl import CONTROL_POINT_ENDPOINT_FROM
from wx.lib.ogl import CONTROL_POINT_ENDPOINT_TO

from wx.lib.ogl import LineControlPoint

from umlshapes.UmlUtils import UmlUtils

from umlshapes.frames.UmlFrame import UmlFrame

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink


class UmlLineControlPointType(Enum):

    FROM_ENDPOINT = 'EndPoint From'
    TO_ENDPOINT   = 'EndPoint To'
    LINE_POINT    = 'Line Point'


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

    @property
    def umlLineControlPointType(self) -> UmlLineControlPointType:
        """
        Syntactic sugar around some Ogl integer values

        CONTROL_POINT_ENDPOINT_TO = 4
        CONTROL_POINT_ENDPOINT_FROM = 5
        CONTROL_POINT_LINE = 6

        Returns:  An enumerated value

        """
        if self._type == CONTROL_POINT_ENDPOINT_TO:
            return UmlLineControlPointType.FROM_ENDPOINT
        elif self._type == CONTROL_POINT_ENDPOINT_FROM:
            return UmlLineControlPointType.TO_ENDPOINT
        else:
            return UmlLineControlPointType.LINE_POINT

    def __repr__(self) -> str:
        return f'UmlLineControlPoint type=`{self.umlLineControlPointType.value}` {self.point}'

    def __str__(self) -> str:
        return self.__repr__()
