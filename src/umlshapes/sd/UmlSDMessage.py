
from typing import List
from typing import NewType
from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from math import sqrt

from wx import Brush
from wx import ClientDC
from wx import MemoryDC
from wx import Point
from wx import WHITE
from wx import BLACK_BRUSH
from wx import RED_BRUSH
from wx import BRUSHSTYLE_TRANSPARENT

from umlshapes.lib.ogl import OP_ALL
from umlshapes.lib.ogl import ArrowHead
from umlshapes.lib.ogl import ARROW_ARROW
from umlshapes.lib.ogl import ARROW_POSITION_END
from umlshapes.lib.ogl import ARROW_POSITION_START

from umlshapes.lib.ogl import LineShape
from umlshapes.lib.ogl import GetArrowPoints
from umlshapes.lib.ogl import GetPointOnLine

from umlmodel.SDMessage import SDMessage

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.mixins.PubSubMixin import PubSubMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.ControlPointMixin import ControlPointMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.SDMessageLabelPlacement import SDMessageLabelPlacement
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDMessageLabel import UmlSDMessageLabel
from umlshapes.sd.eventhandlers.UmlSDMessageLabelEventHandler import UmlSDMessageLabelEventHandler

from umlshapes.types.Common import NAME_IDX
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


class UmlSDMessage(ControlPointMixin, LineShape, IdentifierMixin, PubSubMixin):

    def __init__(self, sdMessage: SDMessage, umlPubSubEngine: IUmlPubSubEngine, messageType: SDMessageType = SDMessageType.SYNCHRONOUS):

        self.logger: Logger = getLogger(__name__)
        super().__init__(shape=self)

        IdentifierMixin.__init__(self)
        LineShape.__init__(self)
        PubSubMixin.__init__(self)

        self._sdMessage:   SDMessage     = sdMessage
        self._messageType: SDMessageType = messageType
        self._preferences: UmlPreferences  = UmlPreferences()

        self._umlPubSubEngine = umlPubSubEngine
        self._messageBackGroundBrush: Brush = Brush(colour=WHITE, style=BRUSHSTYLE_TRANSPARENT)

        self.SetFont(ResourceUtils.defaultFont())

        self._messageLabel: Optional[UmlSDMessageLabel] = None

        #
        # TODO:  Support different message type that require different arrow heads and lines
        #
        self.AddArrow(
            type=ARROW_ARROW,
            end=ARROW_POSITION_END,
            size=self._preferences.messageArrowHeadSize
        )
        self.SetPen(ResourceUtils.blackSolidPen())
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
    def messageType(self) -> SDMessageType:
        return self._messageType

    @messageType.setter
    def messageType(self, messageType: SDMessageType):
        self._messageType = messageType

    @property
    def messageLabel(self) -> Optional[UmlSDMessageLabel]:
        return self._messageLabel

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
        if self._messageLabel is not None:
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

        if self.Selected() is True:
            if self._messageType == SDMessageType.RETURN:
                self.SetPen(ResourceUtils.redDashedPen())
            else:
                self.SetPen(ResourceUtils.redSolidPen())
            self.SetBrush(RED_BRUSH)
        else:
            if self._messageType == SDMessageType.RETURN:
                self.SetPen(ResourceUtils.blackDashedPen())
            else:
                self.SetPen(ResourceUtils.blackSolidPen())
            self.SetBrush(BLACK_BRUSH)

        super().OnDraw(dc=dc)

    def DrawArrow(self, dc: MemoryDC, arrow: ArrowHead, XOffset: float = 0.0, proportionalOffset: bool = False):
        if self._messageType == SDMessageType.SYNCHRONOUS:
            super().DrawArrow(dc, arrow, XOffset, proportionalOffset)
            return

        lineControlPoints: Optional[List[Point]] = self._lineControlPoints
        if not lineControlPoints or len(lineControlPoints) < 2:
            return

        firstLinePoint:      Point = lineControlPoints[0]
        secondLinePoint:     Point = lineControlPoints[1]
        lastLinePoint:       Point = lineControlPoints[-1]
        secondLastLinePoint: Point = lineControlPoints[-2]

        startPositionX:  int
        startPositionY:  int
        positionOnLineX: float
        positionOnLineY: float

        arrowPosition: int = arrow.GetPosition()
        if arrowPosition == ARROW_POSITION_START:
            realOffset: float = XOffset
            if proportionalOffset:
                totalLength: float = sqrt((secondLinePoint.x - firstLinePoint.x) ** 2 + (secondLinePoint.y - firstLinePoint.y) ** 2)
                realOffset = XOffset * totalLength
            positionOnLineX, positionOnLineY = GetPointOnLine(secondLinePoint.x, secondLinePoint.y, firstLinePoint.x, firstLinePoint.y, realOffset)
            startPositionX = secondLinePoint.x
            startPositionY = secondLinePoint.y
        elif arrowPosition == ARROW_POSITION_END:
            realOffset = XOffset
            if proportionalOffset:
                totalLength = sqrt((secondLastLinePoint.x - lastLinePoint.x) ** 2 + (secondLastLinePoint.y - lastLinePoint.y) ** 2)
                realOffset = XOffset * totalLength
            positionOnLineX, positionOnLineY = GetPointOnLine(secondLastLinePoint.x, secondLastLinePoint.y, lastLinePoint.x, lastLinePoint.y, realOffset)
            startPositionX = secondLastLinePoint.x
            startPositionY = secondLastLinePoint.y
        else:
            super().DrawArrow(dc, arrow, XOffset, proportionalOffset)
            return

        arrowLength: float = arrow.GetSize()
        arrowWidth:  float = arrowLength / 3.0

        tipX:   int
        tipY:   int
        side1X: int
        side1Y: int
        side2X: int
        side2Y: int
        tipX, tipY, side1X, side1Y, side2X, side2Y = GetArrowPoints(
            startPositionX, startPositionY, positionOnLineX, positionOnLineY, arrowLength, arrowWidth
        )

        dc.SetPen(ResourceUtils.redSolidPen() if self.Selected() is True else ResourceUtils.blackSolidPen())
        dc.DrawLine(side1X, side1Y, tipX, tipY)
        dc.DrawLine(side2X, side2Y, tipX, tipY)

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

        lineControlPoints: Optional[List[Point]] = self._lineControlPoints
        if lineControlPoints is not None and len(lineControlPoints) > 2:
            self.Initialise()

        # Do a second time, because one may depend on the other
        endX, endY, otherEndX, otherEndY = self.FindLineEndPoints()
        self.SetEnds(endX, fromY, otherEndX, toY)

        if self._messageLabel is not None:
            self._updateMessageLabelPosition(dc=dc)

    def _updateMessageLabelPosition(self, dc: ClientDC):
        """
        Position the message label according to the user's placement preference mode.

        Args:
            dc: The device context
        """
        lineControlPoints: Optional[List[Point]] = self._lineControlPoints
        if self._messageLabel is None or not lineControlPoints or len(lineControlPoints) < 2:
            return

        startX: int = lineControlPoints[0].x
        endX:   int = lineControlPoints[-1].x
        lineY:  int = lineControlPoints[0].y

        placementMode: SDMessageLabelPlacement = self._preferences.messageLabelPlacement

        targetX: int
        match placementMode:
            case SDMessageLabelPlacement.CENTERED:
                targetX = (startX + endX) // 2
            case SDMessageLabelPlacement.PROPORTIONAL:
                targetX = round(startX + (self._messageLabel.proportionalOffset * (endX - startX)))
            case SDMessageLabelPlacement.FIXED:
                targetX = self._messageLabel.fixedX
            case _:
                targetX = (startX + endX) // 2

        targetY: int = lineY + self._messageLabel.verticalOffset

        self._messageLabel.Move(dc, targetX, targetY)
        topLeftX: int = targetX - (self._messageLabel.size.width // 2)
        topLeftY: int = targetY - (self._messageLabel.size.height // 2)
        self._messageLabel.position = UmlPosition(x=topLeftX, y=topLeftY)

    def _createLinkName(self) -> UmlSDMessageLabel:

        labelX, labelY = self.GetLabelPosition(position=NAME_IDX)
        return self._createMessageLabel(x=labelX, y=labelY, text=self.sdMessage.message)

    def _createMessageLabel(self, x: int, y: int, text: str) -> UmlSDMessageLabel:

        assert text is not None, 'Developer error'

        umlSDMessageLabel: UmlSDMessageLabel = UmlSDMessageLabel(label=text)
        umlSDMessageLabel.proportionalOffset = 0.5
        umlSDMessageLabel.fixedX = x
        umlSDMessageLabel.verticalOffset = 0

        topLeftX: int = x - (umlSDMessageLabel.size.width // 2)
        topLeftY: int = y - (umlSDMessageLabel.size.height // 2)
        umlSDMessageLabel.position = UmlPosition(x=topLeftX, y=topLeftY)
        #
        # Maybe not necessary, but let's be consistent
        #
        self._children.append(umlSDMessageLabel)
        self._setupMessageLabel(umlSDMessageLabel)

        return umlSDMessageLabel

    def _setupMessageLabel(self, umlSDMessageLabel: UmlSDMessageLabel):
        """

        Args:
            umlSDMessageLabel:
        """
        from umlshapes.frames.UmlFrame import UmlFrame

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
