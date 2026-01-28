
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger
from typing import Tuple

from umlshapes.UmlUtils import NO_INTERSECTION
from umlshapes.UmlUtils import UmlUtils
from umlshapes.lib.ogl import LineShape
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.types.UmlLine import UmlLine
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
    from umlshapes.sd.UmlInstanceName import UmlInstanceName
    from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer

class UmlSDLifeLine(LineShape):
    """
    """
    def __init__(self, sequenceDiagramFrame: 'SequenceDiagramFrame', instanceName: 'UmlInstanceName', instanceConstrainer: 'SDInstanceConstrainer'):
        """

        Args:
            sequenceDiagramFrame:   The sequence diagram frame I appear on
            instanceName:           The instance name shape that I start from
            instanceConstrainer:    The constrainer shape that I connect to on the bottom
        """

        from umlshapes.sd.UmlInstanceName import UmlInstanceName
        from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer

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

    def setLifeLineEnds(self):
        """

        """

        instanceNameHeight: int = self._umlInstanceName.GetHeight()
        self.logger.debug(f'{instanceNameHeight=}')

        startX: int = round(self._umlInstanceName.GetX())
        startY: int = round(self._umlInstanceName.GetY() + (instanceNameHeight // 2))
        self.logger.debug(f'x2y2: ({startX},{startY})')

        constrainerHeight: int = self._instanceConstrainer.GetHeight()
        endX: int = round(self._instanceConstrainer.GetX())
        endY: int = round(self._instanceConstrainer.GetY() + (constrainerHeight // 2))
        self.logger.debug(f'x1y1: ({endX},{endY})')

        self.SetEnds(
            x1=startX,
            y1=startY,
            x2=endX,
            y2=endY
        )

        self.logger.debug(f'------------------')

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

    def GetPerimeterPoint(self, x1, y1, x2, y2) -> Tuple[int, int] | bool:
        """
        Get the point at which the line from (x1, y1) to (x2, y2) hits
        the shape.

        Args:
            x1: Start of line
            y1:
            x2: End of line
            y2:

        Returns:    `False` if the line doesn't hit the perimeter.
        """
        x3, y3, x4, y4 = self.GetEnds()
        lifeLine: UmlLine = UmlLine(
            start=UmlPosition(x=x3, y=y3),
            end=UmlPosition(x=x4, y=y4)
        )
        checkLine: UmlLine = UmlLine(
            start=UmlPosition(x=x1, y=y1),
            end=UmlPosition(x=x2, y=y2)
        )
        umlPosition: UmlPosition = UmlUtils.getIntersectionPoint(line1=lifeLine, line2=checkLine)
        if umlPosition == NO_INTERSECTION:
            assert False, 'Why am I getting no intersection'
        else:
            return umlPosition.x, umlPosition.y

    def __str__(self) -> str:
        return self._umlInstanceName.sdInstance.instanceName

    def __repr__(self) -> str:
        return self.__str__()
