
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_TEXT

from wx import CommandEvent
from wx import SpinCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.types.UmlDimensions import UmlDimensions


class SDPreferencesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):

        self.logger:       Logger          = getLogger(__name__)
        super().__init__(parent)
        self.SetSizerType('horizontal')

        self._instancePosition:   SpinCtrl          = cast(SpinCtrl, None)
        self._instanceDimensions: DimensionsControl = cast(DimensionsControl, None)

        self._layoutControls(parentSizedPanel=self)
        self._setControlValues()

    def _layoutControls(self, parentSizedPanel: SizedPanel):
        self._layoutInstancePositionControl(parentSizedPanel=parentSizedPanel)

        self._instanceDimensions = DimensionsControl(sizedPanel=parentSizedPanel, displayText='Instance Width/Height',
                                                     minValue=100, maxValue=1000,
                                                     valueChangedCallback=self._noteDimensionsChanged,
                                                     setControlsSize=False)

    def _setControlValues(self):
        """
        """
        self._instancePosition.SetValue(self._preferences.instanceYPosition)
        width:  int = self._preferences.instanceDimensions.width
        height: int = self._preferences.instanceDimensions.height
        self._instanceDimensions.dimensions = Dimensions(width=width, height=height)

    def _layoutInstancePositionControl(self, parentSizedPanel: SizedPanel):

        instancePositionSSB: SizedStaticBox = SizedStaticBox(parentSizedPanel, label='Instance Position')
        instancePositionSSB.SetSizerProps(expand=True, proportion=1)
        self._instancePosition = SpinCtrl(parent=instancePositionSSB)

        # Bind to the text control;  Then we can type in or spin
        self.Bind(EVT_TEXT, self._onPositionsChanged, self._instancePosition)

    def _onPositionsChanged(self, event: CommandEvent):

        newValue: int = event.GetInt()
        self._preferences.instanceYPosition = newValue

    def _noteDimensionsChanged(self, newValue: Dimensions):
        self._preferences.instanceDimensions = UmlDimensions(width=newValue.width, height=newValue.height)
