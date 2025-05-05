
from logging import Logger
from logging import getLogger

from wx import WHITE_BRUSH

from wx.lib.ogl import ControlPoint
from wx.lib.ogl import Shape

from umlshapes.UmlUtils import UmlUtils
from umlshapes.frames.UmlFrame import UmlFrame


class UmlControlPoint(ControlPoint):
    """
    Subclassed, So I can
        * Change the control point color and size
        * Implement resizing of its parent.
    """
    def __init__(self, umlFrame: UmlFrame, shape: Shape, size: int, xOffSet: float, yOffSet: float, controlPointType: int):
        """

        Args:
            umlFrame:           An instance of wx.lib.ogl.Canvas
            shape:              An instance of wx.lib.ogl.Shape
            size:               The control point size;  Single number since it is a square
            xOffSet:            The x position
            yOffSet:            The y position
            controlPointType:       One of the following values

         ======================================== ==================================
         Control point type                       Description
         ======================================== ==================================
         `CONTROL_POINT_VERTICAL`                 Vertical
         `CONTROL_POINT_HORIZONTAL`               Horizontal
         `CONTROL_POINT_DIAGONAL`                 Diagonal
         ======================================== ==================================

        """
        super().__init__(theCanvas=umlFrame, object=shape, size=size, the_xoffset=xOffSet, the_yoffset=yOffSet, the_type=controlPointType)
        self.logger: Logger = getLogger(__name__)

        # Override parent class
        self.SetPen(UmlUtils.redSolidPen())
        self.SetBrush(WHITE_BRUSH)
