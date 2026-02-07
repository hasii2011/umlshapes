from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from copy import deepcopy

from wx import CB_SORT
from wx import EVT_TEXT
from wx import ID_ANY
from wx import CB_DROPDOWN
from wx import EVT_COMBOBOX
from wx import EVT_TEXT_ENTER
from wx import TE_PROCESS_ENTER

from wx import Window
from wx import ComboBox
from wx import DefaultSize
from wx import CommandEvent

from wx.lib.sized_controls import SizedPanel

from umlmodel.SDMessage import SDMessage

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog

Message     = NewType('Message', str)
MessageList = NewType('MessageList', List[Message])


class DlgEditSDMessage(BaseEditDialog):
    def __init__(self, parent: Window, sdMessage: SDMessage, messages: MessageList):

        super().__init__(parent, title="Edit SD Message")

        self.logger:     Logger    = getLogger(__name__)
        self._sdMessage: SDMessage = sdMessage

        sizedPanel:      SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('horizontal')

        # Ensure the current message is in the list and avoid duplicates
        currentMessage = sdMessage.message
        choices = list(messages)
        if currentMessage not in choices:
            choices.append(Message(currentMessage))

        # This combobox is created with a preset list of values.
        self._cb: ComboBox = ComboBox(
            parent=sizedPanel,
            id=ID_ANY,
            size=DefaultSize,
            value=currentMessage,
            choices=choices,
            style=CB_DROPDOWN | TE_PROCESS_ENTER | CB_SORT
        )
        self._cb.SetSizerProps(expand=False, proportion=1, valign='top')

        self.Bind(EVT_COMBOBOX,   self._onEventComboBox, self._cb)
        self.Bind(EVT_TEXT,       self._onEventText,     self._cb)
        self.Bind(EVT_TEXT_ENTER, self.EvtTextEnter,     self._cb)

        self._layoutStandardOkCancelButtonSizer()
        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.Centre()

    @property
    def sdMessage(self) -> SDMessage:
        """
        The dialog invoker MUST invoke this property in order to get
        the current value

        Returns:  The updated SD Message model object
        """
        self._sdMessage.message = self._cb.GetValue()
        return deepcopy(self._sdMessage)

    def _onEventComboBox(self, event: CommandEvent):
        message: str = event.GetString()
        self.logger.debug(f'{message=}')

    def _onEventText(self, event: CommandEvent):
        message: str = event.GetString()
        self.logger.debug(f'{message=}')
        event.Skip(True)

    def EvtTextEnter(self, event: CommandEvent):
        message: str = event.GetString()
        self.logger.debug(f'{message=}')
        event.Skip()
