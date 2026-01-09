
from logging import Logger
from logging import getLogger

from umlmodel.SDInstance import SDInstance

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
        self.AddText(sdInstance.instanceName)

    @property
    def instanceName(self) -> str:
        return self._sdInstance.instanceName

    @instanceName.setter
    def instanceName(self, instanceName: str):

        self._sdInstance.instanceName = instanceName
        self.ClearText()
        self.AddText(instanceName)
