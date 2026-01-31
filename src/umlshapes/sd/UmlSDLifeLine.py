
from logging import Logger
from logging import getLogger

from umlshapes.lib.ogl import RectangleShape

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlInstanceName import UmlInstanceName


class UmlSDLifeLine(RectangleShape, TopLeftMixin):

    def __init__(self, sequenceDiagramFrame: SequenceDiagramFrame, instanceName: UmlInstanceName, instanceConstrainer: SDInstanceConstrainer):

        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        width:  int = 1
        height: int = self._preferences.initialLifeLineLength

        RectangleShape.__init__(self, w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=width, height=height)

        self.SetCanvas(sequenceDiagramFrame)
        self._umlInstanceName:     UmlInstanceName       = instanceName
        self._instanceConstrainer: SDInstanceConstrainer = instanceConstrainer

    @property
    def umlFrame(self) -> SequenceDiagramFrame:
        return self.GetCanvas()

    @property
    def umlInstanceName(self) -> UmlInstanceName:
        return self._umlInstanceName

    @property
    def instanceConstrainer(self) -> SDInstanceConstrainer:
        return self._instanceConstrainer

    def adjustLifeLineTopPosition(self):

        self.logger.debug(f'------------------')

        umlInstanceName: UmlInstanceName = self._umlInstanceName
        instanceNameHeight: int = umlInstanceName.GetHeight()
        instanceNameWidth:  int = umlInstanceName.GetWidth()
        centerX:            int = umlInstanceName.GetX()
        centerY:            int = umlInstanceName.GetY()
        self.logger.debug(f'{instanceNameHeight=} {instanceNameWidth=} {centerX=} {centerY=}')

        instanceNameBottomY: int = centerY + (instanceNameHeight // 2)
        self.logger.debug(f'{instanceNameBottomY=}')

        lifeLineTopY: int = instanceNameBottomY + round(self.GetHeight() // 2)

        self.SetY(lifeLineTopY)
        self.logger.debug(f'------------------')
