
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from enum import Enum

from wx import Point
from wx import WHITE_BRUSH

from wx.lib.ogl import CONTROL_POINT_ENDPOINT_FROM
from wx.lib.ogl import CONTROL_POINT_ENDPOINT_TO
from wx.lib.ogl import CONTROL_POINT_LINE

from wx.lib.ogl import LineControlPoint

from umlshapes.UmlUtils import UmlUtils

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink


class UmlLineControlPointType(Enum):

    FROM_ENDPOINT = 'EndPoint From'
    TO_ENDPOINT   = 'EndPoint To'
    LINE_POINT    = 'Line Point'

    # noinspection PyTypeChecker
    @classmethod
    def toWxType(cls, umlLineControlPointType: 'UmlLineControlPointType') -> int:

        if umlLineControlPointType == UmlLineControlPointType.FROM_ENDPOINT:
            return CONTROL_POINT_ENDPOINT_FROM
        elif umlLineControlPointType == UmlLineControlPointType.TO_ENDPOINT:
            return CONTROL_POINT_ENDPOINT_TO
        elif umlLineControlPointType == UmlLineControlPointType.LINE_POINT:
            return CONTROL_POINT_LINE
        else:
            assert False, 'Unknown line control type'


class UmlLineControlPoint(LineControlPoint):

    def __init__(self, umlFrame: UmlFrame, umlLink: 'UmlLink', controlPointType: UmlLineControlPointType, size: int, x: int = 0, y: int = 0):
        """

        Args:
            umlFrame:           Which frame it is on
            umlLink:            The associated link
            controlPointType:   The type of line control point
            size:               Size; The control is square
            x:                  x position
            y:                  y position
        """

        self.logger: Logger = getLogger(__name__)

        self._lineControlPointType: UmlLineControlPointType = controlPointType
        self._attachedTo:           TopLeftMixin            = cast(TopLeftMixin, None)

        super().__init__(
            theCanvas=umlFrame,
            object=umlLink,
            size=size,
            x=x,
            y=y,
            the_type=UmlLineControlPointType.toWxType(controlPointType)
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
        return self._lineControlPointType

    @property
    def attachedTo(self) -> 'UmlLink':
        return self._shape

    @property
    def position(self) -> UmlPosition:
        return UmlPosition(x=self.GetX(), y=self.GetY())

    @position.setter
    def position(self, position: UmlPosition):
        self.SetX(position.x)
        self.SetY(position.y)

    def __repr__(self) -> str:
        return f'UmlLineControlPoint type=`{self.umlLineControlPointType.value}` {self.point}'

    def __str__(self) -> str:
        return self.__repr__()
