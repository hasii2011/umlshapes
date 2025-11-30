
from typing import List

from logging import Logger
from logging import getLogger

from umlmodel.enumerations.Stereotype import Stereotype
from wx import CANCEL
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_CANCEL
from wx import ID_OK
from wx import OK

from wx import CommandEvent
from wx import ListBox
from wx import StaticText
from wx import Window

from wx.lib.sized_controls import SizedPanel


from umlshapes.dialogs.BaseEditDialog import BaseEditDialog


class DlgEditStereotype(BaseEditDialog):
    """
    Usage:
            with DlgEditStereotype(parent=parent, eventEngine=eventEngine, stereotype=model.stereotype) as dlg:
                if dlg.ShowModal() == OK:
                    self._model.stereotype = dlg.value
    """

    def __init__(self, parent: Window, stereotype: Stereotype):

        super().__init__(parent=parent, title='Select Stereotype')
        self.logger: Logger = getLogger(__name__)

        panel: SizedPanel = self.GetContentsPane()

        panel.SetSizerType('vertical')

        classStereoTypes:         List[str] = [enum.value for enum in Stereotype]
        self._label:              StaticText = StaticText(panel, label='Stereotypes')
        self._stereoTypeSelector: ListBox    = ListBox(panel, choices=classStereoTypes)
        self._stereoTypeSelector.SetSizerProps(proportion=1, expand=True)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK | CANCEL))

        self._setSelected(stereotype=stereotype)
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.Bind(EVT_BUTTON, self._onOk, id=ID_OK)
        self.Bind(EVT_BUTTON, self._onClose, id=ID_CANCEL)
        self.Bind(EVT_CLOSE,  self._onClose)

    @property
    def value(self) -> Stereotype:
        """
        Query this if the dialog ended with Ok.
        I know,  Standard wxPython uses GetValue,  That is too bad, I am providing
        additional functionality,  aka type conversion

        Returns:    The currently selected enumeration
        """
        selection: str = self._stereoTypeSelector.GetString(self._stereoTypeSelector.GetSelection())

        stereotype: Stereotype = Stereotype.toEnum(selection)
        return stereotype

    def _setSelected(self, stereotype: Stereotype):
        x: int = self._stereoTypeSelector.FindString(stereotype.value)
        self._stereoTypeSelector.SetSelection(x)

    def _onOk(self, event: CommandEvent):
        super()._onOk(event)

    def _onClose(self, event: CommandEvent):
        super()._onClose(event)
