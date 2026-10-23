
from typing import cast
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
from umlshapes.lib.ogl import ControlPoint
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

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType

from umlshapes.sd.SDMessageLabelPlacement import SDMessageLabelPlacement
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDMessageLabel import UmlSDMessageLabel
from umlshapes.sd.eventhandlers.UmlSDMessageLabelEventHandler import UmlSDMessageLabelEventHandler

from umlshapes.types.Common import NAME_IDX
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.sd.UmlSDExecution import UmlSDExecution
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


LineControlPoints = NewType('LineControlPoints', List[Point])


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
        if self.isReflexiveMessage:
            self.MakeLineControlPoints(n=4)
        else:
            self.MakeLineControlPoints(n=2)
        self.SetSensitivityFilter(sens=OP_ALL)

        self._fromY: int = 0
        self._toY:   int = 0

        self._loopWidth: Optional[int] = None

        self._relativeFromY: int = 0
        self._relativeToY:   int = 0

        self._initialised: bool = False
        self._lineControlPoints: LineControlPoints = LineControlPoints(self._lineControlPoints)
        self._execution: Optional['UmlSDExecution'] = None

    @property
    def isReflexiveMessage(self) -> bool:
        if self._from is not None and self._to is not None:
            if self._from == self._to:
                return True
        if self._sdMessage.source is not None and self._sdMessage.destination is not None:
            if self._sdMessage.source == self._sdMessage.destination:
                return True
        return False

    def _ensureLineControlPoints(self):
        pointCount: int
        if self.isReflexiveMessage:
            pointCount = 4
        else:
            pointCount = 2

        if len(self.lineControlPoints) != pointCount:
            self.MakeLineControlPoints(n=pointCount)

    @property
    def loopWidth(self) -> int:
        if self._loopWidth is not None:
            return self._loopWidth
        return self._preferences.reflexiveMessageWidth

    @loopWidth.setter
    def loopWidth(self, loopWidth: int):
        self._loopWidth = loopWidth

    @property
    def controlPoints(self) -> list[ControlPoint]:
        return self._controlPoints

    @property
    def lineControlPoints(self) -> LineControlPoints:
        return self._lineControlPoints

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
        self._sdMessage.sourceY = newFromY

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
        self._sdMessage.destinationY = newToY

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

    def GetControlPoints(self) -> list[ControlPoint]:
        return self._controlPoints

    def MakeControlPoints(self):

        if self._canvas is not None and len(self.lineControlPoints) > 0:
            firstPoint: Point = self.lineControlPoints[0]
            lastPoint:  Point = self.lineControlPoints[-1]

            self._makeLineControlPoint(point=firstPoint, controlPointType=UmlLineControlPointType.FROM_ENDPOINT)
            for point in self.lineControlPoints[1:-1]:
                self._makeLineControlPoint(point=point, controlPointType=UmlLineControlPointType.LINE_POINT)
            self._makeLineControlPoint(point=lastPoint, controlPointType=UmlLineControlPointType.TO_ENDPOINT)

    def setReflexiveMessagePoints(self, lifeLineX: int, fromY: int, toY: int):

        self._ensureLineControlPoints()
        loopWidth: int = self.loopWidth

        if len(self.lineControlPoints) >= 4:

            self.lineControlPoints[0] = Point(lifeLineX, fromY)
            self.lineControlPoints[1] = Point(lifeLineX + loopWidth, fromY)
            self.lineControlPoints[2] = Point(lifeLineX + loopWidth, toY)
            self.lineControlPoints[3] = Point(lifeLineX, toY)

            self._initialised = True

        self._xpos = lifeLineX + (loopWidth // 2)
        self._ypos = (fromY + toY) // 2

    @property
    def execution(self) -> Optional['UmlSDExecution']:
        return self._execution

    @execution.setter
    def execution(self, execution: Optional['UmlSDExecution']):
        self._execution = execution

    def Draggable(self) -> bool:
        """
        Override base LineShape behavior (which hardcodes False) so sequence diagram
        messages can be dragged vertically to adjust time steps.
        """
        return True

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

        if self.Selected() is True:
            dc.SetPen(ResourceUtils.redSolidPen())
        else:
            dc.SetPen(ResourceUtils.blackSolidPen())
        dc.DrawLine(side1X, side1Y, tipX, tipY)
        dc.DrawLine(side2X, side2Y, tipX, tipY)

    def OnMoveLink(self, dc: ClientDC, moveControlPoints: bool = True):
        """
        Copied from original but modified to use the original Y positions.
        Handles both standard inter-instance messages and self-referential message loops.

        Args:
            dc:
            moveControlPoints:
        """
        if not self._from or not self._to:
            return

        self._ensureLineControlPoints()

        fromY: int = self._computeAbsoluteY(umlSDLifeLine=self.GetFrom(), relativeY=self._relativeFromY)
        toY:   int = self._computeAbsoluteY(umlSDLifeLine=self.GetTo(), relativeY=self._relativeToY)

        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        fromLifeLine: UmlSDLifeLine = cast(UmlSDLifeLine, self.GetFrom())
        toLifeLine:   UmlSDLifeLine = cast(UmlSDLifeLine, self.GetTo())

        fromExecution: Optional['UmlSDExecution'] = fromLifeLine.getExecutionAtY(fromY)

        if self.isReflexiveMessage:
            startX: int
            if fromExecution is not None:
                startX = round(fromExecution.GetX() + (fromExecution.GetWidth() / 2.0))
            else:
                startX = round(fromLifeLine.GetX())

            loopWidth: int = self.loopWidth

            if len(self.lineControlPoints) >= 4:
                self.lineControlPoints[0] = Point(startX, fromY)
                self.lineControlPoints[1] = Point(startX + loopWidth, fromY)
                self.lineControlPoints[2] = Point(startX + loopWidth, toY)
                self.lineControlPoints[3] = Point(startX, toY)
                self._initialised = True

            self._xpos = startX + (loopWidth // 2)
            self._ypos = (fromY + toY) // 2
            self.Move(dc, self._xpos, self._ypos)
        else:
            toExecution: Optional['UmlSDExecution'] = toLifeLine.getExecutionAtY(toY)

            endX:      int = round(fromLifeLine.GetX())
            otherEndX: int = round(toLifeLine.GetX())

            if fromLifeLine.GetX() < toLifeLine.GetX():
                if fromExecution is not None:
                    endX = round(fromExecution.GetX() + (fromExecution.GetWidth() / 2.0))
                if toExecution is not None:
                    otherEndX = round(toExecution.GetX() - (toExecution.GetWidth() / 2.0))
            else:
                if fromExecution is not None:
                    endX = round(fromExecution.GetX() - (fromExecution.GetWidth() / 2.0))
                if toExecution is not None:
                    otherEndX = round(toExecution.GetX() + (toExecution.GetWidth() / 2.0))

            self.SetEnds(endX, fromY, otherEndX, toY)

            if len(self.lineControlPoints) > 2:
                self.Initialise()

            self.SetEnds(endX, fromY, otherEndX, toY)

        if self._messageLabel is not None:
            self._updateMessageLabelPosition(dc=dc)

    def _updateMessageLabelPosition(self, dc: ClientDC):
        """
        Position the message label according to the user's placement preference mode.

        Args:
            dc: The device context
        """
        if self._messageLabel is None or len(self.lineControlPoints) < 2:
            return

        startX: int = self.lineControlPoints[0].x
        endX:   int = self.lineControlPoints[-1].x
        lineY:  int = self.lineControlPoints[0].y

        placementMode: SDMessageLabelPlacement = self._preferences.messageLabelPlacement

        targetX: int
        targetY: int
        if self.isReflexiveMessage:
            loopX: int = self.lineControlPoints[1].x
            targetX, targetY = self._computeReflexiveMessageLabelCenter(
                startX=startX,
                loopX=loopX,
                lineY=lineY,
                placementMode=placementMode
            )
        else:
            targetX, targetY = self._computeStandardMessageLabelCenter(
                startX=startX,
                endX=endX,
                lineY=lineY,
                placementMode=placementMode
            )

        self._messageLabel.Move(dc, targetX, targetY)
        topLeftX: int = targetX - (self._messageLabel.size.width // 2)
        topLeftY: int = targetY - (self._messageLabel.size.height // 2)

        self._messageLabel.position = UmlPosition(x=topLeftX, y=topLeftY)

    def _computeMessageLabelX(self, leftX: int, rightX: int, placementMode: SDMessageLabelPlacement) -> int:
        """
        Compute the target center X coordinate for the message label.

        Args:
            leftX:         Left boundary X coordinate
            rightX:        Right boundary X coordinate
            placementMode: Label placement preference mode

        Returns:
            The calculated center X coordinate
        """
        assert self._messageLabel is not None, 'Developer error'

        targetX: int
        # PyCharm false-positive: PyCharm erroneously marks subsequent Enum case branches
        # as unreachable in match/case statements (PY-52844).
        # noinspection PyUnreachableCode
        match placementMode:
            case SDMessageLabelPlacement.CENTERED:
                targetX = (leftX + rightX) // 2
            case SDMessageLabelPlacement.PROPORTIONAL:
                targetX = round(leftX + (self._messageLabel.proportionalOffset * (rightX - leftX)))
            case SDMessageLabelPlacement.FIXED:
                targetX = self._messageLabel.fixedX
            case _:
                targetX = (leftX + rightX) // 2

        return targetX

    def _computeReflexiveMessageLabelCenter(self, startX: int, loopX: int, lineY: int, placementMode: SDMessageLabelPlacement) -> tuple[int, int]:
        """
        Compute the center (targetX, targetY) for a reflexive message label.

        Args:
            startX:         Left X of the reflexive loop
            loopX:          Right X of the reflexive loop
            lineY:          Y coordinate of the upper branch
            placementMode:  Label placement preference mode

        Returns:
            Tuple of (targetX, targetY)
        """
        assert self._messageLabel is not None, 'Developer error'

        targetX: int = self._computeMessageLabelX(leftX=startX, rightX=loopX, placementMode=placementMode)
        targetY: int = lineY - (self._messageLabel.size.height // 2) - 2 + self._messageLabel.verticalOffset

        return targetX, targetY

    def _computeStandardMessageLabelCenter(self, startX: int, endX: int, lineY: int, placementMode: SDMessageLabelPlacement) -> tuple[int, int]:
        """
        Compute the center (targetX, targetY) for a standard message label.

        Args:
            startX:         Source lifeline X
            endX:           Destination lifeline X
            lineY:          Message line Y
            placementMode:  Label placement preference mode

        Returns:
            Tuple of (targetX, targetY)
        """
        assert self._messageLabel is not None, 'Developer error'

        targetX: int = self._computeMessageLabelX(leftX=startX, rightX=endX, placementMode=placementMode)
        targetY: int = lineY + self._messageLabel.verticalOffset

        return targetX, targetY

    def _createLinkName(self) -> UmlSDMessageLabel:

        labelX: int
        labelY: int
        if self.isReflexiveMessage and len(self.lineControlPoints) >= 2:
            startX: int = self.lineControlPoints[0].x
            loopX:  int = self.lineControlPoints[1].x
            lineY:  int = self.lineControlPoints[0].y
            labelX = (startX + loopX) // 2
            labelY = lineY
        else:
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

    def _makeLineControlPoint(self, point: Point, controlPointType: UmlLineControlPointType):
        umlControlPointSize: int = self._preferences.controlPointSize

        control: UmlLineControlPoint = UmlLineControlPoint(
            umlFrame=self._canvas,
            umlLink=self,
            controlPointType=controlPointType,
            size=umlControlPointSize,
            x=point.x,
            y=point.y,
        )
        control._point = point
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

    def __str__(self) -> str:
        return f'UmlSDMessage: `{self._sdMessage.message}`'

    def __repr__(self) -> str:
        return self.__str__()


UmlSDMessages = NewType('UmlSDMessages', List[UmlSDMessage])
