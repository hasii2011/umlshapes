from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import OK
from wx import CURSOR_DEFAULT
from wx import Cursor

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import ShapeEvtHandler

from umlmodel.SDMessage import SDMessage

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.dialogs.DlgEditSDMessage import Message
from umlshapes.dialogs.DlgEditSDMessage import MessageList
from umlshapes.dialogs.DlgEditSDMessage import DlgEditSDMessage

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.preferences.Defaults import MIN_REFLEXIVE_MESSAGE_WIDTH
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage


class UmlSDMessageEventHandler(UmlBaseEventHandler):
    def __init__(self, umlSDMessage: UmlSDMessage, umlPubSubEngine: IUmlPubSubEngine, previousEventHandler: ShapeEvtHandler):
        """

        Args:
            umlSDMessage:         The UML SD Message we are managing
            umlPubSubEngine:      The pub sub engine
            previousEventHandler: The previous event handler in order to correctly chain
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSDMessage)

        self._umlSDMessage:    UmlSDMessage     = umlSDMessage
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._layoutEngine:    SDLayoutEngine   = SDLayoutEngine()
        self._preferences:     UmlPreferences   = UmlPreferences()
        self._initialFromY:            Optional[int] = None
        self._initialToY:              Optional[int] = None
        self._initialMouseY:           Optional[int] = None
        self._initialMouseX:           Optional[int] = None
        self._initialLoopWidth:        Optional[int] = None
        self._activeControlPointIndex: Optional[int] = None

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record initial Y coordinates before dragging begins.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        self._initialFromY = self._umlSDMessage.fromY
        self._initialToY = self._umlSDMessage.toY
        self._initialMouseY = y
        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Move the entire message to the nearest snapped vertical time step.

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        targetY: int
        if self._initialMouseY is not None and self._initialFromY is not None:
            deltaY: int = y - self._initialMouseY
            targetY = self._initialFromY + deltaY
        else:
            targetY = y
        self._snapMessageToTimeStep(targetY=targetY)

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize message placement at the snapped time step and notify frame of modification.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        targetY: int
        if self._initialMouseY is not None and self._initialFromY is not None:
            deltaY: int = y - self._initialMouseY
            targetY = self._initialFromY + deltaY
        else:
            targetY = y
        self._snapMessageToTimeStep(targetY=targetY)
        if self._initialFromY is not None and self._umlSDMessage.fromY != self._initialFromY:
            self._indicateFrameModified()

        self._initialFromY = None
        self._initialToY = None
        self._initialMouseY = None
        super().OnEndDragLeft(x, y, keys, attachment)

    def OnSizingBeginDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record initial coordinates when dragging via line control points.

        Args:
            pt:
            x:
            y:
            keys:
            attachment:
        """
        self._initialFromY = self._umlSDMessage.fromY
        self._initialToY = self._umlSDMessage.toY
        self._initialMouseY = y
        self._initialMouseX = x
        self._initialLoopWidth = self._umlSDMessage.loopWidth

        if self._umlSDMessage.isReflexiveMessage is True:
            controlPoints: list[ControlPoint] = self._umlSDMessage.GetControlPoints()
            if pt in controlPoints:
                self._activeControlPointIndex = controlPoints.index(pt)
            else:
                self._activeControlPointIndex = None
        else:
            self._activeControlPointIndex = None

        super().OnSizingBeginDragLeft(pt, x, y, keys, attachment)

        diagramCanvas: Optional[UmlFrame] = self._umlSDMessage.umlFrame
        if diagramCanvas is not None:
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            diagramCanvas.SetCursor(defaultCursor)
            pt._oldCursor = defaultCursor

    def OnSizingDragLeft(self, pt: ControlPoint, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Handle dragging via line control points.

        Args:
            pt:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        if self._umlSDMessage.isReflexiveMessage is True and self._activeControlPointIndex is not None:
            if self._activeControlPointIndex == 2 or self._activeControlPointIndex == 3:
                isCorner: bool = (self._activeControlPointIndex == 2)
                self._resizeOrRepositionReturnMessage(x=x, y=y, isCorner=isCorner)
            elif self._activeControlPointIndex == 0 or self._activeControlPointIndex == 1:
                isCorner = (self._activeControlPointIndex == 1)
                self._resizeOrRepositionCallMessage(x=x, y=y, isCorner=isCorner)
        else:
            self.OnDragLeft(draw=draw, x=x, y=y, keys=keys, attachment=attachment)

        diagramCanvas: Optional[UmlFrame] = self._umlSDMessage.umlFrame
        if diagramCanvas is not None:
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            diagramCanvas.SetCursor(defaultCursor)

    def OnSizingEndDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Handle drag completion via line control points.

        Args:
            pt:
            x:
            y:
            keys:
            attachment:
        """
        if self._umlSDMessage.isReflexiveMessage is True and self._activeControlPointIndex is not None:
            if self._activeControlPointIndex == 2 or self._activeControlPointIndex == 3:
                isCorner: bool = (self._activeControlPointIndex == 2)
                self._resizeOrRepositionReturnMessage(x=x, y=y, isCorner=isCorner)
            elif self._activeControlPointIndex == 0 or self._activeControlPointIndex == 1:
                isCorner = (self._activeControlPointIndex == 1)
                self._resizeOrRepositionCallMessage(x=x, y=y, isCorner=isCorner)

            hasChanged: bool = False
            if self._initialFromY is not None and self._umlSDMessage.fromY != self._initialFromY:
                hasChanged = True
            if self._initialToY is not None and self._umlSDMessage.toY != self._initialToY:
                hasChanged = True
            if self._initialLoopWidth is not None and self._umlSDMessage.loopWidth != self._initialLoopWidth:
                hasChanged = True

            if hasChanged is True:
                self._indicateFrameModified()
        else:
            self.OnEndDragLeft(x=x, y=y, keys=keys, attachment=attachment)

        self._activeControlPointIndex = None
        self._initialFromY = None
        self._initialToY = None
        self._initialMouseY = None
        self._initialMouseX = None
        self._initialLoopWidth = None
        super().OnSizingEndDragLeft(pt, x, y, keys, attachment)

        diagramCanvas: Optional[UmlFrame] = self._umlSDMessage.umlFrame
        if diagramCanvas is not None:
            defaultCursor: Cursor = Cursor(CURSOR_DEFAULT)
            diagramCanvas.SetCursor(defaultCursor)

    def _resizeOrRepositionReturnMessage(self, x: int, y: int, isCorner: bool):
        """
        Resize vertical span and optionally reposition reflexive message when dragging
        the return branch control point (endpoint or corner).
        """
        startLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if startLifeLine is None:
            return

        lifeLineX: int = round(startLifeLine.GetX())
        if isCorner is True:
            rawWidth: int = x - lifeLineX
            newLoopWidth: int = max(MIN_REFLEXIVE_MESSAGE_WIDTH, rawWidth)
            self._umlSDMessage.loopWidth = newLoopWidth

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

        canvas: UmlFrame = self._umlSDMessage.umlFrame
        if self._preferences.autoGrowLifeLines is True:
            neededHeight: int = (newToY - headerBottomY) + self._layoutEngine.parameters.bottomPadding
            if neededHeight > startLifeLine.size.height:
                if self._preferences.uniformLifeLineLength is True:
                    if hasattr(canvas, 'setAllLifeLinesLength') is True:
                        canvas.setAllLifeLinesLength(neededHeight)
                else:
                    startSDInstance: UmlSDInstance | None = startLifeLine.umlSDInstance
                    if startSDInstance is not None:
                        startSDInstance.setLifeLineLength(neededHeight)
        else:
            maxTimeStepIndex: int = max(
                0,
                (startLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding)
                // minTimeStepSpacing
            )
            maxToY: int = self._layoutEngine.computeTimeStepY(
                headerBottomY=headerBottomY,
                timeStepIndex=maxTimeStepIndex
            )
            newToY = min(newToY, maxToY)
            if newToY <= newFromY:
                newFromY = max(minFromY, newToY - minTimeStepSpacing)

        hasGeometryChanged: bool = False
        if newFromY != self._umlSDMessage.fromY or newToY != self._umlSDMessage.toY:
            hasGeometryChanged = True
        if isCorner is True:
            hasGeometryChanged = True

        if hasGeometryChanged is True:
            self._umlSDMessage.fromY = newFromY
            self._umlSDMessage.toY = newToY
            dc: ClientDC = ClientDC(canvas)
            canvas.PrepareDC(dc)
            self._umlSDMessage.OnMoveLink(dc=dc)
            self._umlSDMessage.ResetControlPoints()
            canvas.refresh()

    def _resizeOrRepositionCallMessage(self, x: int, y: int, isCorner: bool):
        """
        Resize vertical span and optionally reposition reflexive message when dragging
        the call branch control point (endpoint or corner).
        """
        startLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if startLifeLine is None:
            return

        lifeLineX: int = round(startLifeLine.GetX())
        if isCorner is True:
            rawWidth: int = x - lifeLineX
            newLoopWidth: int = max(MIN_REFLEXIVE_MESSAGE_WIDTH, rawWidth)
            self._umlSDMessage.loopWidth = newLoopWidth

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

        canvas: UmlFrame = self._umlSDMessage.umlFrame
        if self._preferences.autoGrowLifeLines is True:
            neededHeight: int = (newToY - headerBottomY) + self._layoutEngine.parameters.bottomPadding
            if neededHeight > startLifeLine.size.height:
                if self._preferences.uniformLifeLineLength is True:
                    if hasattr(canvas, 'setAllLifeLinesLength') is True:
                        canvas.setAllLifeLinesLength(neededHeight)
                else:
                    startSDInstance: UmlSDInstance | None = startLifeLine.umlSDInstance
                    if startSDInstance is not None:
                        startSDInstance.setLifeLineLength(neededHeight)
        else:
            maxTimeStepIndex: int = max(
                0,
                (startLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding)
                // minTimeStepSpacing
            )
            maxToY: int = self._layoutEngine.computeTimeStepY(
                headerBottomY=headerBottomY,
                timeStepIndex=maxTimeStepIndex
            )
            if newToY > maxToY:
                newToY = maxToY
                newFromY = max(minFromY, newToY - minTimeStepSpacing)

        hasGeometryChanged: bool = False
        if newFromY != self._umlSDMessage.fromY or newToY != self._umlSDMessage.toY:
            hasGeometryChanged = True
        if isCorner is True:
            hasGeometryChanged = True

        if hasGeometryChanged is True:
            self._umlSDMessage.fromY = newFromY
            self._umlSDMessage.toY = newToY
            dc: ClientDC = ClientDC(canvas)
            canvas.PrepareDC(dc)
            self._umlSDMessage.OnMoveLink(dc=dc)
            self._umlSDMessage.ResetControlPoints()
            canvas.refresh()

    def _snapMessageToTimeStep(self, targetY: int):
        """
        Compute nearest valid timeStep Y and update message endpoints and label.

        Args:
            targetY: Raw cursor Y coordinate
        """
        startLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if startLifeLine is None:
            return

        headerBottomY:    int = startLifeLine.rectangle.top
        rawTimeStepIndex: int = self._layoutEngine.computeNearestTimeStepIndex(headerBottomY=headerBottomY, targetY=targetY)

        span: int = 0
        if self._initialToY is not None and self._initialFromY is not None:
            span = self._initialToY - self._initialFromY
        else:
            span = self._umlSDMessage.toY - self._umlSDMessage.fromY

        timeStepIndex: int
        snappedFromY:  int
        snappedToY:    int
        canvas: UmlFrame = self._umlSDMessage.umlFrame
        if self._preferences.autoGrowLifeLines:
            timeStepIndex = max(0, rawTimeStepIndex)
            snappedFromY = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=timeStepIndex)
            snappedToY = snappedFromY + span
            neededHeight: int = (snappedToY - headerBottomY) + self._layoutEngine.parameters.bottomPadding
            destLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetTo())
            currentStartHeight: int = startLifeLine.size.height
            currentDestHeight:  int = 0
            if destLifeLine is not None:
                currentDestHeight = destLifeLine.size.height
            if (neededHeight > currentStartHeight) or (neededHeight > currentDestHeight):
                if self._preferences.uniformLifeLineLength:
                    if hasattr(canvas, 'setAllLifeLinesLength'):
                        canvas.setAllLifeLinesLength(neededHeight)
                else:
                    startSDInstance: UmlSDInstance | None = startLifeLine.umlSDInstance
                    if startSDInstance is not None:
                        startSDInstance.setLifeLineLength(neededHeight)
                    if destLifeLine is not None and destLifeLine != startLifeLine:
                        destSDInstance: UmlSDInstance | None = destLifeLine.umlSDInstance
                        if destSDInstance is not None:
                            destSDInstance.setLifeLineLength(neededHeight)
        else:
            maxTimeStepIndex: int = max(
                0,
                (startLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding - span)
                // self._layoutEngine.parameters.timeStepHeight
            )
            timeStepIndex = max(0, min(rawTimeStepIndex, maxTimeStepIndex))
            snappedFromY = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=timeStepIndex)
            snappedToY = snappedFromY + span

        if snappedFromY != self._umlSDMessage.fromY or snappedToY != self._umlSDMessage.toY:
            self._umlSDMessage.fromY = snappedFromY
            self._umlSDMessage.toY = snappedToY
            dc: ClientDC = ClientDC(canvas)
            canvas.PrepareDC(dc)
            self._umlSDMessage.OnMoveLink(dc=dc)
            self._umlSDMessage.ResetControlPoints()
            canvas.refresh()

    def OnLeftClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """

        Args:
            x:              The x-coordinate we will pass along
            y:              The y-coordinate we will pass along
            keys:
            attachment:
        """
        self.logger.info(f'xy: ({x},{y})')
        super().OnLeftClick(x, y, keys, attachment)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlSDMessage: UmlSDMessage = self._umlSDMessage
        umlFrame:     UmlFrame     = umlSDMessage.umlFrame
        modelClass:   SDMessage    = umlSDMessage.sdMessage

        messages: MessageList = MessageList([Message('message1'), Message('message2')])

        with DlgEditSDMessage(parent=umlFrame, sdMessage=modelClass, messages=messages) as dlg:
            if dlg.ShowModal() == OK:
                umlSDMessage.sdMessage = dlg.sdMessage
                umlFrame.refresh()
