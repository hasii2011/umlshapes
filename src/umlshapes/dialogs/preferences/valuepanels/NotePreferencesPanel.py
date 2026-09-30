
from logging import Logger
from logging import getLogger

from wx import EVT_TEXT
from wx import ID_ANY
from wx import Size
from wx import TE_MULTILINE

from wx import CommandEvent
from wx import StaticText
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsParameters

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.types.UmlDimensions import UmlDimensions


class NotePreferencesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):

        self.logger:       Logger         = getLogger(__name__)
        super().__init__(parent)

        self.SetSizerType('vertical')
        nameSizer: SizedPanel = SizedPanel(self)
        nameSizer.SetSizerProps(proportion=3, expand=False)

        StaticText(nameSizer, ID_ANY, 'Default Note Text:')
        noteText: TextCtrl = TextCtrl(nameSizer, value=self._preferences.noteText, size=Size(400, 100), style=TE_MULTILINE)
        noteText.SetSizerProps(expand=True, proportion=1)

        parent.Bind(EVT_TEXT, self._onNoteTextChanged, noteText)

        dimensionsParameters: DimensionsParameters = DimensionsParameters(
            caption='Note Width/Height',
            valueChangedCallback=self._noteDimensionsChanged
        )
        self._noteDimensions: DimensionsControl = DimensionsControl(parent=self, parameters=dimensionsParameters)

        self._noteDimensions.SetSizerProps(expand=True, proportion=1)
        self._noteDimensions.dimensions = self._preferences.noteDimensions

    def _onNoteTextChanged(self, event: CommandEvent):
        newText: str = event.GetString()
        self._preferences.noteText = newText

    def _noteDimensionsChanged(self, newValue: Dimensions):

        # Just as easy to just cast this;  But, I want no technical debt
        self._preferences.noteDimensions = UmlDimensions(width=newValue.width, height=newValue.height)
