
from typing import List
from typing import cast
from typing import NewType

from logging import Logger
from logging import getLogger

from enum import Enum

from wx import Brush
from wx import WHITE
from wx import BLACK_BRUSH
from wx import BRUSHSTYLE_TRANSPARENT

from umlshapes.UmlUtils import UmlUtils
from umlshapes.lib.ogl import LineShape
from umlshapes.lib.ogl import ARROW_ARROW
from umlshapes.lib.ogl import ARROW_POSITION_END
from umlshapes.lib.ogl import FORMAT_SIZE_TO_CONTENTS

from umlmodel.SDMessage import SDMessage

from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.preferences.UmlPreferences import UmlPreferences


class SD_MESSAGE_TYPE(Enum):
    SYNCHRONOUS_MESSAGE = 'Synchronous Message'


class UmlSDMessage(LineShape, IdentifierMixin):
    def __init__(self, sdMessage: SDMessage, messageType: SD_MESSAGE_TYPE = SD_MESSAGE_TYPE.SYNCHRONOUS_MESSAGE):

        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        self.logger: Logger = getLogger(__name__)
        IdentifierMixin.__init__(self)
        LineShape.__init__(self)

        self._sdMessage:   SDMessage       = sdMessage
        self._messageType: SD_MESSAGE_TYPE = messageType
        self._preferences: UmlPreferences  = UmlPreferences()

        self._messageBackGroundBrush: Brush = Brush(colour=WHITE, style=BRUSHSTYLE_TRANSPARENT)

        self.SetFont(UmlUtils.defaultFont())

        self.SetFormatMode(mode=FORMAT_SIZE_TO_CONTENTS)
        self.AddText(sdMessage.message)

        #
        # TODO:  Support different message type that require different arrow heads and lines
        #
        self.AddArrow(
            type=ARROW_ARROW,
            end=ARROW_POSITION_END,
            size=self._preferences.messageArrowHeadSize
        )
        self.SetPen(UmlUtils.blackSolidPen())
        self.SetBrush(BLACK_BRUSH)      # Required for solid arrow

        self.SetDraggable(True, recursive=True)
        self.MakeLineControlPoints(n=2)
        self._fromLifeline: UmlSDLifeLine = cast(UmlSDLifeLine, None)
        self._toLifeLine:   UmlSDLifeLine = cast(UmlSDLifeLine, None)
        self._fromY: int = 0
        self._toY:   int = 0

    @property
    def fromY(self) -> int:
        return self._fromY

    @fromY.setter
    def fromY(self, newFromY: int):
        self._fromY = newFromY

    @property
    def toY(self) -> int:
        return self._toY

    @toY.setter
    def toY(self, newToY: int):
        self._toY = newToY

    @property
    def sdMessage(self) -> SDMessage:
        """

        Returns: The UML Model SD message
        """
        return self._sdMessage

    def updateMessage(self):
        """
        Update the message
        """
        text: str = self._sdMessage.message
        self.ClearText()
        self.AddText(text)

    def GetBackgroundBrush(self) -> Brush:
        """
        Override default behavior;  So we can see 'through' the message text
        
        Returns:  our precomputed transparent brush
        """
        return self._messageBackGroundBrush

    def __str__(self) -> str:
        return f'UmlSDMessage: `{self._sdMessage.message}`'

    def __repr__(self) -> str:
        return self.__str__()


UmlSDMessages = NewType('UmlSDMessages', List[UmlSDMessage])
