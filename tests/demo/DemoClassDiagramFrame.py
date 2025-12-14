
from logging import Logger
from logging import getLogger

from wx import Brush
from wx import Colour
from wx import DC
from wx import PENSTYLE_LONG_DASH

from wx import PaintEvent
from wx import Pen
from wx import PenInfo
from wx import PenStyle
from wx import RED
from wx import Window

from umlshapes.frames.UmlFrame import Ltrb
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

RIGHT_MARGIN:  int = 5
LEFT_MARGIN:   int = 5
TOP_MARGIN:    int = 5
BOTTOM_MARGIN: int = 5


class DemoClassDiagramFrame(ClassDiagramFrame):

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
        """

        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)
        self.demoLogger: Logger = getLogger(__name__)

        self._drawShapeBoundary: bool = False

    @property
    def drawShapeBoundary(self):
        return self._drawShapeBoundary

    @drawShapeBoundary.setter
    def drawShapeBoundary(self, drawShapeBoundary: bool):
        self._drawShapeBoundary = drawShapeBoundary

    def OnPaint(self, event: PaintEvent):
        """
        Override so I have a place to draw the shape boundaries

        Args:
            event:
        """
        from wx import PaintDC

        dc = PaintDC(self)
        w, h = self.GetSize()
        mem: DC = self._createDC(w, h)
        mem.SetBackground(Brush(self.GetBackgroundColour()))
        mem.Clear()

        x, y = self.CalcUnscrolledPosition(0, 0)

        if self._umlPreferences.backGroundGridEnabled is True:
            self._drawGrid(memDC=mem, width=w, height=h, startX=x, startY=y)
        self.Redraw(mem)

        if self.drawShapeBoundary is True:

            mem.SetPen(self._getBoundaryPen())
            boundary: Ltrb = self.shapeBoundaries

            self.demoLogger.info(f'{boundary=}')
            self._drawTopBoundary(mem=mem, boundary=boundary)
            self._drawBottomBoundary(mem=mem, boundary=boundary)
            self._drawRightBoundary(mem=mem, boundary=boundary)
            self._drawLeftBoundary(mem=mem, boundary=boundary)

        dc.Blit(0, 0, w, h, mem, x, y)

    def _drawTopBoundary(self, mem: DC, boundary: Ltrb):

        mem.DrawLine(x1=boundary.left - LEFT_MARGIN,
                     y1=boundary.top - TOP_MARGIN,
                     x2=boundary.right + RIGHT_MARGIN,
                     y2=boundary.top - TOP_MARGIN
                     )

    def _drawBottomBoundary(self, mem: DC, boundary: Ltrb):

        mem.DrawLine(x1=boundary.left - LEFT_MARGIN,
                     y1=boundary.bottom + BOTTOM_MARGIN,
                     x2=boundary.right + RIGHT_MARGIN,
                     y2=boundary.bottom + BOTTOM_MARGIN
                     )

    def _drawLeftBoundary(self, mem: DC, boundary: Ltrb):

        mem.DrawLine(x1=boundary.left - LEFT_MARGIN,
                     y1=boundary.top - TOP_MARGIN,
                     x2=boundary.left - LEFT_MARGIN,
                     y2=boundary.bottom + BOTTOM_MARGIN
                     )

    def _drawRightBoundary(self, mem: DC, boundary: Ltrb):

        mem.DrawLine(x1=boundary.right + RIGHT_MARGIN,
                     y1=boundary.top - TOP_MARGIN,
                     x2=boundary.right + RIGHT_MARGIN,
                     y2=boundary.bottom + BOTTOM_MARGIN
                     )

    def _getBoundaryPen(self) -> Pen:

        lineColor: Colour   = RED
        lineStyle: PenStyle = PENSTYLE_LONG_DASH
        pen:       Pen      = Pen(PenInfo(lineColor).Style(lineStyle).Width(1))

        return pen
