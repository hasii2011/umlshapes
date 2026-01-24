
from typing import cast
from typing import List
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import MemoryDC
from wx import PENSTYLE_SOLID
from wx import Pen

from umlshapes.UmlUtils import UmlUtils
from umlshapes.lib.ogl import ARROW_ARROW
from umlshapes.lib.ogl import FORMAT_SIZE_TO_CONTENTS
from umlshapes.lib.ogl import LineShape

from umlmodel.SDMessage import SDMessage

from umlshapes.sd.UmlMessageEnd import UmlMessageEnd
if TYPE_CHECKING:
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


class UmlSDMessage(LineShape):
    def __init__(self, sdMessage: SDMessage):
        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        self.logger: Logger = getLogger(__name__)
        super().__init__()

        self._sdMessage: SDMessage = sdMessage
        # self._initializeTextFont()
        self.AddText(sdMessage.message)
        self.AddArrow(type=ARROW_ARROW)

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
        self.SetDraggable(True, recursive=True)

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
        savePen: Pen = dc.GetPen()

        # TODO:  Support different message types here
        pen: Pen = UmlUtils.blackSolidPen()
        pen.SetStyle(PENSTYLE_SOLID)
        dc.SetPen(pen)

        startX, startY, endX, endY = self.GetEnds()

        dc.DrawLine(
            x1=startX,
            y1=startY,
            x2=endX,
            y2=endY
        )

        self.SetPen(pen)
        self.DrawArrows(dc)

        dc.SetPen(savePen)

    def OnDrawContents(self, dc: MemoryDC):
        pass

    def SetFrom(self, fromLifeline: 'UmlSDLifeLine'):
        self._fromLifeline = fromLifeline

    def SetTo(self, toLifeLine: 'UmlSDLifeLine'):
        self._toLifeLine = toLifeLine

    def __str__(self) -> str:
        return f'UmlSDMessage: {self._sdMessage.message}'

    def __repr__(self) -> str:
        return self.__str__()


UmlSDMessages = NewType('UmlSDMessages', List[UmlSDMessage])
