
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import FONTWEIGHT_NORMAL
from wx import Font

from umlmodel.SDInstance import SDInstance

from umlshapes.UmlUtils import UmlUtils
from umlshapes.lib.ogl import RectangleShape

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.shapes.sd.UmlSDLifeLine import UmlSDLifeLine

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlFontFamily import UmlFontFamily

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

        self._initializeTextFont()
        self.AddText(sdInstance.instanceName)

    @property
    def sdInstance(self) -> SDInstance:
        return self._sdInstance

    @sdInstance.setter
    def sdInstance(self, sdInstance: SDInstance):

        self._sdInstance = sdInstance
        self.ClearText()
        self.AddText(sdInstance.instanceName)

    def attachLifeline(self, umlSDLifeLine: UmlSDLifeLine, constrainer: 'SDInstanceConstrainer'):

        self.AddLine(line=umlSDLifeLine, other=constrainer)

        umlSDLifeLine.umlInstanceName        = self
        umlSDLifeLine.instanceConstrainer = constrainer

    def _initializeTextFont(self):
        """
        Use a partial version of the defaults
        """
        textSize:    int  = self._preferences.textFontSize
        defaultFont: Font = UmlUtils.defaultFont()
        textFont:    Font = defaultFont.GetBaseFont()

        textFont.SetPointSize(textSize)
        textFont.SetPointSize(textSize)
        textFont.SetWeight(FONTWEIGHT_NORMAL)

        textFontFamily: UmlFontFamily = self._preferences.textFontFamily
        textFont.SetFamily(UmlUtils.umlFontFamilyToWxFontFamily(textFontFamily))

        self.SetFont(textFont)

    def __str__(self) -> str:
        return f'UmlInstanceName: {self.sdInstance.instanceName}'

    def __repr__(self) -> str:
        return str(self)
