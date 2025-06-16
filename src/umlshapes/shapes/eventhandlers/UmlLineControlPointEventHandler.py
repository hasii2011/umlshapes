
from logging import Logger
from logging import getLogger

from wx.lib.ogl import ShapeEvtHandler

from umlshapes.UmlUtils import UmlUtils
from umlshapes.frames.DiagramFrame import DiagramFrame
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType

from umlshapes.types.Common import Rectangle
from umlshapes.types.UmlPosition import UmlPosition


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
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.shapes.UmlClass import UmlClass

        umlLineControlPoint:     UmlLineControlPoint     = self.GetShape()
        umlLineControlPointType: UmlLineControlPointType = umlLineControlPoint.umlLineControlPointType

        if umlLineControlPointType == UmlLineControlPointType.FROM_ENDPOINT:
            self.logger.debug(f'{umlLineControlPoint=} x,y: ({x},{y})')

            umlLink:    UmlLink   = umlLineControlPoint.attachedTo
            umlClass:   UmlClass  = umlLink.GetFrom()
            rectangle:  Rectangle = umlClass.rectangle

            self.logger.debug(f'{umlLink=} {umlClass=}')

            borderPosition: UmlPosition = UmlUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=rectangle)

            ends = umlLink.GetEnds()
            toX = ends[2]
            toY = ends[3]

            self.logger.info(f'{borderPosition=}')
            umlLink.SetEnds(x1=borderPosition.x, y1=borderPosition.y, x2=toX, y2=toY)
            umlLineControlPoint.SetX(borderPosition.x)
            umlLineControlPoint.SetY(borderPosition.y)

        elif umlLineControlPointType == UmlLineControlPointType.TO_ENDPOINT:
            pass
        else:
            super().OnDragLeft(draw, x, y, keys, attachment)

        canvas: DiagramFrame = umlLineControlPoint.GetCanvas()
        canvas.refresh()
