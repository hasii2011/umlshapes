
from logging import Logger
from logging import getLogger

from wx.lib.ogl import RectangleShape
from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas

from umlshapes.UmlUtils import UmlUtils


class UmlControlPoint(RectangleShape):

    """The :class:`wx.ControlPoint` class."""
    def __init__(self, canvas: ShapeCanvas, shape: Shape, size: int, xOffSet: float, yOffSet: float, controlPointType: int):
        """

        Args:
            canvas:      An instance of wx.lib.ogl.Canvas
            shape:       An instance of  wx.lib.ogl.Shape`
            size:           The control point size;  Single number since it is a square
            xOffSet:    The x position
            yOffSet:    The y position
            controlPointType:       One of the following values

         ======================================== ==================================
         Control point type                       Description
         ======================================== ==================================
         `CONTROL_POINT_VERTICAL`                 Vertical
         `CONTROL_POINT_HORIZONTAL`               Horizontal
         `CONTROL_POINT_DIAGONAL`                 Diagonal
         ======================================== ==================================

        """
        super().__init__(w=size, h=size)

        self.logger: Logger = getLogger(__name__)

        self._canvas:  ShapeCanvas = canvas
        self._shape:   Shape       = shape
        self._xOffSet: float = xOffSet
        self._yOffSet: float = yOffSet
        self._type:    int   = controlPointType      # old name to keep compatibility with Shape

        self.SetPen(UmlUtils.redSolidPen())

        self._oldCursor = None
        self._visible:     bool = True
        self._eraseObject: bool = True

    def OnDraw(self, dc):
        """The draw handler."""
        self._xpos = self._shape.GetX() + self._xOffSet
        self._ypos = self._shape.GetY() + self._yOffSet
        RectangleShape.OnDraw(self, dc)

    def OnErase(self, dc):
        """The erase handler."""
        RectangleShape.OnErase(self, dc)

    # Implement resizing of canvas object
    def OnDragLeft(self, draw, x, y, keys=0, attachment=0):
        """The drag left handler."""
        self._shape.GetEventHandler().OnSizingDragLeft(self, draw, x, y, keys, attachment)

    def OnBeginDragLeft(self, x, y, keys=0, attachment=0):
        """The begin drag left handler."""
        self._shape.GetEventHandler().OnSizingBeginDragLeft(self, x, y, keys, attachment)

    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        """The end drag left handler."""
        self._shape.GetEventHandler().OnSizingEndDragLeft(self, x, y, keys, attachment)

    def OnSizingBeginDragLeft(self, pt, x, y, keys=0, attachment=0):

        super().OnSizingBeginDragLeft(pt, x, y, keys, attachment)
        self.logger.info(f'New position: ({x},{y})')

    def GetNumberOfAttachments(self):
        """Get the number of attachments."""
        return 1

    def GetAttachmentPosition(self, attachment, nth=0, no_arcs=1, line=None):
        """

        Args:
            attachment: the attachment ???
            nth:        get nth attachment ???
            no_arcs:
            line:

        Returns:

        """
        return self._xpos, self._ypos

    def SetEraseObject(self, er):
        """
        Set the erase object ???

        Args:
            er:
        """
        self._eraseObject = er
