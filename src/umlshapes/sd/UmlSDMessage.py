
from typing import cast
from typing import List
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from enum import Enum

from wx import BLACK_BRUSH

from wx import Pen
from wx import MemoryDC

from umlshapes.lib.ogl import LineShape
from umlshapes.lib.ogl import ARROW_ARROW
from umlshapes.lib.ogl import ARROW_POSITION_END
from umlshapes.lib.ogl import FORMAT_SIZE_TO_CONTENTS

from umlshapes.UmlUtils import UmlUtils

from umlmodel.SDMessage import SDMessage

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.sd.UmlMessageEnd import UmlMessageEnd
if TYPE_CHECKING:
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

class UmlMessageType(Enum):
    SYNCHRONOUS_MESSAGE = 'Synchronous Message'


class UmlSDMessage(LineShape):
    def __init__(self, sdMessage: SDMessage, messageType: UmlMessageType = UmlMessageType.SYNCHRONOUS_MESSAGE):

        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        self.logger: Logger = getLogger(__name__)
        super().__init__()

        self._sdMessage:   SDMessage      = sdMessage
        self._messageType: UmlMessageType = messageType
        self._preferences: UmlPreferences = UmlPreferences()
        self.AddText(sdMessage.message)
        #
        # TODO:  Support different message type that require different arrow heads
        #
        self.AddArrow(
            type=ARROW_ARROW,
            end=ARROW_POSITION_END,
            size=self._preferences.messageArrowHeadSize
        )
        self.SetBrush(BLACK_BRUSH)      # Required for solid arrow

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
        self.SetDraggable(True, recursive=True)
        self.MakeLineControlPoints(n=2)
        self._fromLifeline: UmlSDLifeLine = cast(UmlSDLifeLine, None)
        self._toLifeLine:   UmlSDLifeLine = cast(UmlSDLifeLine, None)

    @property
    def sdMessage(self) -> SDMessage:
        """

        Returns: The UML Model SD message
        """
        return self._sdMessage

    def updatePosition(self, umlMessageEnd: UmlMessageEnd, yPosition: int):
        """
        Updates the end point position so that the OnDraw method can then move it

        Args:
            umlMessageEnd:  The end to move
            yPosition:

        """

        self.logger.info(f'{umlMessageEnd=} {yPosition=}')

        xStart, yStart, xEnd, yEnd = self.GetEnds()

        if umlMessageEnd == umlMessageEnd.Start:
            self._sdMessage.sourceY = yPosition
            self.SetEnds(x1=xStart, y1=yPosition, x2=xEnd, y2=yEnd)
        else:
            self._sdMessage.destinationY = yPosition
            self.SetEnds(x1=xStart, y1=yPosition, x2=xEnd, y2=yPosition)

        self.logger.debug(f'{self._sdMessage=}')

    def updateMessage(self):
        """
        Update the message
        """
        text: str = self._sdMessage.message
        self.ClearText()
        self.AddText(text)

    def OnDraw(self, dc: MemoryDC):

        # TODO:  Support different message types here
        pen: Pen = UmlUtils.blackSolidPen()
        dc.SetPen(pen)

        startX, startY, endX, endY = self.GetEnds()

        fromX: int = self._fromLifeline.GetX()
        toX:   int = self._toLifeLine.GetX()
        dc.DrawLine(
            x1=round(fromX),
            y1=round(startY),
            x2=round(toX),
            y2=round(endY)
        )
        self.SetEnds(
            x1=round(fromX),
            y1=round(startY),
            x2=round(toX),
            y2=round(endY)
        )
        self.SetPen(pen)
        self.DrawArrows(dc=dc)

    def OnDrawContents(self, dc: MemoryDC):
        pass

    def SetFrom(self, fromLifeline: 'UmlSDLifeLine'):
        self._from         = fromLifeline
        self._fromLifeline = fromLifeline

    def SetTo(self, toLifeLine: 'UmlSDLifeLine'):
        self._to         = toLifeLine
        self._toLifeLine = toLifeLine

    def __str__(self) -> str:
        return f'UmlSDMessage: {self._sdMessage.message}'

    def __repr__(self) -> str:
        return self.__str__()


UmlSDMessages = NewType('UmlSDMessages', List[UmlSDMessage])
