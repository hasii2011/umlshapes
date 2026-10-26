
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
from umlshapes.sd.UmlSDCombinedFragment import UmlSDCombinedFragment

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDInstance import UmlSDInstance

MIN_FRAGMENT_WIDTH: int = 100
MIN_FRAGMENT_HEIGHT: int = 40

HANDLE_TOP_LEFT: int = 0
HANDLE_TOP_MIDDLE: int = 1
HANDLE_TOP_RIGHT: int = 2
HANDLE_MIDDLE_RIGHT: int = 3
HANDLE_BOTTOM_RIGHT: int = 4
HANDLE_BOTTOM_MIDDLE: int = 5
HANDLE_BOTTOM_LEFT: int = 6
HANDLE_MIDDLE_LEFT: int = 7


class UmlSDCombinedFragmentEventHandler(UmlBaseEventHandler):
    """
    Event handler for sequence diagram combined fragments (alt, opt, loop, etc.).
    Manages interactive selection, dragging with vertical time step snapping,
    and 8-point boundary resizing snapped to participant time steps.
    """

    def __init__(
        self,
        umlSDCombinedFragment: UmlSDCombinedFragment,
        umlPubSubEngine: IUmlPubSubEngine,
        previousEventHandler: ShapeEvtHandler
    ):
        """
        Initialize the combined fragment event handler.

        Args:
            umlSDCombinedFragment: The combined fragment shape being managed.
            umlPubSubEngine:       The pub-sub notification engine.
            previousEventHandler:  The previous event handler in the chain.
        """

        super().__init__(previousEventHandler=previousEventHandler, shape=umlSDCombinedFragment)

        self.logger: Logger = getLogger(__name__)

        self._umlSDCombinedFragment: UmlSDCombinedFragment = umlSDCombinedFragment
        self._umlPubSubEngine:       IUmlPubSubEngine      = umlPubSubEngine
        self._preferences:           UmlPreferences        = UmlPreferences()
        self._layoutEngine:          SDLayoutEngine        = SDLayoutEngine()

        self._dragStartX: Optional[int] = None
        self._dragStartY: Optional[int] = None

        self._initialFragmentX: Optional[float] = None
        self._initialFragmentY: Optional[float] = None

        self._activeHandleIndex: Optional[int]   = None
        self._initialLeft:       Optional[float] = None
        self._initialRight:      Optional[float] = None
        self._initialTop:        Optional[float] = None
        self._initialBottom:     Optional[float] = None

    def OnLeftClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Handle left-click on the combined fragment to toggle selection state.

        Args:
            x: Click X position.
            y: Click Y position.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        fragment: UmlSDCombinedFragment = self._umlSDCombinedFragment
        umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], fragment.GetCanvas())
        if umlFrame is None:
            return

        dc: ClientDC = ClientDC(umlFrame)
        umlFrame.PrepareDC(dc)

        isCurrentlySelected: bool = fragment.Selected()
        if keys != MOD_CMD:
            self._unSelectAllShapesOnCanvas(fragment, umlFrame, dc)

        newSelectionState: bool = not isCurrentlySelected
        fragment.Select(newSelectionState, dc)

        if self._umlPubSubEngine is not None:
            if newSelectionState:
                self._umlPubSubEngine.sendMessage(
                    messageType=UmlMessageType.UML_SHAPE_SELECTED,
                    frameId=umlFrame.id,
                    umlShape=fragment
                )

        umlFrame.refresh()

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record initial coordinates when dragging begins and ensure selection.

        Args:
            x: Initial drag X position.
            y: Initial drag Y position.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        fragment: UmlSDCombinedFragment = self._umlSDCombinedFragment
        self._dragStartX = x
        self._dragStartY = y
        self._initialFragmentX = fragment.GetX()
        self._initialFragmentY = fragment.GetY()

        if not fragment.Selected():
            umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], fragment.GetCanvas())
            if umlFrame is not None:
                dc: ClientDC = ClientDC(umlFrame)
                umlFrame.PrepareDC(dc)
                if keys != MOD_CMD:
                    self._unSelectAllShapesOnCanvas(fragment, umlFrame, dc)
                fragment.Select(True, dc)
                if self._umlPubSubEngine is not None:
                    self._umlPubSubEngine.sendMessage(
                        messageType=UmlMessageType.UML_SHAPE_SELECTED,
                        frameId=umlFrame.id,
                        umlShape=fragment
                    )
                umlFrame.refresh()

        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Move fragment during drag, snapping vertical position to discrete time steps.

        Args:
            draw: Whether to draw intermediate feedback.
            x: Current drag X coordinate.
            y: Current drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        if self._dragStartX is None:
            return
        if self._dragStartY is None:
            return
        if self._initialFragmentX is None:
            return
        if self._initialFragmentY is None:
            return

        fragment: UmlSDCombinedFragment = self._umlSDCombinedFragment
        deltaX: int = x - self._dragStartX
        deltaY: int = y - self._dragStartY

        newCenterX: float = self._initialFragmentX + deltaX

        halfHeight: float = fragment.GetHeight() / 2.0
        candidateTopY: int = round((self._initialFragmentY + deltaY) - halfHeight)
        headerBottomY: int = self._getHeaderBottomY()

        snappedTopY: int = self._layoutEngine.computeNearestTimeStepY(
            headerBottomY=headerBottomY,
            targetY=candidateTopY
        )
        newCenterY: float = snappedTopY + halfHeight

        fragment.setPosition(newCenterX, newCenterY)
        fragment.ResetControlPoints()

        umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], fragment.GetCanvas())
        if umlFrame is not None:
            umlFrame.refresh()

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize dragging motion and reset drag state variables.

        Args:
            x: Final drag X coordinate.
            y: Final drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        self.OnDragLeft(draw=False, x=x, y=y, keys=keys, attachment=attachment)
        self._dragStartX = None
        self._dragStartY = None
        self._initialFragmentX = None
        self._initialFragmentY = None

    def OnSizingBeginDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record initial fragment bounds when a sizing handle drag begins.

        Args:
            pt: The control point handle being dragged.
            x: Initial drag X coordinate.
            y: Initial drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        controlPoints: list[ControlPoint] = self._umlSDCombinedFragment.getControlPoints()
        if pt in controlPoints:
            self._activeHandleIndex = controlPoints.index(pt)
        else:
            self._activeHandleIndex = None

        fragment: UmlSDCombinedFragment = self._umlSDCombinedFragment
        halfWidth: float = fragment.GetWidth() / 2.0
        halfHeight: float = fragment.GetHeight() / 2.0

        self._initialLeft = fragment.GetX() - halfWidth
        self._initialRight = fragment.GetX() + halfWidth
        self._initialTop = fragment.GetY() - halfHeight
        self._initialBottom = fragment.GetY() + halfHeight

    def OnSizingDragLeft(self, pt: ControlPoint, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Adjust fragment boundaries during handle drag, snapping top/bottom to time steps.

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
        if self._initialLeft is None:
            return
        if self._initialRight is None:
            return
        if self._initialTop is None:
            return
        if self._initialBottom is None:
            return

        handleIndex: int = self._activeHandleIndex
        newLeft: float = self._initialLeft
        newRight: float = self._initialRight
        newTop: float = self._initialTop
        newBottom: float = self._initialBottom

        # Handle horizontal sizing
        if handleIndex == HANDLE_TOP_LEFT or handleIndex == HANDLE_MIDDLE_LEFT or handleIndex == HANDLE_BOTTOM_LEFT:
            maxLeft: float = self._initialRight - MIN_FRAGMENT_WIDTH
            if x > maxLeft:
                newLeft = maxLeft
            else:
                newLeft = float(x)
        elif handleIndex == HANDLE_TOP_RIGHT or handleIndex == HANDLE_MIDDLE_RIGHT or handleIndex == HANDLE_BOTTOM_RIGHT:
            minRight: float = self._initialLeft + MIN_FRAGMENT_WIDTH
            if x < minRight:
                newRight = minRight
            else:
                newRight = float(x)

        # Handle vertical sizing snapped to time steps
        headerBottomY: int = self._getHeaderBottomY()
        minHeight: int = max(MIN_FRAGMENT_HEIGHT, self._layoutEngine.parameters.timeStepHeight)

        if handleIndex == HANDLE_TOP_LEFT or handleIndex == HANDLE_TOP_MIDDLE or handleIndex == HANDLE_TOP_RIGHT:
            snappedTop: int = self._layoutEngine.computeNearestTimeStepY(
                headerBottomY=headerBottomY,
                targetY=y
            )
            maxTop: int = round(self._initialBottom - minHeight)
            if snappedTop > maxTop:
                newTop = float(maxTop)
            else:
                newTop = float(snappedTop)
        elif handleIndex == HANDLE_BOTTOM_LEFT or handleIndex == HANDLE_BOTTOM_MIDDLE or handleIndex == HANDLE_BOTTOM_RIGHT:
            snappedBottom: int = self._layoutEngine.computeNearestTimeStepY(
                headerBottomY=headerBottomY,
                targetY=y
            )
            minBottom: int = round(self._initialTop + minHeight)
            if snappedBottom < minBottom:
                newBottom = float(minBottom)
            else:
                newBottom = float(snappedBottom)

        newWidth: float = newRight - newLeft
        newHeight: float = newBottom - newTop
        newCenterX: float = (newLeft + newRight) / 2.0
        newCenterY: float = (newTop + newBottom) / 2.0

        fragment: UmlSDCombinedFragment = self._umlSDCombinedFragment
        fragment.SetSize(newWidth, newHeight)
        fragment.setPosition(newCenterX, newCenterY)
        fragment.ResetControlPoints()

        umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], fragment.GetCanvas())
        if umlFrame is not None:
            umlFrame.refresh()

    def OnSizingEndDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize interactive boundary sizing drag.

        Args:
            pt: The control point handle released.
            x: Final drag X coordinate.
            y: Final drag Y coordinate.
            keys: Modifier keys bitmask.
            attachment: Attachment point identifier.
        """
        self.OnSizingDragLeft(pt=pt, draw=False, x=x, y=y, keys=keys, attachment=attachment)
        self._activeHandleIndex = None
        self._initialLeft = None
        self._initialRight = None
        self._initialTop = None
        self._initialBottom = None

    def _getHeaderBottomY(self) -> int:
        """
        Determine the baseline header bottom Y from participant lifelines on the canvas.
        Falls back to default startY if no lifelines exist.
        """
        umlFrame: Optional[UmlFrame] = cast(Optional[UmlFrame], self._umlSDCombinedFragment.GetCanvas())
        if umlFrame is not None:
            if hasattr(umlFrame, 'getSDInstances'):
                instances: list['UmlSDInstance'] = getattr(umlFrame, 'getSDInstances')()
                if len(instances) > 0:
                    return round(instances[0].umlSDLifeLine.rectangle.top)
        return self._layoutEngine.parameters.startY
