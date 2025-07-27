
from typing import NewType
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from enum import Enum

from wx import Point
from wx import VERTICAL
from wx import HORIZONTAL
from wx import SUNKEN_BORDER

# I know it is there
# noinspection PyUnresolvedReferences
from wx.core import PenStyle

from wx import MouseEvent
from wx import Bitmap
from wx import Brush
from wx import ClientDC
from wx import Colour
from wx import DC
from wx import MemoryDC
from wx import PaintDC
from wx import PaintEvent
from wx import Pen
from wx import PenInfo
from wx import SystemAppearance
from wx import SystemSettings

from wx import Window

from wx.lib.ogl import ShapeCanvas

from umlshapes.UmlUtils import UmlUtils
from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlPenStyle import UmlPenStyle

from umlshapes.preferences.UmlPreferences import UmlPreferences

if TYPE_CHECKING:
    from umlshapes.UmlDiagram import UmlDiagram

FrameId = NewType('FrameId', str)


class WheelAxis(Enum):
    WHEEL_AXIS_VERTICAL   = 0
    WHEEL_AXIS_HORIZONTAL = 1

    @classmethod
    def toEnum(cls, value: int) -> 'WheelAxis':

        if value == 0:
            return WheelAxis.WHEEL_AXIS_VERTICAL
        elif value == 1:
            return WheelAxis.WHEEL_AXIS_HORIZONTAL
        else:
            assert False, f'Unknown wheel axis: {value=}'


