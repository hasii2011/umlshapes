
from typing import cast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlShapeGenre
from dataclasses import dataclass
from typing import Optional

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import MOD_CMD
from wx import ID_OK
from wx import CURSOR_DEFAULT
from wx import Cursor

from wx.lib.ogl import ControlPoint
from wx.lib.ogl import ShapeEvtHandler

from umlmodel.SDMessage import SDMessage

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.dialogs.DlgEditSDMessage import Message
from umlshapes.dialogs.DlgEditSDMessage import MessageList
from umlshapes.dialogs.DlgEditSDMessage import DlgEditSDMessage

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.preferences.Defaults import MIN_REFLEXIVE_MESSAGE_WIDTH
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage

from umlshapes.types.DeltaXY import DeltaXY


@dataclass
class MessageDragContext:
    """
    Encapsulates transient mouse drag and sizing state for sequence diagram messages.

    Rationale:
        1. Unified Lifecycle: Coordinates and indices
           (fromY, toY, mouseX, mouseY, loopWidth, control point index) share an identical

           * lifecycle—instantiated together on mouse-down,
           * consumed during mouse-drag, and
           * discarded on mouse-up.
        2. Moving these transient attributes from the
           event handler into a dedicated context ensures all drag fields are strictly
           non-optional (int and bool) and eliminates compound '
        3. Atomic Cleanup: Discarding the context via 'self._dragContext = None' prevents
           partial state leakage across distinct drag operations without needing to reset
           multiple loosely-coupled instance variables.
    """
    initialFromY:            int
    initialToY:              int
    initialMouseX:           int
    initialMouseY:           int
    initialLoopWidth:        int
    activeControlPointIndex: int  = -1
    isDirectEndpointDrag:    bool = False


