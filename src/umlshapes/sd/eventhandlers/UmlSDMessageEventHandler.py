
from logging import Logger
from logging import getLogger

from wx import OK

from umlshapes.lib.ogl import ShapeEvtHandler

from umlmodel.SDMessage import SDMessage

from umlshapes.dialogs.DlgEditSDMessage import Message
from umlshapes.dialogs.DlgEditSDMessage import MessageList
from umlshapes.dialogs.DlgEditSDMessage import DlgEditSDMessage

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.sd.UmlSDMessage import UmlSDMessage

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine


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

        self._umlSDMessage:    UmlSDMessage     = umlSDMessage
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
