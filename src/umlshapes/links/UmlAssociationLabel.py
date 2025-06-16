
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Font
from wx import MemoryDC

from wx.lib.ogl import FORMAT_CENTRE_HORIZ
from wx.lib.ogl import FORMAT_CENTRE_VERT
from wx.lib.ogl import TextShape

from umlshapes.UmlUtils import UmlUtils
from umlshapes.links.DeltaXY import DeltaXY
from umlshapes.links.LabelType import LabelType

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlDimensions import UmlDimensions


class UmlAssociationLabel(ControlPointMixin, TextShape, TopLeftMixin):

    def __init__(self, label: str = '', size: UmlDimensions = None, labelType: LabelType = LabelType.NOT_SET):
        """

        Args:
            label:
            size:
            labelType: Source or Destination Cardinality or association name
        """
        # Use preferences to get initial size if not specified
        self._preferences: UmlPreferences = UmlPreferences()

        if size is None:
            labelSize: UmlDimensions = self._preferences.associationLabelSize
        else:
            labelSize = size

        super().__init__(shape=self)
        TextShape.__init__(self, width=labelSize.width, height=labelSize.height)
        TopLeftMixin.__init__(self, umlShape=self, width=labelSize.width, height=labelSize.height)

        self.logger: Logger = getLogger(__name__)

        font: Font = self.GetFont()
        font.SetPointSize(self._preferences.associationTextFontSize)
        self.SetFont(font)

        self.AddText(label)
        self.SetFormatMode(mode=FORMAT_CENTRE_HORIZ | FORMAT_CENTRE_VERT)
        self.SetDraggable(drag=True)
        self.Show(show=True)
        self.SetCentreResize(False)

        self._linkDelta: DeltaXY   = DeltaXY()          # no delta to start with
        self._labelType: LabelType = labelType
        self._label:     str       = label

    def OnDraw(self, dc: MemoryDC):

        dc.SetBrush(self._brush)

        if self.Selected() is True:
            UmlUtils.drawSelectedRectangle(dc=dc, shape=self)

    def OnDrawContents(self, dc):

        if self.Selected() is True:
            self.SetTextColour('Red')
        else:
            self.SetTextColour('Black')

        super().OnDrawContents(dc=dc)

    @property
    def parent(self) -> 'UmlLink':
        return self.GetParent()

    @parent.setter
    def parent(self, parent: 'UmlLink'):
        self.SetParent(parent)

    @property
    def linkDelta(self) -> DeltaXY:
        return self._linkDelta

    @linkDelta.setter
    def linkDelta(self, deltaXY: DeltaXY):
        self._linkDelta = deltaXY

    @property
    def labelType(self) -> LabelType:
        return self._labelType

    @labelType.setter
    def labelType(self, labelType: LabelType):
        self._labelType = labelType

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label
        self.ClearText()
        self.AddText(label)

    def coordinateToRelative(self, x: int, y: int):
        """
        Convert absolute coordinates to relative ones.
        Relative coordinates are coordinates relative to the origin of the
        shape.

        Args:
            x:
            y:

        Returns:  Coordinates relative to the top left
        """
        from umlshapes.shapes.UmlClass import UmlClass

        if self.parent is not None:
            umlClass: UmlClass = cast(UmlClass, self.parent)
            ox: int = umlClass.position.x
            oy: int = umlClass.position.y
            x -= ox
            y -= oy

        return x, y

    def __str__(self) -> str:
        return f'UmlAssociationLabel - `{self.label}`'

    def __repr__(self) -> str:
        return f'UmlAssociationLabel - `{self.label}` type={self.labelType}'
