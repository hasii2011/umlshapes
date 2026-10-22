
from logging import Logger
from logging import getLogger

from wx import MemoryDC

from umlmodel.SDInstance import SDInstance

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.lib.ogl import RectangleShape
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlDimensions import UmlDimensions


class UmlInstanceName(RectangleShape, TopLeftMixin):
    """
    Use Shape's capabilities to create a name value
    """

    def __init__(self, sdInstance: SDInstance):
        self.logger: Logger = getLogger(__name__)

        self._preferences: UmlPreferences = UmlPreferences()

        self._sdInstance: SDInstance = sdInstance

        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

        width:  int = instanceDimensions.width
        height: int = round(instanceDimensions.height * self._preferences.instanceNameRelativeHeight)

        super().__init__(w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=width, height=height)
        self.SetFont(ResourceUtils.defaultFont())
        self.AddText(sdInstance.instanceName)
        self.SetCentreResize(False)

    @property
    def sdInstance(self) -> SDInstance:
        return self._sdInstance

    @sdInstance.setter
    def sdInstance(self, sdInstance: SDInstance):

        self._sdInstance = sdInstance
        self.ClearText()
        self.AddText(sdInstance.instanceName)

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
