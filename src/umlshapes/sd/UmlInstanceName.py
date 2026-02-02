
from logging import Logger
from logging import getLogger

from umlmodel.SDInstance import SDInstance

from umlshapes.UmlUtils import UmlUtils
from umlshapes.lib.ogl import RectangleShape

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlDimensions import UmlDimensions


class UmlInstanceName(RectangleShape):
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
        self.SetFont(UmlUtils.defaultFont())
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
