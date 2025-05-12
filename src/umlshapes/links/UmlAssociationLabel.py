
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import MemoryDC

from wx.lib.ogl import FORMAT_CENTRE_HORIZ
from wx.lib.ogl import FORMAT_CENTRE_VERT
from wx.lib.ogl import TextShape

from umlshapes.UmlUtils import UmlUtils
from umlshapes.links.DeltaXY import DeltaXY

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.ControlPointMixin import ControlPointMixin
from umlshapes.shapes.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlDimensions import UmlDimensions


class UmlAssociationLabel(ControlPointMixin, TextShape, TopLeftMixin):

    def __init__(self, label: str = '', size: UmlDimensions = None):

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

        if label == '':
            realLabel: str = self._preferences.defaultAssociationName
        else:
            realLabel = label

        self.AddText(realLabel)
        self.SetFormatMode(mode=FORMAT_CENTRE_HORIZ | FORMAT_CENTRE_VERT)
        self.SetDraggable(drag=True)
        self.Show(show=True)
        self.SetCentreResize(False)

        self._nameDelta: DeltaXY = DeltaXY()    # no delta to start with

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
    def nameDelta(self) -> DeltaXY:
        return self._nameDelta

    @nameDelta.setter
    def nameDelta(self, deltaXY: DeltaXY):
        self._nameDelta = deltaXY

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
