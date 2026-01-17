from logging import Logger
from logging import getLogger

from umlmodel.SDInstance import SDInstance
from wx import EVT_TEXT
from wx import TE_MULTILINE

from wx import Size
from wx import Window
from wx import TextCtrl
from wx import CommandEvent

from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog


class DlgEditInstanceName(BaseEditDialog):
    """
    Defines a multi-line text control dialog for note editing.
    This dialog is used to ask the user to enter the text that will be
    displayed in a UML note.

    Sample use:
        with DlgEditNote(umlFrame, pyutNote) as dlg:
            if dlg.ShowModal() == ID_OK:
                self._eventEngine.sendEvent(EventType.UMLDiagramModified)

    """
    def __init__(self, parent: Window, sdInstance: SDInstance):
        """

        Args:
            parent:      parent window to center on
            sdInstance:  reference to the model;  Will be modified
        """
        super().__init__(parent, title="Edit Instance Name")

        self.logger: Logger = getLogger(__name__)
        self._sdInstance: SDInstance = sdInstance

        sizedPanel: SizedPanel = self.GetContentsPane()

        self._txtCtrl: TextCtrl = TextCtrl(sizedPanel, value=self._sdInstance.instanceName, size=Size(400, 180), style=TE_MULTILINE)
        self._txtCtrl.SetFocus()

        self._layoutStandardOkCancelButtonSizer()

        self.Bind(EVT_TEXT, self._onInstanceNameChanged, self._txtCtrl)

        self.Centre()

    def _onInstanceNameChanged(self, event: CommandEvent):
        """
        Handle changes to the text in the widget identified by TXT_NOTE

        Args:
            event:
        """
        self._sdInstance.instanceName = event.GetString()
        self.logger.debug(f'{self._sdInstance=}')

    @property
    def sdInstance(self) -> SDInstance:
        return self._sdInstance
