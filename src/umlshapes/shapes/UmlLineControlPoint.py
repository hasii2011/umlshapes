
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import WHITE_BRUSH

from wx.lib.ogl import LineControlPoint

from wx.lib.ogl import ShapeCanvas

from umlshapes.UmlUtils import UmlUtils
if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink


class UmlLineControlPoint(LineControlPoint):

    def __init__(self, canvas: ShapeCanvas, shape: 'UmlLink', size: int, x: int = 0, y: int = 0, controlPointType: int = 0):

        # canvas: ShapeCanvas, shape: Shape, size: int, xOffSet: float, yOffSet: float, controlPointType: int

        self.logger: Logger = getLogger(__name__)
        super().__init__(
            theCanvas=canvas,
            object=shape,
            size=size,
            x=x,
            y=y,
            the_type=controlPointType
        )

        self.SetDraggable(drag=True)
        # Override parent class
        self.SetPen(UmlUtils.redSolidPen())
        self.SetBrush(WHITE_BRUSH)
