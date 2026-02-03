
from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


@dataclass
class LifeLineClickDetails:
    clickPosition: UmlPosition
    lifeLine:      UmlSDLifeLine


class UmlSDLifeLineEventHandler(ShapeEvtHandler):

    def __init__(self, umlSDLifeLine: UmlSDLifeLine,  umlPubSubEngine: IUmlPubSubEngine, previousEventHandler: ShapeEvtHandler):
        """

        Args:
            umlSDLifeLine:          The lifeline we are managing
            umlPubSubEngine:        The pub sub engine
            previousEventHandler:   The previous event handler in order to correctly chain
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(prev=previousEventHandler, shape=umlSDLifeLine)

        self._umlSDLifeLine:   UmlSDLifeLine    = umlSDLifeLine
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

    def OnLeftClick(self, x: int, y: int, keys: int, attachment: int):
        """
        We want to capture this in order to inform any subscribers that the
        life has been left-clicked.  We send along relevant click details

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

        self._umlPubSubEngine.sendMessage(
            messageType=UmlMessageType.SD_LIFELINE_CLICKED,
            frameId=umlFrame.id,
            clickDetails=LifeLineClickDetails(
                clickPosition=clickPosition,
                lifeLine=sdLifeLine
            )
        )
