
from typing import Union

from umlmodel.Class import Class
from umlmodel.Interface import Interface
from wx import EVT_TEXT
from wx import TE_MULTILINE

from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog


class DlgEditDescription(BaseEditDialog):
    """
    Edit a class description
    """
    def __init__(self, parent: Window, model: Union[Class, Interface]):
        """

        Args:
            parent:
            model:
        """
        super().__init__(parent, title="Edit Description")

        self._model: Union[Class, Interface] = model

        sizedPanel: SizedPanel = self.GetContentsPane()

        self._txtCtrl: TextCtrl = TextCtrl(sizedPanel, value=self._model.description, style=TE_MULTILINE)
        self._txtCtrl.SetSizerProps(expand=True, proportion=1)
        self._txtCtrl.SetFocus()

        self._layoutStandardOkCancelButtonSizer()

        # text events
        self.Bind(EVT_TEXT, self._onTxtDescriptionChange, self._txtCtrl)

        self.Centre()

    @property
    def description(self) -> str:
        return self._model.description

    def _onTxtDescriptionChange(self, event):
        self._model.description = event.GetString()
