from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import App
from wx import Font
from wx import MemoryDC
from wx import ScreenDC
from wx import TRANSPARENT_BRUSH

from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import TextShape

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.PubSubMixin import PubSubMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.utils.DrawingUtils import DrawingUtils

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame

DEFAULT_LABEL_WIDTH:       int = 75
DEFAULT_LABEL_HEIGHT:      int = 24
DEFAULT_LABEL_FONT_SIZE:   int = 12
DEFAULT_LABEL_FORMAT_MODE: int = 1
LABEL_HORIZONTAL_PADDING:  int = 14
LABEL_VERTICAL_PADDING:    int = 6


class UmlBaseLabel(ControlPointMixin, TextShape, TopLeftMixin, PubSubMixin, IdentifierMixin):
    """
    Base class for floating diagram text labels attached to shapes or links.
    """

    def __init__(self, label: str = '', size: Optional[UmlDimensions] = None, fontSize: Optional[int] = None, formatMode: Optional[int] = None):
        """

        Args:
            label:      The text of the label
            size:       Optional width and height dimensions
            fontSize:   Optional font point size
            formatMode: Optional OGL formatting bitmask
        """
        self._preferences: UmlPreferences = UmlPreferences()
        self.logger:       Logger         = getLogger(__name__)

        actualFontSize: int
        if fontSize is not None:
            actualFontSize = fontSize
        else:
            actualFontSize = DEFAULT_LABEL_FONT_SIZE

        actualFormatMode: int
        if formatMode is not None:
            actualFormatMode = formatMode
        else:
            actualFormatMode = DEFAULT_LABEL_FORMAT_MODE

        initialWidth: int
        if size is not None:
            initialWidth = size.width
        else:
            initialWidth = DEFAULT_LABEL_WIDTH

        initialHeight: int
        if size is not None:
            initialHeight = size.height
        else:
            initialHeight = DEFAULT_LABEL_HEIGHT

        super().__init__(shape=self)
        TextShape.__init__(self, width=initialWidth, height=initialHeight)
        TopLeftMixin.__init__(self, umlShape=self, width=initialWidth, height=initialHeight)
        PubSubMixin.__init__(self)
        IdentifierMixin.__init__(self)

        font: Font = self.GetFont()
        font.SetPointSize(actualFontSize)
        self.SetFont(font)

        labelSize: UmlDimensions
        if size is not None:
            labelSize = size
        else:
            labelSize = self._computeSizeForText(text=label, font=font)
        self.SetSize(labelSize.width, labelSize.height)

        self.SetFormatMode(mode=actualFormatMode)
        self.AddText(label)

        self.SetBrush(TRANSPARENT_BRUSH)
        self.SetDraggable(drag=True)
        self.Show(show=True)
        self.SetCentreResize(False)

        self._label: str = label

    @property
    def umlFrame(self) -> 'UmlFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'UmlFrame'):
        self.SetCanvas(frame)

    @property
    def parent(self) -> Shape:
        return self.GetParent()

    @parent.setter
    def parent(self, parentShape: Shape):
        self.SetParent(parentShape)

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label
        self.ClearText()
        self.AddText(label)
        self.fitToText()

    def fitToText(self):
        newSize: UmlDimensions = self._computeSizeForText(text=self._label, font=self.GetFont())
        self.SetSize(newSize.width, newSize.height)
        self._formatted = False

    def SetSize(self, x: float, y: float, recursive: bool = True):

        super().SetSize(x, y, recursive=recursive)
        intWidth:  int = round(x)
        intHeight: int = round(y)
        if hasattr(self, '_size') and self._size is not None:
            self._size.SetWidth(intWidth)
            self._size.SetHeight(intHeight)
        self._formatted = False

    def OnDraw(self, dc: MemoryDC):
        dc.SetBrush(self._brush)

        if self.Selected() is True:
            DrawingUtils.drawSelectedRectangle(dc=dc, shape=self)

    def OnDrawContents(self, dc: MemoryDC):
        if self.Selected() is True:
            self.SetTextColour('Red')
        else:
            self.SetTextColour('Black')

        if not self._formatted:
            self.Recentre(dc)
            self._formatted = True

        super().OnDrawContents(dc=dc)

    def _computeTextExtent(self, text: str, font: Font) -> UmlDimensions:
        """
        Compute the pixel extent (width and height) of the given text using the specified font.

        Note:
            We might move this method to DrawingUtils if another shape needs this capability.

        Args:
            text: The string to measure
            font: The wx.Font used for rendering

        Returns:
            UmlDimensions containing text width and height in pixels
        """
        if App.Get() is None:
            estimatedWidth: int = len(text) * 8
            return UmlDimensions(width=estimatedWidth, height=14)

        screenDc: ScreenDC = ScreenDC()
        screenDc.SetFont(font)

        textWidth:  int
        textHeight: int
        textWidth, textHeight = screenDc.GetTextExtent(text)

        return UmlDimensions(width=textWidth, height=textHeight)

    def _computeSizeForText(self, text: str, font: Font) -> UmlDimensions:
        """
        Compute padded label dimensions required to accommodate the given text.

        Note:
            We might move this method to DrawingUtils if another shape needs this capability.

        Args:
            text: The string to measure
            font: The wx.Font used for rendering

        Returns:
            UmlDimensions containing the padded width and height
        """
        if not text:
            return UmlDimensions(width=DEFAULT_LABEL_WIDTH, height=DEFAULT_LABEL_HEIGHT)

        extent:         UmlDimensions = self._computeTextExtent(text=text, font=font)
        computedWidth:  int           = extent.width + LABEL_HORIZONTAL_PADDING
        computedHeight: int           = max(extent.height + LABEL_VERTICAL_PADDING, DEFAULT_LABEL_HEIGHT)

        return UmlDimensions(width=computedWidth, height=computedHeight)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} - `{self.label}`'

    def __repr__(self) -> str:
        return self.__str__()
