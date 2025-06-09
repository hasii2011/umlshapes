
from logging import Logger
from logging import getLogger


from wx.lib.ogl import CONTROL_POINT_DIAGONAL
from wx.lib.ogl import CONTROL_POINT_HORIZONTAL
from wx.lib.ogl import CONTROL_POINT_VERTICAL

from wx.lib.ogl import CircleShape
from wx.lib.ogl import EllipseShape
from wx.lib.ogl import Shape

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlControlPoint import UmlControlPoint
from umlshapes.shapes.eventhandlers.UmlControlPointEventHandler import UmlControlPointEventHandler


class ControlPointMixin:
    """
    Use this mixin to get red control points that are slightly smaller
    than the default ogl control points
    """
    def __init__(self, shape: Shape):

        self.cpLogger:     Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        self._shape:       Shape          = shape

    def MakeControlPoints(self):
        from umlshapes.shapes.UmlActor import UmlActor

        """
        Make a list of control points (draggable handles) appropriate to
        the shape.
        """
        maxX, maxY = self._shape.GetBoundingBoxMax()
        minX, minY = self._shape.GetBoundingBoxMin()

        widthMin  = minX
        heightMin = minY

        # Offsets from the main object
        top:    int = -heightMin // 2
        bottom: int = heightMin // 2 + (maxY - minY)

        left:   int = -widthMin // 2
        right:  int = widthMin // 2 + (maxX - minX)

        canvas: UmlFrame = self._shape.GetCanvas()
        assert isinstance(canvas, UmlFrame), 'I only support this'

        umlControlPointSize: int = self._preferences.controlPointSize

        if isinstance(self._shape, CircleShape) is True or isinstance(self._shape, EllipseShape):
            self._makeOrthogonalControlPoints(canvas=canvas, top=top, right=right, bottom=bottom, left=left)
        elif isinstance(self._shape, UmlActor):
            self._makeDiagonalControlPoints(canvas=canvas, top=top, right=right, bottom=bottom, left=left)
        else:
            #
            # Bad implementation;  These have to be created in this exact order because of the Shape.ResetControlPoints() method
            #
            control: UmlControlPoint = UmlControlPoint(canvas, self._shape, umlControlPointSize, left, top, CONTROL_POINT_DIAGONAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, 0, top, CONTROL_POINT_VERTICAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, right, top, CONTROL_POINT_DIAGONAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, right, 0, CONTROL_POINT_HORIZONTAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, right, bottom, CONTROL_POINT_DIAGONAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, 0, bottom, CONTROL_POINT_VERTICAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, left, bottom, CONTROL_POINT_DIAGONAL)
            self._setupControlPoint(umlControlPoint=control)

            control = UmlControlPoint(canvas, self._shape, umlControlPointSize, left, 0, CONTROL_POINT_HORIZONTAL)
            self._setupControlPoint(umlControlPoint=control)

    def _makeOrthogonalControlPoints(self, canvas: UmlFrame, top: int, right: int, bottom: int, left: int):

        umlControlPointSize: int = self._preferences.controlPointSize

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, 0, top, CONTROL_POINT_VERTICAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, right, 0, CONTROL_POINT_HORIZONTAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, 0, bottom, CONTROL_POINT_VERTICAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, left, 0, CONTROL_POINT_HORIZONTAL)
        self._setupControlPoint(umlControlPoint=control)

    def _makeDiagonalControlPoints(self, canvas: UmlFrame, top: int, right: int, bottom: int, left: int):

        umlControlPointSize: int = self._preferences.controlPointSize

        control: UmlControlPoint = UmlControlPoint(canvas, self._shape, umlControlPointSize, left, top, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, right, top, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, right, bottom, CONTROL_POINT_DIAGONAL)
        self._setupControlPoint(umlControlPoint=control)

        control = UmlControlPoint(canvas, self._shape, umlControlPointSize, left, bottom, CONTROL_POINT_DIAGONAL)
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
