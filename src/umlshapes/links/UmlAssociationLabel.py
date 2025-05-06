
from logging import Logger
from logging import getLogger

from wx import MemoryDC

from wx.lib.ogl import TextShape

from umlshapes.UmlUtils import UmlUtils
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

        self.SetDraggable(drag=True)
        self.Show(show=True)
        self.SetCentreResize(False)

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
