
from logging import Logger
from logging import getLogger


from wx.lib.ogl import CONTROL_POINT_DIAGONAL
from wx.lib.ogl import CONTROL_POINT_HORIZONTAL
from wx.lib.ogl import CONTROL_POINT_VERTICAL
from wx.lib.ogl import Shape

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlControlPoint import UmlControlPoint
from umlshapes.shapes.UmlControlPointEventHandler import UmlControlPointEventHandler

CONTROL_POINT_SIZE: int = 4         # Make this a preference


class ControlPointMixin:
    """
    Use this mixin to get red control points that are slightly smaller
    than the default ogl control points
    """
    def __init__(self, shape: Shape):
        self.cpLogger: Logger = getLogger(__name__)

        self._shape:  Shape    = shape

    def MakeControlPoints(self):
        """
        Make a list of control points (draggable handles) appropriate to
        the shape.
        """
        maxX, maxY = self._shape.GetBoundingBoxMax()
        minX, minY = self._shape.GetBoundingBoxMin()

        widthMin = minX + CONTROL_POINT_SIZE + 2
        heightMin = minY + CONTROL_POINT_SIZE + 2

        # Offsets from main object
        top = -heightMin / 2.0
        bottom = heightMin / 2.0 + (maxY - minY)
        left = -widthMin / 2.0
        right = widthMin / 2.0 + (maxX - minX)

        canvas: UmlFrame = self._shape.GetCanvas()
        assert isinstance(canvas, UmlFrame), 'I only support this'

        control: UmlControlPoint = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, left, top, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, 0, top, CONTROL_POINT_VERTICAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, right, top, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, right, 0, CONTROL_POINT_HORIZONTAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, right, bottom, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, 0, bottom, CONTROL_POINT_VERTICAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, left, bottom, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, CONTROL_POINT_SIZE, left, 0, CONTROL_POINT_HORIZONTAL)
        self._setupControlPoint(umlControlPoint=control)

    def _setupControlPoint(self, umlControlPoint: UmlControlPoint):

        umlControlPoint.SetParent(self._shape)

        # This is dangerous if the returned type changes
        self._shape.GetChildren().append(umlControlPoint)
        self._shape.GetCanvas().AddShape(umlControlPoint)
        # This is dangerous, accessing internal stuff
        # noinspection PyProtectedMember
        self._shape._controlPoints.append(umlControlPoint)
        self._addEventHandler(umlControlPoint=umlControlPoint)

    def _addEventHandler(self, umlControlPoint: UmlControlPoint):

        eventHandler: UmlControlPointEventHandler = UmlControlPointEventHandler()
        eventHandler.SetShape(umlControlPoint)
        eventHandler.SetPreviousHandler(umlControlPoint.GetEventHandler())

        umlControlPoint.SetEventHandler(eventHandler)
