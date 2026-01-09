
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger
from typing import cast

from wx import DC
from wx import BLACK
from wx import MemoryDC
from wx import BLACK_PEN
from wx import PENSTYLE_DOT
from wx import PENSTYLE_SOLID
from wx import PENSTYLE_TRANSPARENT
from wx import BRUSHSTYLE_TRANSPARENT

from wx import Pen
from wx import RED
from wx import Font
from wx import Brush
from wx import RED_PEN

from wx import Size

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import RectangleShape

from umlshapes.UmlUtils import UmlUtils

from umlshapes.mixins.IDMixin import IDMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import LeftCoordinate
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlDimensions import UmlDimensions

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame


class UmlSdInstance(RectangleShape, IDMixin, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, xPosition):

        self._sdInstance: SDInstance = sdInstance

        self.logger: Logger = getLogger(__name__)

        self._preferences: UmlPreferences = UmlPreferences()

        instanceWidth:  int = self._preferences.instanceDimensions.width
        instanceHeight: int = self._preferences.instanceDimensions.height

        super().__init__(w=instanceWidth, h=instanceHeight)

        instanceSize: UmlDimensions = UmlDimensions(width=instanceWidth, height=instanceHeight)

        IDMixin.__init__(self, shape=self)
        TopLeftMixin.__init__(self, umlShape=self, width=instanceSize.width, height=instanceSize.height)

        instancePosition: UmlPosition = UmlPosition(
            x=xPosition,
            y=self._preferences.instanceYPosition
        )
        self.position = instancePosition
        self._defaultFont:              Font  = UmlUtils.defaultFont()
        self._instanceNameRelativeSize: float = self._preferences.instanceNameRelativeHeight
        self._textHeight:               int   = cast(int, None)

        self._inDebugMode: bool = self._preferences.debugSDInstance
        if self._inDebugMode is True:
            self.SetPen(RED_PEN)

    @property
    def sdInstance(self) -> SDInstance:
        return self._sdInstance

    @sdInstance.setter
    def sdInstance(self, sdInstance: SDInstance):
        self._sdInstance = sdInstance

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    def OnDraw(self, dc: MemoryDC):
        """
        Start coordinates are on the UML Class perimeter
        End coordinates are where the line ends and the circle is drawn

        Args:
            dc:
        """
        if self._textHeight is None:
            self._textHeight = self._determineTextHeight(dc)  + self._preferences.lineHeightAdjustment

        brush: Brush = self.GetBrush()
        pen:   Pen   = self.GetPen()

        brush.SetStyle(BRUSHSTYLE_TRANSPARENT)
        if self._inDebugMode is True:
            pen.SetStyle(PENSTYLE_DOT)
        else:
            pen.SetStyle(PENSTYLE_TRANSPARENT)

        dc.SetFont(self._defaultFont)
        if self.selected:
            dc.SetPen(RED_PEN)
            dc.SetTextForeground(RED)
        else:
            dc.SetPen(BLACK_PEN)
            dc.SetTextForeground(BLACK)

        super().OnDraw(dc=dc)

        self._drawInstanceBox(dc, pen)
        self._drawInstanceLifeLine(dc)

    def _drawInstanceBox(self, dc: MemoryDC, pen: Pen):
        """

        Args:
            dc:
            pen:
        """
        x: int = self.position.x
        y: int = self._preferences.instanceYPosition
        width:  int = self.size.width
        height: int = round(self.size.height * self._instanceNameRelativeSize)

        pen.SetWidth(1)
        pen.SetStyle(PENSTYLE_SOLID)
        pen.SetColour(BLACK)
        dc.SetPen(pen)

        dc.DrawRectangle(x, y, width, height)
        self._drawInstanceName(dc=dc)

    def _drawInstanceName(self, dc: MemoryDC):

        leftCoordinate: LeftCoordinate = self._computeTopLeft()
        x: int = leftCoordinate.x
        y: int = leftCoordinate.y
        w: int = self.size.width

        instanceName: str = self.sdInstance.instanceName

        #
        # Draw the class name
        nameWidth: int = self._textWidth(dc, instanceName)
        nameX:     int = x + (w - nameWidth) // 2
        nameY:     int = y + self._textHeight

        dc.DrawText(instanceName, nameX, nameY)

    def _drawInstanceLifeLine(self, dc: MemoryDC):
        """
        Draw Instance Life Line
        Args:
            dc:
        """

        startX: int = self.position.x + (self.size.width // 2)
        y:      int = self._preferences.instanceYPosition + round(self.size.height * self._instanceNameRelativeSize)

        endX:  int = startX
        destY: int = self.position.y + self.size.height

        dc.DrawLine(x1=startX, y1=y, x2=endX, y2=destY)

    def _textWidth(self, dc: DC, text: str):
        """

        Args:
            dc:   Current device context
            text: The string to measure

        Returns:
        """

        size: Size = dc.GetTextExtent(text)

        return size.width

    def _determineTextHeight(self, dc: DC):
        """
        Convenience method

        Args:
            dc:   Current device context

        Returns:  Text height of typical character
        """

        size: Size = dc.GetTextExtent('*')
        return round(size.height)
