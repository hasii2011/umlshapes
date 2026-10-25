from typing import Optional
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import MOD_CMD
from wx import ClientDC

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.UmlSDExecution import EXECUTION_BOTTOM_HANDLE_INDEX
from umlshapes.sd.UmlSDExecution import EXECUTION_TOP_HANDLE_INDEX
from umlshapes.sd.UmlSDExecution import UmlSDExecution

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

MIN_EXECUTION_DURATION_PIXELS: int = 20


class UmlSDExecutionEventHandler(UmlBaseEventHandler):
    """
    Event handler for sequence diagram execution specification bars.
    Manages selection, delegation of participant drag, and interactive vertical
    duration resizing snapped to diagram time steps.
    """

    def __init__(
        self,
        umlSDExecution: UmlSDExecution,
        umlPubSubEngine: IUmlPubSubEngine,
        previousEventHandler: ShapeEvtHandler
    ):
        """
        Initialize the execution specification event handler.

        Args:
            umlSDExecution: The execution shape being managed.
            umlPubSubEngine: The pub-sub notification engine.
            previousEventHandler: The previous event handler in the chain.
        """
        super().__init__(previousEventHandler=previousEventHandler, shape=umlSDExecution)
        self.logger: Logger = getLogger(__name__)
        self._umlSDExecution: UmlSDExecution = umlSDExecution
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._preferences: UmlPreferences = UmlPreferences()
        self._layoutEngine: SDLayoutEngine = SDLayoutEngine()
        self._activeHandleIndex: Optional[int] = None
        self._initialStartY: Optional[int] = None
        self._initialEndY: Optional[int] = None

    def OnLeftClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Handle left-click on the execution bar to toggle selection state.

        Args:
            x: Click X position.
            y: Click Y position.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        execution: UmlSDExecution = self._umlSDExecution
        umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], execution.GetCanvas())
        if umlFrame is None:
            return

        dc: ClientDC = ClientDC(umlFrame)
        umlFrame.PrepareDC(dc)

        if keys != MOD_CMD:
            self._unSelectAllShapesOnCanvas(execution, umlFrame, dc)

        isCurrentlySelected: bool = execution.Selected()
        newSelectionState: bool = not isCurrentlySelected
        execution.Select(newSelectionState, dc)

        if self._umlPubSubEngine is not None:
            if newSelectionState:
                self._umlPubSubEngine.sendMessage(
                    messageType=UmlMessageType.UML_SHAPE_SELECTED,
                    frameId=umlFrame.id,
                    umlShape=execution
                )

        umlFrame.refresh()

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate horizontal drag start to the parent lifeline's participant instance.

        Args:
            x: Drag X coordinate.
            y: Drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        lifeLine: Optional['UmlSDLifeLine'] = self._umlSDExecution.lifeLine
        if lifeLine is not None:
            if lifeLine.umlSDInstance is not None:
                parentHandler: Optional[ShapeEvtHandler] = lifeLine.umlSDInstance.GetEventHandler()
                if parentHandler is not None:
                    parentHandler.OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate horizontal drag motion to the parent lifeline's participant instance.

        Args:
            draw: Whether to draw intermediate feedback.
            x: Current drag X coordinate.
            y: Current drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        lifeLine: Optional['UmlSDLifeLine'] = self._umlSDExecution.lifeLine
        if lifeLine is not None:
            if lifeLine.umlSDInstance is not None:
                parentHandler: Optional[ShapeEvtHandler] = lifeLine.umlSDInstance.GetEventHandler()
                if parentHandler is not None:
                    parentHandler.OnDragLeft(draw, x, y, keys, attachment)

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate horizontal drag completion to the parent lifeline's participant instance.

        Args:
            x: Final drag X coordinate.
            y: Final drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        lifeLine: Optional['UmlSDLifeLine'] = self._umlSDExecution.lifeLine
        if lifeLine is not None:
            if lifeLine.umlSDInstance is not None:
                parentHandler: Optional[ShapeEvtHandler] = lifeLine.umlSDInstance.GetEventHandler()
                if parentHandler is not None:
                    parentHandler.OnEndDragLeft(x, y, keys, attachment)

    def OnSizingBeginDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record initial execution duration state when sizing handle drag begins.

        Args:
            pt: The control point handle being dragged.
            x: Initial drag X coordinate.
            y: Initial drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        controlPoints: list[ControlPoint] = self._umlSDExecution.GetControlPoints()
        if pt in controlPoints:
            self._activeHandleIndex = controlPoints.index(pt)
        else:
            self._activeHandleIndex = None

        self._initialStartY = self._umlSDExecution.startY
        self._initialEndY = self._umlSDExecution.endY
        self.logger.debug(f'OnSizingBeginDragLeft: activeHandleIndex={self._activeHandleIndex}')

    def OnSizingDragLeft(self, pt: ControlPoint, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Adjust execution duration during handle drag, snapping to the nearest time step.

        Args:
            pt: The control point handle being dragged.
            draw: Whether to draw intermediate feedback.
            x: Current drag X coordinate.
            y: Current drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        if self._activeHandleIndex is None:
            return

        lifeLine: Optional['UmlSDLifeLine'] = self._umlSDExecution.lifeLine
        if lifeLine is None:
            return

        headerBottomY: int = round(lifeLine.rectangle.top)
        lifelineBottomY: int = round(lifeLine.rectangle.bottom)
        snappedY: int = self._layoutEngine.computeNearestTimeStepY(headerBottomY=headerBottomY, targetY=y)

        if self._activeHandleIndex == EXECUTION_TOP_HANDLE_INDEX:
            if snappedY < headerBottomY:
                snappedY = headerBottomY
            maxStartY: int = self._umlSDExecution.endY - MIN_EXECUTION_DURATION_PIXELS
            if snappedY > maxStartY:
                snappedY = maxStartY
            self._umlSDExecution.startY = snappedY
        elif self._activeHandleIndex == EXECUTION_BOTTOM_HANDLE_INDEX:
            minEndY: int = self._umlSDExecution.startY + MIN_EXECUTION_DURATION_PIXELS
            if snappedY < minEndY:
                snappedY = minEndY
            if snappedY > lifelineBottomY:
                snappedY = lifelineBottomY
            self._umlSDExecution.endY = snappedY

        lifeLine.recalculateNestingLevels()
        lifeLine.recomputeExecutionsGeometry()

        umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], self._umlSDExecution.GetCanvas())
        if umlFrame is not None:
            umlFrame.refresh()

    def OnSizingEndDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize execution duration sizing drag.

        Args:
            pt: The control point handle released.
            x: Final drag X coordinate.
            y: Final drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        self.OnSizingDragLeft(pt=pt, draw=False, x=x, y=y, keys=keys, attachment=attachment)
        self._activeHandleIndex = None
        self._initialStartY = None
        self._initialEndY = None
