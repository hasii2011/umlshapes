
from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import OK

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import ShapeEvtHandler

from umlmodel.SDMessage import SDMessage

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.dialogs.DlgEditSDMessage import Message
from umlshapes.dialogs.DlgEditSDMessage import MessageList
from umlshapes.dialogs.DlgEditSDMessage import DlgEditSDMessage

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
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
        self._initialFromY:    Optional[int]    = None
        self._initialToY:      Optional[int]    = None

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
        super().OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Move the entire message to the nearest snapped vertical time slot.

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        self._snapMessageToSlot(targetY=y)

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Finalize message placement at the snapped slot and notify frame of modification.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        self._snapMessageToSlot(targetY=y)
        if self._initialFromY is not None and self._umlSDMessage.fromY != self._initialFromY:
            self._indicateFrameModified()

        self._initialFromY = None
        self._initialToY = None
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
        self.OnBeginDragLeft(x=x, y=y, keys=keys, attachment=attachment)

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
        self.OnDragLeft(draw=draw, x=x, y=y, keys=keys, attachment=attachment)

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
        self.OnEndDragLeft(x=x, y=y, keys=keys, attachment=attachment)

    def _snapMessageToSlot(self, targetY: int):
        """
        Compute nearest valid slot Y and update message endpoints and label.

        Args:
            targetY: Raw cursor Y coordinate
        """
        startLifeLine: Optional[UmlSDLifeLine] = cast(Optional[UmlSDLifeLine], self._umlSDMessage.GetFrom())
        if startLifeLine is None:
            return

        headerBottomY: int = startLifeLine.rectangle.top
        rawSlotIndex: int = self._layoutEngine.computeNearestSlotIndex(headerBottomY=headerBottomY, targetY=targetY)
        maxSlotIndex: int = max(
            0,
            (startLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding)
            // self._layoutEngine.parameters.slotHeight
        )
        clampedSlotIndex: int = max(0, min(rawSlotIndex, maxSlotIndex))
        snappedY: int = self._layoutEngine.computeSlotY(headerBottomY=headerBottomY, slotIndex=clampedSlotIndex)

        if snappedY != self._umlSDMessage.fromY or snappedY != self._umlSDMessage.toY:
            self._umlSDMessage.fromY = snappedY
            self._umlSDMessage.toY = snappedY
            canvas: UmlFrame = self._umlSDMessage.umlFrame
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
