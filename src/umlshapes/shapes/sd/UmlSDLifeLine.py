
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlshapes.lib.ogl import LineShape

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
        self._instanceName:        UmlInstanceName       = instanceName
        self._instanceConstrainer: SDInstanceConstrainer = instanceConstrainer

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def instanceName(self) -> 'UmlInstanceName':
        return self._instanceName

    @instanceName.setter
    def instanceName(self, instanceName: 'UmlInstanceName'):
        self._instanceName = instanceName

    @property
    def instanceConstrainer(self) -> 'SDInstanceConstrainer':
        return self._instanceConstrainer

    @instanceConstrainer.setter
    def instanceConstrainer(self, instanceConstrainer: 'SDInstanceConstrainer'):
        self._instanceConstrainer = instanceConstrainer
