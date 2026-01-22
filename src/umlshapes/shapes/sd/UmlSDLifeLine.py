
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlshapes.lib.ogl import LineShape
from umlshapes.shapes.sd.UmlSDMessage import UmlSDMessage

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
    from umlshapes.shapes.sd.UmlInstanceName import UmlInstanceName
    from umlshapes.shapes.sd.SDInstanceConstrainer import SDInstanceConstrainer

class UmlSDLifeLine(LineShape):
    def __init__(self, sequenceDiagramFrame: 'SequenceDiagramFrame', instanceName: 'UmlInstanceName', instanceConstrainer: 'SDInstanceConstrainer'):

        from umlshapes.shapes.sd.UmlInstanceName import UmlInstanceName
        from umlshapes.shapes.sd.SDInstanceConstrainer import SDInstanceConstrainer

        self.logger: Logger = getLogger(__name__)

        super().__init__()

        self.SetCanvas(sequenceDiagramFrame)
        self._umlInstanceName:     UmlInstanceName       = instanceName
        self._instanceConstrainer: SDInstanceConstrainer = instanceConstrainer

    @property
    def sequenceDiagramFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @sequenceDiagramFrame.setter
    def sequenceDiagramFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def umlInstanceName(self) -> 'UmlInstanceName':
        return self._umlInstanceName

    @umlInstanceName.setter
    def umlInstanceName(self, instanceName: 'UmlInstanceName'):
        self._umlInstanceName = instanceName

    @property
    def instanceConstrainer(self) -> 'SDInstanceConstrainer':
        return self._instanceConstrainer

    @instanceConstrainer.setter
    def instanceConstrainer(self, instanceConstrainer: 'SDInstanceConstrainer'):
        self._instanceConstrainer = instanceConstrainer

    def addMessage(self, umlSDMessage: UmlSDMessage, destinationLifeLine: 'UmlSDLifeLine'):
        """

        Args:
            umlSDMessage:           The message between us and the 'other' life line
            destinationLifeLine:    The 'other'

        Returns:

        """

        self.AddLine(line=umlSDMessage, other=destinationLifeLine)

        # umlLink.sourceShape      = self
        # umlLink.destinationShape = destinationClass

    def __str__(self) -> str:
        return self._umlInstanceName.sdInstance.instanceName

    def __repr__(self) -> str:
        return self.__str__()
