from logging import Logger
from logging import getLogger

from wx import App
from wx import MemoryDC
from wx import ScreenDC

from umlmodel.SDInstance import SDInstance

from umlshapes.preferences.Defaults import DEFAULT_INSTANCE_HORIZONTAL_PADDING
from umlshapes.preferences.Defaults import MIN_INSTANCE_WIDTH
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.lib.ogl import RectangleShape
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlDimensions import UmlDimensions


class UmlInstanceName(RectangleShape, TopLeftMixin):
    """
    Use Shape's capabilities to create a name value
    """

    def __init__(self, sdInstance: SDInstance):
        self.logger: Logger = getLogger(__name__)

        self._preferences: UmlPreferences = UmlPreferences()

        self._sdInstance: SDInstance = sdInstance

        instanceDimensions: UmlDimensions = self._preferences.instanceDimensions

        width: int = instanceDimensions.width
        if self._preferences.autoFitInstanceWidth:
            autoFitWidth: int = self.computeAutoFitWidth(text=sdInstance.instanceName)
            if autoFitWidth > width:
                width = autoFitWidth

        height: int = round(instanceDimensions.height * self._preferences.instanceNameRelativeHeight)

        super().__init__(w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=width, height=height)
        self.SetFont(ResourceUtils.defaultFont())
        self.AddText(sdInstance.instanceName)
        self.SetCentreResize(False)

    def computeAutoFitWidth(self, text: str) -> int:
        """
        Compute the width required to fit the instance name text with horizontal padding.

        Args:
            text: The instance name string to measure.

        Returns:
            The minimum width required in pixels.
        """
        textWidth: int
        if App.Get() is None:
            textWidth = len(text) * 8
        else:
            screenDc: ScreenDC = ScreenDC()
            screenDc.SetFont(ResourceUtils.defaultFont())
            textWidth, _ = screenDc.GetTextExtent(text)

        paddedWidth: int = textWidth + DEFAULT_INSTANCE_HORIZONTAL_PADDING
        if paddedWidth < MIN_INSTANCE_WIDTH:
            return MIN_INSTANCE_WIDTH
        return paddedWidth

    @property
    def size(self) -> UmlDimensions:
        return super().size

    @size.setter
    def size(self, newSize: UmlDimensions):
        self._shape.SetSize(newSize.width, newSize.height)
        self._size.SetWidth(newSize.width)
        self._size.SetHeight(newSize.height)
        self.ClearText()
        self.AddText(self._sdInstance.instanceName)

    @property
    def width(self) -> int:
        return self.size.width

    @width.setter
    def width(self, newWidth: int):
        self.size = UmlDimensions(width=newWidth, height=self.size.height)

    @property
    def sdInstance(self) -> SDInstance:
        return self._sdInstance

    @sdInstance.setter
    def sdInstance(self, sdInstance: SDInstance):

        self._sdInstance = sdInstance
        if self._preferences.autoFitInstanceWidth:
            newWidth: int = self.computeAutoFitWidth(text=sdInstance.instanceName)
            if newWidth != self.width:
                self.width = newWidth
        self.ClearText()
        self.AddText(sdInstance.instanceName)

    @property
    def instanceName(self) -> str:
        return self._sdInstance.instanceName

    @instanceName.setter
    def instanceName(self, newName: str):
        self._sdInstance.instanceName = newName
        self.ClearText()
        self.AddText(newName)

    def OnDraw(self, dc: MemoryDC):
        """
        Draw the instance name rectangle, highlighting in red dashed pen when selected.

        Args:
            dc:
        """
        if self.AncestorSelected() is True:
            self.SetPen(ResourceUtils.redDashedPen())
        else:
            self.SetPen(ResourceUtils.blackSolidPen())

        super().OnDraw(dc)
