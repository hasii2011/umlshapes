
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import RectangleShape

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.shapes.sd.UmlSDLifeLine import UmlSDLifeLine

from umlshapes.types.UmlDimensions import UmlDimensions

if TYPE_CHECKING:
    from umlshapes.shapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame


class UmlInstanceName(RectangleShape):
    """
    Use Shape's capabilities to create a name value
    """

    def __init__(self, sdInstance: SDInstance, sequenceDiagramFrame: 'SequenceDiagramFrame'):

        self.logger: Logger = getLogger(__name__)

        self._sdInstance: SDInstance = sdInstance

        self._preferences:  UmlPreferences = UmlPreferences()
        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

        width:  int = instanceDimensions.width
        height: int = round(instanceDimensions.height * self._preferences.instanceNameRelativeHeight)

        super().__init__(w=width, h=height)
        self.SetCanvas(sequenceDiagramFrame)

        self.AddText(sdInstance.instanceName)

    @property
    def instanceName(self) -> str:
        return self._sdInstance.instanceName

    @instanceName.setter
    def instanceName(self, instanceName: str):

        self._sdInstance.instanceName = instanceName
        self.ClearText()
        self.AddText(instanceName)

    def attachLifeline(self, umlSDLifeLine: UmlSDLifeLine, constrainer: 'SDInstanceConstrainer'):

        self.AddLine(line=umlSDLifeLine, other=constrainer)

        umlSDLifeLine.instanceName        = self
        umlSDLifeLine.instanceConstrainer = constrainer
