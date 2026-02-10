
from typing import cast
from typing import List
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from enum import Enum

from wx import Brush
from wx import ClientDC
from wx import MemoryDC
from wx import WHITE
from wx import BLACK_BRUSH
from wx import BRUSHSTYLE_TRANSPARENT

from umlshapes.lib.ogl import OP_ALL
from umlshapes.lib.ogl import LineShape
from umlshapes.lib.ogl import ARROW_ARROW
from umlshapes.lib.ogl import ARROW_POSITION_END

from umlmodel.SDMessage import SDMessage

from umlshapes.UmlUtils import UmlUtils
from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.LabelType import LabelType

from umlshapes.mixins.PubSubMixin import PubSubMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.ControlPointMixin import ControlPointMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.UmlSDMessageLabel import UmlSDMessageLabel
from umlshapes.sd.eventhandlers.UmlSDMessageLabelEventHandler import UmlSDMessageLabelEventHandler

from umlshapes.types.Common import NAME_IDX
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame


class SD_MESSAGE_TYPE(Enum):
    SYNCHRONOUS_MESSAGE = 'Synchronous Message'


class UmlSDMessage(ControlPointMixin, LineShape, IdentifierMixin, PubSubMixin):

    def __init__(self, sdMessage: SDMessage, umlPubSubEngine: IUmlPubSubEngine, messageType: SD_MESSAGE_TYPE = SD_MESSAGE_TYPE.SYNCHRONOUS_MESSAGE):

        self.logger: Logger = getLogger(__name__)
        super().__init__(shape=self)

        IdentifierMixin.__init__(self)
        LineShape.__init__(self)
        PubSubMixin.__init__(self)

        self._sdMessage:   SDMessage       = sdMessage
        self._messageType: SD_MESSAGE_TYPE = messageType
        self._preferences: UmlPreferences  = UmlPreferences()

        self._umlPubSubEngine = umlPubSubEngine
        self._messageBackGroundBrush: Brush = Brush(colour=WHITE, style=BRUSHSTYLE_TRANSPARENT)

        self.SetFont(UmlUtils.defaultFont())

        self._messageLabel: UmlSDMessageLabel = cast(UmlSDMessageLabel, None)

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
        self.SetSensitivityFilter(sens=OP_ALL)

        self._fromY: int = 0
        self._toY:   int = 0

        self._relativeFromY: int = 0
        self._relativeToY:   int = 0

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    @property
    def fromY(self) -> int:
        return self._fromY

    @fromY.setter
    def fromY(self, newFromY: int):
        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        sdLifeLine: UmlSDLifeLine = self.GetFrom()
        if sdLifeLine:
            self._relativeFromY = newFromY - sdLifeLine.rectangle.top

        self._fromY = newFromY

    @property
    def toY(self) -> int:
        return self._toY

    @toY.setter
    def toY(self, newToY: int):
        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        sdLifeLine: UmlSDLifeLine = self.GetTo()
        if sdLifeLine:
            self._relativeToY = newToY - sdLifeLine.rectangle.top
        self._toY = newToY

    @property
    def sdMessage(self) -> SDMessage:
        """

        Returns: The UML Model SD message
        """
        return self._sdMessage

    @sdMessage.setter
    def sdMessage(self, sdMessage: SDMessage):
        """

        Args:
            sdMessage:  The updated model class
        """
        self._sdMessage = sdMessage
        self.updateMessage()

    def updateMessage(self):
        """
        Update the message
        """
        self._messageLabel.label = self._sdMessage.message

    def GetBackgroundBrush(self) -> Brush:
        """
        Override default behavior;  So we can see 'through' the message text
        
        Returns:  our precomputed transparent brush
        """
        return self._messageBackGroundBrush

    def OnDraw(self, dc: MemoryDC):
        if self._messageLabel is None:
            self._messageLabel = self._createLinkName()
            self._setupMessageLabel(umlSDMessageLabel=self._messageLabel)

        if self.Selected() is True:
            self.SetPen(UmlUtils.redSolidPen())
        else:
            self.SetPen(UmlUtils.blackSolidPen())

        super().OnDraw(dc=dc)

    def OnMoveLink(self, dc: ClientDC, moveControlPoints: bool = True):
        """
        Copied from original but modified to use the original Y positions;  Did
        not copy the self link code;

        TODO: revisit when we support self links

        Args:
            dc:
            moveControlPoints:
        """
        if not self._from or not self._to:
            return

        # Do each end - nothing in the middle. User has to move other points
        # manually if necessary
        endX, endY, otherEndX, otherEndY = self.FindLineEndPoints()

        fromY: int = self._computeAbsoluteY(umlSDLifeLine=self.GetFrom(), relativeY=self._relativeFromY)
        toY:   int = self._computeAbsoluteY(umlSDLifeLine=self.GetTo(), relativeY=self._relativeToY)
        self.SetEnds(endX, fromY, otherEndX, toY)

        if len(self._lineControlPoints) > 2:
            self.Initialise()

        # Do a second time, because one may depend on the other
        endX, endY, otherEndX, otherEndY = self.FindLineEndPoints()
        self.SetEnds(endX, fromY, otherEndX, toY)

    def _createLinkName(self) -> UmlSDMessageLabel:

        labelX, labelY = self.GetLabelPosition(position=NAME_IDX)
        return self._createMessageLabel(x=labelX, y=labelY, text=self.sdMessage.message, labelType=LabelType.ASSOCIATION_NAME)

    def _createMessageLabel(self, x: int, y: int, text: str, labelType: LabelType) -> UmlSDMessageLabel:

        assert text is not None, 'Developer error'

        umlSDMessageLabel: UmlSDMessageLabel = UmlSDMessageLabel(label=text, labelType=labelType)

        umlSDMessageLabel.position = UmlPosition(x=x, y=y)
        #
        # Maybe not necessary, but let's be consistent
        #
        self._children.append(umlSDMessageLabel)
        self._setupMessageLabel(umlSDMessageLabel)

        return umlSDMessageLabel

    def _setupMessageLabel(self, umlSDMessageLabel):
        """

        Args:
            umlSDMessageLabel:
        """
        umlFrame: UmlFrame = self.GetCanvas()
        umlSDMessageLabel.SetCanvas(umlFrame)
        umlSDMessageLabel.parent = self

        diagram: UmlDiagram = umlFrame.umlDiagram
        diagram.AddShape(umlSDMessageLabel)

        self._setMessageLabelEventHandler(umlSDMessageLabel)

    def _setMessageLabelEventHandler(self, umlSDMessageLabel: UmlSDMessageLabel):
        """

        Args:
            umlSDMessageLabel:
        """
        eventHandler: UmlSDMessageLabelEventHandler = UmlSDMessageLabelEventHandler(previousEventHandler=umlSDMessageLabel.GetEventHandler())

        eventHandler.SetShape(umlSDMessageLabel)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine

        umlSDMessageLabel.SetEventHandler(eventHandler)

    def _computeAbsoluteY(self, umlSDLifeLine: 'UmlSDLifeLine', relativeY: int) -> int:
        return umlSDLifeLine.rectangle.top + relativeY

    def __str__(self) -> str:
        return f'UmlSDMessage: `{self._sdMessage.message}`'

    def __repr__(self) -> str:
        return self.__str__()


UmlSDMessages = NewType('UmlSDMessages', List[UmlSDMessage])