class DiagramFrame(ShapeCanvas):
    """
    A frame to draw UML diagrams.
    """
    def __init__(self, parent: Window):
        """

        Args:
            parent:  parent window
        """
        from umlshapes.UmlDiagram import UmlDiagram

        super().__init__(parent, style=SUNKEN_BORDER)

        self._dfLogger:       Logger         = getLogger(__name__)
        self._umlPreferences: UmlPreferences = UmlPreferences()

        umlDiagram: UmlDiagram = UmlDiagram(self)
        umlDiagram.SetSnapToGrid(True)

        self.SetDiagram(diag=umlDiagram)    # incestuous behavior here
        systemAppearance: SystemAppearance = SystemSettings.GetAppearance()
        self._darkMode:   bool             = systemAppearance.IsDark()

        self._dfLogger.debug(f'{self._darkMode=}')

        self._setAppropriateSetBackground()

        w, h = self.GetSize()
        self._workingBitmap: Bitmap = Bitmap(w, h)   # double buffering

        self._isInfinite: bool    = False    # Indicates if the frame is infinite
        # The ShapeCanvas ID is an integer;  use our own
        self._id: FrameId = FrameId(UmlUtils.getID())

    @property
    def umlDiagram(self) -> 'UmlDiagram':
        return self.GetDiagram()

    @umlDiagram.setter
    def umlDiagram(self, newDiagram: 'UmlDiagram'):
        self.SetDiagram(newDiagram)

    @property
    def id(self) -> FrameId:
        """
        UmlFrame ID

        Returns:  The UML generated Frame ID
        """
        return self._id

    def refresh(self, eraseBackground: bool = True):

        w, h = self.GetSize()

        dc: DC = self._createDC(w, h)

        # noinspection PySimplifyBooleanCheck
        if eraseBackground is True:
            self.Redraw(dc)
            client: ClientDC = ClientDC(self)

            x, y = self.CalcUnscrolledPosition(0, 0)
            client.Blit(0, 0, w, h, dc, x, y)

        else:
            self.RedrawWithBackground()

    def RedrawWithBackground(self):
        """
        Redraw the screen using the background.
        """
        self.Redraw(cast(DC, None))

    def setInfinite(self, infinite: bool = False):
        """
        Set this diagram frame as an infinite work area. The result is that the
        virtual size is enlarged when the scrollbar reaches the specified
        margins (see `SetMargins`). When we set this as `True`, the scrollbars
        are moved to the middle of their scale.

        Args:
            infinite:   If `True` the work area is infinite
        """
        self._isInfinite = infinite

        # noinspection PySimplifyBooleanCheck
        if infinite is True:
            # place all the shapes in an area centered on the infinite work area
            vWidth, vHeight = self.GetVirtualSize()
            cWidth, cHeight = self.GetClientSize()
            # get the number of pixels per scroll unit
            xUnit, yUnit = self.GetScrollPixelsPerUnit()

            # get the scroll units
            noUnitX = (vWidth-cWidth) // xUnit
            noUnitY = (vHeight-cHeight) // yUnit

            if self._umlPreferences.centerDiagram is True:
                self.Scroll(noUnitX // 2, noUnitY // 2)   # set the scrollbars position in the middle of their scale
            else:
                self.Scroll(0, 0)

    def OnPaint(self, event: PaintEvent):
        """
        Override the parent method because, when initially adding shapes
        to the diagram, they do not show up unless the canvas is moved.

        I copied this from the legacy pyut miniogl.

        Args:
            event:
        """
        dc = PaintDC(self)
        w, h = self.GetSize()
        mem = self._createDC(w, h)
        mem.SetBackground(Brush(self.GetBackgroundColour()))
        mem.Clear()

        x, y = self.CalcUnscrolledPosition(0, 0)

        if self._umlPreferences.backGroundGridEnabled is True:
            self._drawGrid(memDC=mem, width=w, height=h, startX=x, startY=y)
        self.Redraw(mem)

        dc.Blit(0, 0, w, h, mem, x, y)

    def OnMouseEvent(self, mouseEvent: MouseEvent):

        rotation:  int       = mouseEvent.GetWheelRotation()
        wheelAxis: WheelAxis = WheelAxis.toEnum(value=mouseEvent.GetWheelAxis())
        inverted:  bool      = mouseEvent.IsWheelInverted()

        if not inverted:
            rotation = -rotation

        self._dfLogger.debug(f'{wheelAxis} - {inverted=} - {rotation=}')

        yScrollPosition: int = self.GetScrollPos(VERTICAL)
        xScrollPosition: int = self.GetScrollPos(HORIZONTAL)

        if wheelAxis == WheelAxis.WHEEL_AXIS_VERTICAL:
            yScrollPosition += rotation
        else:
            xScrollPosition += rotation

        self.Scroll(Point(x=xScrollPosition, y=yScrollPosition))

        super().OnMouseEvent(evt=mouseEvent)

    def _drawGrid(self, memDC: DC, width: int, height: int, startX: int, startY: int):

        # self.clsLogger.info(f'{width=} {height=} {startX=} {startY=}')
        savePen = memDC.GetPen()

        newPen: Pen = self._getGridPen()
        memDC.SetPen(newPen)

        self._drawHorizontalLines(memDC=memDC, width=width, height=height, startX=startX, startY=startY)
        self._drawVerticalLines(memDC=memDC,   width=width, height=height, startX=startX, startY=startY)
        memDC.SetPen(savePen)

    def _drawHorizontalLines(self, memDC: DC, width: int, height: int, startX: int, startY: int):

        x1:   int = 0
        x2:   int = startX + width
        stop: int = height + startY
        step: int = self._umlPreferences.backgroundGridInterval
        for movingY in range(startY, stop, step):
            memDC.DrawLine(x1, movingY, x2, movingY)

    def _drawVerticalLines(self, memDC: DC, width: int, height: int, startX: int, startY: int):

        y1:   int = 0
        y2:   int = startY + height
        stop: int = width + startX
        step: int = self._umlPreferences.backgroundGridInterval

        for movingX in range(startX, stop, step):
            memDC.DrawLine(movingX, y1, movingX, y2)

    def _getGridPen(self) -> Pen:

        # noinspection PySimplifyBooleanCheck
        if self._darkMode is True:
            gridLineColor: Colour = UmlColor.toWxColor(self._umlPreferences.darkModeGridLineColor)
        else:
            gridLineColor = UmlColor.toWxColor(self._umlPreferences.gridLineColor)

        gridLineStyle: PenStyle = UmlPenStyle.toWxPenStyle(self._umlPreferences.gridLineStyle)

        pen:           Pen    = Pen(PenInfo(gridLineColor).Style(gridLineStyle).Width(1))

        return pen

    def _createDC(self, w: int, h: int) -> DC:
        """
        Create a DC, load the background on demand.

        Args:
            w: width of the frame.
            h: height of the frame.

        Returns:  A device context
        """
        dc: MemoryDC = MemoryDC()
        bm: Bitmap   = self._workingBitmap
        # cache the bitmap, to avoid creating a new one at each refresh.
        # only recreate it if the size of the window has changed
        if (bm.GetWidth(), bm.GetHeight()) != (w, h):
            bm = self.__workingBitmap = Bitmap(w, h)
        dc.SelectObject(bm)

        dc.SetBackground(Brush(self.GetBackgroundColour()))
        dc.Clear()

        self.PrepareDC(dc)

        return dc

    def _setAppropriateSetBackground(self):

        # noinspection PySimplifyBooleanCheck
        if self._darkMode is True:
            color: Colour = UmlColor.toWxColor(self._umlPreferences.darkModeBackGroundColor)
            self.SetBackgroundColour(color)
        else:
            color = UmlColor.toWxColor(self._umlPreferences.backGroundColor)
            self.SetBackgroundColour(color)
