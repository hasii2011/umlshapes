
from logging import Logger
from logging import getLogger

from wx.lib.ogl import ShapeEvtHandler

from umlshapes.frames.DiagramFrame import DiagramFrame
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType


class UmlLineControlPointEventHandler(ShapeEvtHandler):
    """
    Nothing special here;  Just some syntactic sugar and a canvas refresh
    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__()

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        The drag left handler.  This appears to be the only event handler
        invoked regardless of which direction you are dragging

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """

        umlLineControlPoint:     UmlLineControlPoint     = self.GetShape()
        umlLineControlPointType: UmlLineControlPointType = umlLineControlPoint.umlLineControlPointType

        if umlLineControlPointType == UmlLineControlPointType.FROM_ENDPOINT or umlLineControlPointType == UmlLineControlPointType.TO_ENDPOINT:
            self.logger.info(f'{umlLineControlPoint=} x,y: ({x},{y})')

        else:
            super().OnDragLeft(draw, x, y, keys, attachment)

        canvas: DiagramFrame = umlLineControlPoint.GetCanvas()
        canvas.refresh()
