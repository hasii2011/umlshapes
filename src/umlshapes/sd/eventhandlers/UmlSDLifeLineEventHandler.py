from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDInstance import UmlSDInstance


@dataclass
class LifeLineClickDetails:
    clickPosition: UmlPosition
    lifeLine:      UmlSDLifeLine


class UmlSDLifeLineEventHandler(ShapeEvtHandler):

    def __init__(self, umlSDLifeLine: UmlSDLifeLine, previousEventHandler: ShapeEvtHandler):
        """

        Args:
            umlSDLifeLine:          The lifeline we are managing
            previousEventHandler:   The previous event handler in order to correctly chain
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(prev=previousEventHandler, shape=umlSDLifeLine)

        self._umlSDLifeLine: UmlSDLifeLine = umlSDLifeLine

    def OnLeftClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        We want to capture this in order to inform any subscribers that the
        lifeline has been left-clicked. We send along relevant click details and
        delegate selection to the parent UmlSDInstance.

        Args:
            x:              The x-coordinate we will pass along
            y:              The y-coordinate we will pass along
            keys:
            attachment:
        """
        clickPosition: UmlPosition = UmlPosition(x=x, y=y)
        self.logger.debug(f'{clickPosition=}')

        sdLifeLine: UmlSDLifeLine = self.GetShape()
        umlFrame:   UmlFrame      = sdLifeLine.GetCanvas()

        if umlFrame is not None and hasattr(umlFrame, 'umlPubSubEngine') and umlFrame.umlPubSubEngine is not None:
            umlFrame.umlPubSubEngine.sendMessage(
                messageType=UmlMessageType.SD_LIFELINE_CLICKED,
                frameId=umlFrame.id,
                clickDetails=LifeLineClickDetails(
                    clickPosition=clickPosition,
                    lifeLine=sdLifeLine
                )
            )

        parentInstance: Optional['UmlSDInstance'] = sdLifeLine.umlSDInstance
        if parentInstance is not None:
            parentHandler: ShapeEvtHandler = parentInstance.GetEventHandler()
            if parentHandler is not None:
                parentHandler.OnLeftClick(x, y, keys, attachment)

    def OnBeginDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate the start of a left drag to the parent UmlSDInstance so dragging
        the lifeline moves the entire participant horizontally.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        sdLifeLine: UmlSDLifeLine = self.GetShape()
        parentInstance: Optional['UmlSDInstance'] = sdLifeLine.umlSDInstance
        if parentInstance is not None:
            parentHandler: ShapeEvtHandler = parentInstance.GetEventHandler()
            if parentHandler is not None:
                parentHandler.OnBeginDragLeft(x, y, keys, attachment)

    def OnDragLeft(self, draw: bool, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate left drag motion to the parent UmlSDInstance.

        Args:
            draw:
            x:
            y:
            keys:
            attachment:
        """
        sdLifeLine: UmlSDLifeLine = self.GetShape()
        parentInstance: Optional['UmlSDInstance'] = sdLifeLine.umlSDInstance
        if parentInstance is not None:
            parentHandler: ShapeEvtHandler = parentInstance.GetEventHandler()
            if parentHandler is not None:
                parentHandler.OnDragLeft(draw, x, y, keys, attachment)

    def OnEndDragLeft(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Delegate the end of a left drag to the parent UmlSDInstance.

        Args:
            x:
            y:
            keys:
            attachment:
        """
        sdLifeLine: UmlSDLifeLine = self.GetShape()
        parentInstance: Optional['UmlSDInstance'] = sdLifeLine.umlSDInstance
        if parentInstance is not None:
            parentHandler: ShapeEvtHandler = parentInstance.GetEventHandler()
            if parentHandler is not None:
                parentHandler.OnEndDragLeft(x, y, keys, attachment)
