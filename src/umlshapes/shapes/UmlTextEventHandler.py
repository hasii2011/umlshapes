
from typing import NewType
from typing import List

from logging import Logger
from logging import getLogger

from wx import ClientDC

from wx import DC
from wx import PENSTYLE_SOLID

from wx import Colour
from wx import Pen

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

ShapeList = NewType('ShapeList', List[Shape])


class UmlTextEventHandler(ShapeEvtHandler):

    def __init__(self, moveColor: Colour):

        self.logger: Logger = getLogger(__name__)
        super().__init__(self)

        self._moveColor: Colour = moveColor
        self._outlinePen: Pen    = Pen(colour=self._moveColor, width=2, style=PENSTYLE_SOLID)

    def OnHighlight(self, dc: DC):
        super().OnHighlight(dc)

    def OnDragRight(self, draw, x, y, keys=0, attachment=0):
        super().OnDragRight(draw=draw, x=x, y=y, attachment=attachment)

        self.logger.info(f'{draw=}')

    def OnRightClick(self, *doNotCare):
        self.logger.info(f'{self.GetShape()}')

    def OnDrawOutline(self, dc: ClientDC, x: float, y: float, w: int, h: int):
        """
        Called when shape is moving
        Args:
            dc:  This is a client DC; It won't draw on OS X
            x:
            y:
            w:
            h:
        """
        self.logger.debug(f'Position: ({x},{y}) Size: ({w},{h})')

        shape: Shape  = self.GetShape()
        shape.SetX(x)
        shape.SetY(y)

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):

        shape:  Shape       = self.GetShape()
        canvas: ShapeCanvas = shape.GetCanvas()
        dc:     ClientDC    = ClientDC(canvas)

        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            canvas.Refresh(False)
        else:
            shapeList:  ShapeList = canvas.GetDiagram().GetShapeList()
            toUnselect: ShapeList = ShapeList([])

            for s in shapeList:
                if s.Selected() is True:
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if len(toUnselect) > 0:
                for s in toUnselect:
                    s.Select(False, dc)

                # #canvas.Redraw(dc)
                canvas.Refresh(False)
