
from typing import Optional
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import ClientDC

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.sd.UmlSDMessageLabel import UmlSDMessageLabel
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDMessage import UmlSDMessage


class UmlSDMessageLabelEventHandler(UmlBaseEventHandler):
    """
    Event handler for Sequence Diagram Message Labels.
    """

    def __init__(self, previousEventHandler: ShapeEvtHandler):
        self.logger: Logger = getLogger(__name__)
        super().__init__(previousEventHandler=previousEventHandler)
        self._dragOffsetX: int = 0
        self._dragOffsetY: int = 0

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Record drag offsets and capture mouse for smooth unconstrained dragging.

        Args:
            x: Raw cursor X
            y: Raw cursor Y
            keys: Key modifiers
            attachment: Attachment point
        """
        label: UmlSDMessageLabel = cast(UmlSDMessageLabel, self.GetShape())
        self._dragOffsetX = round(label.GetX() - x)
        self._dragOffsetY = round(label.GetY() - y)

        canvas: UmlFrame = label.umlFrame
        if not canvas.HasCapture():
            canvas.CaptureMouse()

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Move the label smoothly with 1-pixel precision during drag.

        Args:
            draw: Unused in live move
            x: Raw cursor X
            y: Raw cursor Y
            keys: Key modifiers
            attachment: Attachment point
        """
        label: UmlSDMessageLabel = cast(UmlSDMessageLabel, self.GetShape())

        newCenterX: int = round(x + self._dragOffsetX)
        newCenterY: int = round(y + self._dragOffsetY)

        canvas: UmlFrame = label.umlFrame
        dc: ClientDC = ClientDC(canvas)
        canvas.PrepareDC(dc)

        label.Move(dc, newCenterX, newCenterY)
        topLeftX: int = newCenterX - (label.size.width // 2)
        topLeftY: int = newCenterY - (label.size.height // 2)
        label.position = UmlPosition(x=topLeftX, y=topLeftY)

        canvas.refresh()

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize manual placement with 1-pixel precision and update offsets.

        Args:
            x: Raw cursor X
            y: Raw cursor Y
            keys: Key modifiers
            attachment: Attachment point
        """
        label: UmlSDMessageLabel = cast(UmlSDMessageLabel, self.GetShape())
        canvas: UmlFrame = label.umlFrame
        if canvas.HasCapture():
            canvas.ReleaseMouse()

        newCenterX: int = round(x + self._dragOffsetX)
        newCenterY: int = round(y + self._dragOffsetY)

        dc: ClientDC = ClientDC(canvas)
        canvas.PrepareDC(dc)

        label.Move(dc, newCenterX, newCenterY)
        topLeftX: int = newCenterX - (label.size.width // 2)
        topLeftY: int = newCenterY - (label.size.height // 2)
        label.position = UmlPosition(x=topLeftX, y=topLeftY)

        from umlshapes.sd.UmlSDMessage import UmlSDMessage

        parentMessage: Optional[UmlSDMessage] = cast(Optional[UmlSDMessage], label.parent)
        if parentMessage is not None and len(parentMessage._lineControlPoints) >= 2:
            startX: int = round(parentMessage._lineControlPoints[0][0])
            endX: int = round(parentMessage._lineControlPoints[-1][0])
            lineY: int = round(parentMessage._lineControlPoints[0][1])

            lineLength: int = endX - startX
            if lineLength != 0:
                fraction: float = (newCenterX - startX) / lineLength
                label.proportionalOffset = fraction
            label.fixedX = newCenterX
            label.verticalOffset = newCenterY - lineY

        self._indicateFrameModified()
        canvas.refresh()

    def OnSizingEndDragLeft(self, pt: ControlPoint, x: int, y: int, keys: int = 0, attachment: int = 0):
        super().OnSizingEndDragLeft(pt, x, y, keys, attachment)
        label: UmlSDMessageLabel = cast(UmlSDMessageLabel, self.GetShape())
        label.fitToText()
        canvas: UmlFrame = label.umlFrame
        self._indicateFrameModified()
        canvas.refresh()

