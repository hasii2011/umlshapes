
from typing import cast

from logging import Logger
from logging import getLogger

from wx import MemoryDC

from umlshapes.lib.ogl import RectangleShape

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.UmlSDMessage import UmlSDMessages


class UmlSDLifeLine(IdentifierMixin, RectangleShape, TopLeftMixin):

    def __init__(self, sequenceDiagramFrame: SequenceDiagramFrame, instanceName: UmlInstanceName, instanceConstrainer: SDInstanceConstrainer):

        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        width:  int = 1
        height: int = self._preferences.initialLifeLineLength

        IdentifierMixin.__init__(self)
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

    @property
    def messages(self) -> UmlSDMessages:
        return cast(UmlSDMessages, self._lines)

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

    def addMessage(self, umlSDMessage: UmlSDMessage, destinationLifeLine: 'UmlSDLifeLine'):
        """

        Args:
            umlSDMessage:           The message between us and the 'other' life line
            destinationLifeLine:    The 'other'

        Returns:

        """

        self.AddLine(line=umlSDMessage, other=destinationLifeLine)

    def OnDraw(self, dc: MemoryDC):
        self.SetPen(ResourceUtils.blackSolidPen())
        super().OnDraw(dc=dc)

    def __str__(self) -> str:
        return f'UmlSDLifeLine: {self.id}'

    def __repr__(self) -> str:
        return self.__str__()
