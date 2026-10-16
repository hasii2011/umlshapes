from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import Font
from wx import MemoryDC
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

DEFAULT_LABEL_WIDTH: int = 75
DEFAULT_LABEL_HEIGHT: int = 24
DEFAULT_LABEL_FONT_SIZE: int = 12
DEFAULT_LABEL_FORMAT_MODE: int = 1


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
        self.logger: Logger = getLogger(__name__)

        labelSize: UmlDimensions = size if size is not None else UmlDimensions(width=DEFAULT_LABEL_WIDTH, height=DEFAULT_LABEL_HEIGHT)
        actualFontSize: int = fontSize if fontSize is not None else DEFAULT_LABEL_FONT_SIZE
        actualFormatMode: int = formatMode if formatMode is not None else DEFAULT_LABEL_FORMAT_MODE

        super().__init__(shape=self)
        TextShape.__init__(self, width=labelSize.width, height=labelSize.height)
        TopLeftMixin.__init__(self, umlShape=self, width=labelSize.width, height=labelSize.height)
        PubSubMixin.__init__(self)
        IdentifierMixin.__init__(self)

        self.SetFormatMode(mode=actualFormatMode)

        font: Font = self.GetFont()
        font.SetPointSize(actualFontSize)
        self.SetFont(font)

        self.AddText(label)

        self.SetBrush(TRANSPARENT_BRUSH)
        self.SetDraggable(drag=True)
        self.Show(show=True)
        self.SetCentreResize(False)

        self._label: str = label

    def OnDraw(self, dc: MemoryDC):
        dc.SetBrush(self._brush)

        if self.Selected() is True:
            DrawingUtils.drawSelectedRectangle(dc=dc, shape=self)

    def OnDrawContents(self, dc: MemoryDC):
        if self.Selected() is True:
            self.SetTextColour('Red')
        else:
            self.SetTextColour('Black')

        super().OnDrawContents(dc=dc)

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

    def __str__(self) -> str:
        return f'{self.__class__.__name__} - `{self.label}`'

    def __repr__(self) -> str:
        return self.__str__()