class UmlSDMessageEventHandler(UmlBaseEventHandler):
    def __init__(self, umlSDMessage: UmlSDMessage, previousEventHandler: ShapeEvtHandler):
        """

        Args:
            umlSDMessage:         The UML SD Message we are managing
            previousEventHandler: The previous event handler in order to correctly chain
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSDMessage)

        self._umlSDMessage: UmlSDMessage   = umlSDMessage
        self._layoutEngine: SDLayoutEngine = SDLayoutEngine()
        self._preferences:  UmlPreferences = UmlPreferences()

        self._dragContext: Optional[MessageDragContext] = None

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides UmlBaseEventHandler.OnBeginDragLeft to record initial Y coordinates
        and selection state before vertical dragging begins.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        if not self._umlSDMessage.Selected():
            umlFrame: UmlFrame = self._umlSDMessage.umlFrame
            dc: ClientDC = ClientDC(umlFrame)
            umlFrame.PrepareDC(dc)
            if keys != MOD_CMD:
                self._unSelectAllShapesOnCanvas(self._umlSDMessage, umlFrame, dc)
            self._umlSDMessage.Select(True, dc)
            self.umlPubSubEngine.sendMessage(
                messageType=UmlMessageType.UML_SHAPE_SELECTED,
                frameId=umlFrame.id,
                umlShape=self._umlSDMessage
            )
            umlFrame.refresh()

        isDirectEndpointDrag: bool = False
        freeX: int
        if self._umlSDMessage.isLostMessage is True and len(self._umlSDMessage.lineControlPoints) >= 2:
            freeX = self._umlSDMessage.lineControlPoints[-1].x
            if abs(x - freeX) <= 15:
                isDirectEndpointDrag = True
        elif self._umlSDMessage.isFoundMessage is True and len(self._umlSDMessage.lineControlPoints) >= 2:
            freeX = self._umlSDMessage.lineControlPoints[0].x
            if abs(x - freeX) <= 15:
                isDirectEndpointDrag = True

        self._dragContext = MessageDragContext(
            initialFromY=self._umlSDMessage.fromY,
            initialToY=self._umlSDMessage.toY,
            initialMouseX=x,
            initialMouseY=y,
            initialLoopWidth=self._umlSDMessage.loopWidth,
            isDirectEndpointDrag=isDirectEndpointDrag
        )

        if not isDirectEndpointDrag:
            self._umlSDMessage.moveMaster = True
            self._saveSelectedShapesInitialPositions()
            self._umlSDMessage.umlFrame.markShapeAsMoved(umlShape=cast('UmlShapeGenre', self._umlSDMessage))

        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides UmlBaseEventHandler.OnDragLeft to move the message to the nearest
        snapped vertical time step and publish vertical deltaXY to any other selected shapes.

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        if self._dragContext is not None and self._dragContext.isDirectEndpointDrag:
            if self._umlSDMessage.isLostMessage:
                self._resizeLostMessageEndpoint(x=x)
            elif self._umlSDMessage.isFoundMessage:
                self._resizeFoundMessageEndpoint(x=x)
            return

        self._umlSDMessage.moveMaster = True
        previousFromY: int = self._umlSDMessage.fromY

        targetY: int
        if self._dragContext is not None:
            deltaY: int = y - self._dragContext.initialMouseY
            targetY = self._dragContext.initialFromY + deltaY
        else:
            targetY = y
        self._snapMessageToTimeStep(targetY=targetY)

        actualDeltaY: int = self._umlSDMessage.fromY - previousFromY
        if actualDeltaY != 0:
            self.umlPubSubEngine.sendMessage(
                messageType=UmlMessageType.SHAPE_MOVING,
                frameId=self._umlSDMessage.umlFrame.id,
                deltaXY=DeltaXY(deltaX=0, deltaY=actualDeltaY)
            )

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides UmlBaseEventHandler.OnEndDragLeft to finalize message placement at
        the snapped time step, update other selected shapes, and notify frame of modification.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        if self._dragContext is not None and self._dragContext.isDirectEndpointDrag:
            if self._umlSDMessage.isLostMessage:
                self._resizeLostMessageEndpoint(x=x)
            elif self._umlSDMessage.isFoundMessage:
                self._resizeFoundMessageEndpoint(x=x)
            self._indicateFrameModified()
            self._dragContext = None
            super(UmlBaseEventHandler, self).OnEndDragLeft(x, y, keys, attachment)
            return

        previousFromY: int = self._umlSDMessage.fromY

        targetY: int
        if self._dragContext is not None:
            deltaY: int = y - self._dragContext.initialMouseY
            targetY = self._dragContext.initialFromY + deltaY
        else:
            targetY = y
        self._snapMessageToTimeStep(targetY=targetY)

        actualDeltaY: int = self._umlSDMessage.fromY - previousFromY
        if actualDeltaY != 0:
            self.umlPubSubEngine.sendMessage(
                messageType=UmlMessageType.SHAPE_MOVING,
                frameId=self._umlSDMessage.umlFrame.id,
                deltaXY=DeltaXY(deltaX=0, deltaY=actualDeltaY)
            )

        if self._dragContext is not None and self._umlSDMessage.fromY != self._dragContext.initialFromY:
            self._indicateFrameModified()

        self._umlSDMessage.moveMaster = False
        self._dragContext = None

        umlFrame: UmlFrame = self._umlSDMessage.umlFrame
        from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand
        from umlshapes.frames.ShapeMoveInfo import InitialPositions

        if len(self._initialPositions) > 0:
            shapesMovedCommand: ShapesMovedCommand = ShapesMovedCommand(
                umlFrame=umlFrame,
                movedShapes=umlFrame.movedShapes,
                initialPositions=self._initialPositions
            )
            umlFrame.commandProcessor.Submit(command=shapesMovedCommand, storeIt=True)
            self._debugDumpMovedShapes(umlFrame)
            umlFrame.clearMovedShapes()
            self._initialPositions = InitialPositions({})
            umlFrame.refresh()

        super(UmlBaseEventHandler, self).OnEndDragLeft(x, y, keys, attachment)

    def OnSizingBeginDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides ShapeEvtHandler.OnSizingBeginDragLeft to record initial coordinates
        when dragging via line control points.

        Args:
            pt:
            x:
            y:
            keys:
            attachment:
        """
        activeControlPointIndex: int = -1
        if self._umlSDMessage.isReflexiveMessage or self._umlSDMessage.isLostMessage or self._umlSDMessage.isFoundMessage:
            controlPoints: list[ControlPoint] = self._umlSDMessage.GetControlPoints()
            if pt in controlPoints:
                activeControlPointIndex = controlPoints.index(pt)

        self._dragContext = MessageDragContext(
            initialFromY=self._umlSDMessage.fromY,
            initialToY=self._umlSDMessage.toY,
            initialMouseX=x,
            initialMouseY=y,
            initialLoopWidth=self._umlSDMessage.loopWidth,
            activeControlPointIndex=activeControlPointIndex
        )

        super().OnSizingBeginDragLeft(pt, x, y, keys, attachment)

        umlFrame: Optional[UmlFrame] = self._umlSDMessage.umlFrame
        if umlFrame is not None:
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            umlFrame.SetCursor(defaultCursor)
            pt._oldCursor = defaultCursor

    def OnSizingDragLeft(self, pt: ControlPoint, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides ShapeEvtHandler.OnSizingDragLeft to handle dragging via line control points.

        Args:
            pt:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        activeIdx: int = -1
        if self._dragContext is not None:
            activeIdx = self._dragContext.activeControlPointIndex
        if self._umlSDMessage.isReflexiveMessage is True and activeIdx != -1:
            if activeIdx == 2 or activeIdx == 3:
                isCorner: bool = (activeIdx == 2)
                self._resizeOrRepositionReturnMessage(x=x, y=y, isCorner=isCorner)
            elif activeIdx == 0 or activeIdx == 1:
                isCorner = (activeIdx == 1)
                self._resizeOrRepositionCallMessage(x=x, y=y, isCorner=isCorner)
        elif self._umlSDMessage.isLostMessage is True and activeIdx == 1:
            self._resizeLostMessageEndpoint(x=x)
        elif self._umlSDMessage.isFoundMessage is True and activeIdx == 0:
            self._resizeFoundMessageEndpoint(x=x)
        else:
            self.OnDragLeft(draw=draw, x=x, y=y, keys=keys, attachment=attachment)

        umlFrame: Optional[UmlFrame] = self._umlSDMessage.umlFrame
        if umlFrame is not None:
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            umlFrame.SetCursor(defaultCursor)

    def OnSizingEndDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides ShapeEvtHandler.OnSizingEndDragLeft to handle drag completion via line control points.

        Args:
            pt:
            x:
            y:
            keys:
            attachment:
        """
        activeIdx: int = -1
        if self._dragContext is not None:
            activeIdx = self._dragContext.activeControlPointIndex
        if self._umlSDMessage.isReflexiveMessage is True and activeIdx != -1:
            if activeIdx == 2 or activeIdx == 3:
                isCorner: bool = (activeIdx == 2)
                self._resizeOrRepositionReturnMessage(x=x, y=y, isCorner=isCorner)
            elif activeIdx == 0 or activeIdx == 1:
                isCorner = (activeIdx == 1)
                self._resizeOrRepositionCallMessage(x=x, y=y, isCorner=isCorner)

            hasChanged: bool = False
            if self._dragContext is not None:
                if self._umlSDMessage.fromY != self._dragContext.initialFromY:
                    hasChanged = True
                if self._umlSDMessage.toY != self._dragContext.initialToY:
                    hasChanged = True
                if self._umlSDMessage.loopWidth != self._dragContext.initialLoopWidth:
                    hasChanged = True

            if hasChanged:
                self._indicateFrameModified()
        elif (self._umlSDMessage.isLostMessage is True and activeIdx == 1) or (self._umlSDMessage.isFoundMessage is True and activeIdx == 0):
            self._indicateFrameModified()
        else:
            self.OnEndDragLeft(x=x, y=y, keys=keys, attachment=attachment)

        self._dragContext = None
        super().OnSizingEndDragLeft(pt, x, y, keys, attachment)

        umlFrame: Optional[UmlFrame] = self._umlSDMessage.umlFrame
        if umlFrame is not None:
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            umlFrame.SetCursor(defaultCursor)

    def OnLeftClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides UmlBaseEventHandler.OnLeftClick to log click coordinates and select the message.

        Args:
            x:              The x-coordinate we will pass along
            y:              The y-coordinate we will pass along
            keys:
            attachment:
        """
        self.logger.info(f'xy: ({x},{y})')
        super().OnLeftClick(x, y, keys, attachment)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Overrides ShapeEvtHandler.OnLeftDoubleClick to open the edit message dialog.
        """
        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlSDMessage: UmlSDMessage = self._umlSDMessage
        umlFrame:     UmlFrame     = umlSDMessage.umlFrame
        modelClass:   SDMessage    = umlSDMessage.sdMessage

        messages: MessageList = MessageList([Message('message1'), Message('message2')])

        with DlgEditSDMessage(parent=umlFrame, sdMessage=modelClass, messages=messages) as dlg:
            if dlg.ShowModal() == ID_OK:
                umlSDMessage.sdMessage = dlg.sdMessage
                dc: ClientDC = ClientDC(umlFrame)
                umlFrame.PrepareDC(dc)
                umlSDMessage.updateMessageLabelPosition(dc=dc)
                self._indicateFrameModified()
                umlFrame.refresh()

    def _resizeLostMessageEndpoint(self, x: int):
        startX: int = self._umlSDMessage.lineControlPoints[0].x
        newSpanX: int = x - startX
        if abs(newSpanX) >= 20:
            y: int = self._umlSDMessage.fromY
            self._umlSDMessage.SetEnds(startX, y, x, y)
            umlFrame: Optional[UmlFrame] = self._umlSDMessage.umlFrame
            if umlFrame is not None:
                dc: ClientDC = ClientDC(umlFrame)
                umlFrame.PrepareDC(dc)
                self._umlSDMessage.updateMessageLabelPosition(dc=dc)
                self._umlSDMessage.ResetControlPoints()
                umlFrame.refresh()

    def _resizeFoundMessageEndpoint(self, x: int):
        endX: int = self._umlSDMessage.lineControlPoints[-1].x
        newSpanX: int = endX - x
        if abs(newSpanX) >= 20:
            y: int = self._umlSDMessage.toY
            self._umlSDMessage.SetEnds(x, y, endX, y)
            umlFrame: Optional[UmlFrame] = self._umlSDMessage.umlFrame
            if umlFrame is not None:
                dc: ClientDC = ClientDC(umlFrame)
                umlFrame.PrepareDC(dc)
                self._umlSDMessage.updateMessageLabelPosition(dc=dc)
                self._umlSDMessage.ResetControlPoints()
                umlFrame.refresh()

    def _updateReflexiveLoopWidth(self, startLifeLine: UmlSDLifeLine, x: int, isCorner: bool):
        """
        Update the reflexive loop width if dragging a corner control point.

        Args:
            startLifeLine: Origin lifeline shape
            x:             Cursor X coordinate
            isCorner:      True if dragging a corner control point
        """
        if isCorner:
            lifeLineX: int = round(startLifeLine.GetX())
            rawWidth: int = x - lifeLineX
            newLoopWidth: int = max(MIN_REFLEXIVE_MESSAGE_WIDTH, rawWidth)
            self._umlSDMessage.loopWidth = newLoopWidth

    def _finalizeReflexiveResize(self, startLifeLine: UmlSDLifeLine, newFromY: int, newToY: int, isCorner: bool):
        """
        Apply auto-grow or clamping constraints, update reflexive message geometry,
        and refresh the frame.

        Args:
            startLifeLine: Origin lifeline shape
            newFromY:      Proposed fromY coordinate
            newToY:        Proposed toY coordinate
            isCorner:      True if dragging a corner control point
        """
        headerBottomY:      int = startLifeLine.rectangle.top
        minTimeStepSpacing: int = self._layoutEngine.parameters.timeStepHeight
        minFromY:           int = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=0)
        umlFrame:           UmlFrame = self._umlSDMessage.umlFrame

        if self._preferences.autoGrowLifeLines:
            neededHeight: int = (newToY - headerBottomY) + self._layoutEngine.parameters.bottomPadding
            self._umlSDMessage.growLifeLinesIfNeeded(neededHeight=neededHeight, umlFrame=umlFrame)
        else:
            maxTimeStepIndex: int = max(
                0,
                (startLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding)
                // minTimeStepSpacing
            )
            maxToY: int = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=maxTimeStepIndex)
            newToY = min(newToY, maxToY)
            if newToY <= newFromY:
                newFromY = max(minFromY, newToY - minTimeStepSpacing)

        hasGeometryChanged: bool = False
        if newFromY != self._umlSDMessage.fromY or newToY != self._umlSDMessage.toY:
            hasGeometryChanged = True
        if isCorner:
            hasGeometryChanged = True

        if hasGeometryChanged:
            self._umlSDMessage.fromY = newFromY
            self._umlSDMessage.toY = newToY
            dc: ClientDC = ClientDC(umlFrame)
            umlFrame.PrepareDC(dc)
            self._umlSDMessage.OnMoveLink(dc=dc)
            self._umlSDMessage.ResetControlPoints()
            umlFrame.refresh()

    def _resizeOrRepositionReturnMessage(self, x: int, y: int, isCorner: bool):
        """
        Resize vertical span and optionally reposition reflexive message when dragging
        the return branch control point (endpoint or corner).

        Args:
            x:        Cursor X coordinate
            y:        Cursor Y coordinate
            isCorner: True if dragging a corner control point
        """
        startLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if startLifeLine is None:
            return

        self._updateReflexiveLoopWidth(startLifeLine=startLifeLine, x=x, isCorner=isCorner)

        headerBottomY: int = startLifeLine.rectangle.top
        minTimeStepSpacing: int = self._layoutEngine.parameters.timeStepHeight

        rawTimeStepIndex: int = self._layoutEngine.computeNearestTimeStepIndex(
            headerBottomY=headerBottomY,
            targetY=y
        )
        candidateToY: int = self._layoutEngine.computeTimeStepY(
            headerBottomY=headerBottomY,
            timeStepIndex=rawTimeStepIndex
        )

        minFromY: int = self._layoutEngine.computeTimeStepY(
            headerBottomY=headerBottomY,
            timeStepIndex=0
        )
        currentFromY: int = self._umlSDMessage.fromY
        newFromY: int
        newToY: int

        if candidateToY > currentFromY:
            newFromY = currentFromY
            newToY = candidateToY
        else:
            newToY = max(minFromY + minTimeStepSpacing, candidateToY)
            newFromY = newToY - minTimeStepSpacing

        self._finalizeReflexiveResize(
            startLifeLine=startLifeLine,
            newFromY=newFromY,
            newToY=newToY,
            isCorner=isCorner
        )

    def _resizeOrRepositionCallMessage(self, x: int, y: int, isCorner: bool):
        """
        Resize vertical span and optionally reposition reflexive message when dragging
        the call branch control point (endpoint or corner).

        Args:
            x:        Cursor X coordinate
            y:        Cursor Y coordinate
            isCorner: True if dragging a corner control point
        """
        startLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if startLifeLine is None:
            return

        self._updateReflexiveLoopWidth(startLifeLine=startLifeLine, x=x, isCorner=isCorner)

        headerBottomY: int = startLifeLine.rectangle.top
        minTimeStepSpacing: int = self._layoutEngine.parameters.timeStepHeight

        rawTimeStepIndex: int = self._layoutEngine.computeNearestTimeStepIndex(
            headerBottomY=headerBottomY,
            targetY=y
        )
        candidateFromY: int = self._layoutEngine.computeTimeStepY(
            headerBottomY=headerBottomY,
            timeStepIndex=rawTimeStepIndex
        )

        minFromY: int = self._layoutEngine.computeTimeStepY(
            headerBottomY=headerBottomY,
            timeStepIndex=0
        )
        currentToY: int = self._umlSDMessage.toY
        newFromY: int
        newToY: int

        if candidateFromY < currentToY:
            newFromY = max(minFromY, candidateFromY)
            newToY = currentToY
        else:
            newFromY = candidateFromY
            newToY = candidateFromY + minTimeStepSpacing

        self._finalizeReflexiveResize(
            startLifeLine=startLifeLine,
            newFromY=newFromY,
            newToY=newToY,
            isCorner=isCorner
        )

    def _computeMessageSpan(self) -> int:
        """
        Compute the vertical span between the message endpoints.
        """
        span: int
        if self._dragContext is not None:
            span = self._dragContext.initialToY - self._dragContext.initialFromY
        else:
            span = self._umlSDMessage.toY - self._umlSDMessage.fromY
        return span

    def _computeAutoGrowEndpoints(self, headerBottomY: int, rawTimeStepIndex: int, span: int, umlFrame: UmlFrame) -> tuple[int, int]:
        """
        Compute snapped message endpoints and expand lifelines if necessary.

        Args:
            headerBottomY:    Bottom Y coordinate of the lifeline header
            rawTimeStepIndex: Unbounded timeStep index based on cursor position
            span:             Vertical span between fromY and toY
            umlFrame:         The UML frame

        Returns:
            Tuple of (snappedFromY, snappedToY)
        """
        timeStepIndex: int = max(0, rawTimeStepIndex)
        snappedFromY:  int = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=timeStepIndex)
        snappedToY:    int = snappedFromY + span
        neededHeight:  int = (snappedToY - headerBottomY) + self._layoutEngine.parameters.bottomPadding
        self._umlSDMessage.growLifeLinesIfNeeded(neededHeight=neededHeight, umlFrame=umlFrame)
        return snappedFromY, snappedToY

    def _computeBoundedEndpoints(self, referenceLifeLine: UmlSDLifeLine, headerBottomY: int, rawTimeStepIndex: int, span: int) -> tuple[int, int]:
        """
        Compute snapped message endpoints bounded within current lifeline length.

        Args:
            referenceLifeLine: Reference lifeline shape
            headerBottomY:    Bottom Y coordinate of the lifeline header
            rawTimeStepIndex: Unbounded timeStep index based on cursor position
            span:             Vertical span between fromY and toY

        Returns:
            Tuple of (snappedFromY, snappedToY)
        """
        maxTimeStepIndex: int = max(
            0,
            (referenceLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding - span)
            // self._layoutEngine.parameters.timeStepHeight
        )
        timeStepIndex: int = max(0, min(rawTimeStepIndex, maxTimeStepIndex))
        snappedFromY:  int = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=timeStepIndex)
        snappedToY:    int = snappedFromY + span
        return snappedFromY, snappedToY

    def _applyMessageEndpoints(self, snappedFromY: int, snappedToY: int, umlFrame: UmlFrame):
        """
        Apply new endpoints to the message, synchronize execution, and refresh frame.

        Args:
            snappedFromY: Snapped Y coordinate for the start of the message
            snappedToY:   Snapped Y coordinate for the end of the message
            umlFrame:     The UML frame
        """
        if snappedFromY != self._umlSDMessage.fromY or snappedToY != self._umlSDMessage.toY:
            dc: ClientDC = ClientDC(umlFrame)
            umlFrame.PrepareDC(dc)
            self._umlSDMessage.setVerticalEndpoints(fromY=snappedFromY, toY=snappedToY, dc=dc)
            umlFrame.refresh()

    def _snapMessageToTimeStep(self, targetY: int):
        """
        Compute nearest valid timeStep Y and update message endpoints and label.

        Args:
            targetY: Raw cursor Y coordinate
        """
        referenceLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if referenceLifeLine is None:
            referenceLifeLine = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetTo())
        if referenceLifeLine is None:
            return

        headerBottomY:    int = referenceLifeLine.rectangle.top
        rawTimeStepIndex: int = self._layoutEngine.computeNearestTimeStepIndex(headerBottomY=headerBottomY, targetY=targetY)
        span:             int = self._computeMessageSpan()
        umlFrame:         UmlFrame = self._umlSDMessage.umlFrame

        snappedFromY: int
        snappedToY:   int
        if self._preferences.autoGrowLifeLines:
            snappedFromY, snappedToY = self._computeAutoGrowEndpoints(
                headerBottomY=headerBottomY,
                rawTimeStepIndex=rawTimeStepIndex,
                span=span,
                umlFrame=umlFrame
            )
        else:
            snappedFromY, snappedToY = self._computeBoundedEndpoints(
                referenceLifeLine=referenceLifeLine,
                headerBottomY=headerBottomY,
                rawTimeStepIndex=rawTimeStepIndex,
                span=span
            )

        self._applyMessageEndpoints(snappedFromY=snappedFromY, snappedToY=snappedToY, umlFrame=umlFrame)
