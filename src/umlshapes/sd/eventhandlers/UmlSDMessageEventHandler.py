
from logging import Logger
from logging import getLogger

# from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.lib.ogl import ShapeEvtHandler
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.sd.UmlSDMessage import UmlSDMessage


class UmlSDMessageEventHandler(ShapeEvtHandler):
    def __init__(self, umlSDMessage: UmlSDMessage, umlPubSubEngine: IUmlPubSubEngine, previousEventHandler: ShapeEvtHandler):
        """

        Args:
            umlSDMessage:           The UML SD Message we are managing
            umlPubSubEngine:        The pub sub engine
            previousEventHandler:   The previous event handler in order to correctly chain
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(prev=previousEventHandler, shape=umlSDMessage)

        self._umlSDMessage:    UmlSDMessage      = umlSDMessage
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

    def OnLeftClick(self, x: int, y: int, keys: int, attachment: int):
        """

        Args:
            x:              The x-coordinate we will pass along
            y:              The y-coordinate we will pass along
            keys:
            attachment:
        """

        self.logger.info(f'xy: ({x},{y})')

        # umlSDMessage: UmlSDMessage = self._umlSDMessage
        # umlFrame:     UmlFrame     = umlSDMessage.umlFrame

        super().OnLeftClick(x, y, keys, attachment)
