from logging import Logger
from logging import getLogger
from typing import cast

from wx import SpinCtrl
from wx import SpinCtrlDouble
from wx import Window
from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

NO_SPIN_CTRL: SpinCtrl = cast(SpinCtrl, None)


class LollipopPreferencesPanel(BasePreferencesPanel):

    def __init__(self,  parent: Window):
        self.logger: Logger = getLogger(__name__)

        self._lollipopLineLength:   SpinCtrl = NO_SPIN_CTRL
        self._lollipopCircleRadius: SpinCtrl = NO_SPIN_CTRL
        self._interfaceNameIndent:  SpinCtrl = NO_SPIN_CTRL
        self._hitAreaInflationRate: SpinCtrl = NO_SPIN_CTRL

        self._horizontalOffset:     SpinCtrlDouble = cast(SpinCtrlDouble, None)

        super().__init__(parent)
        self._layoutControls(parent=self)
        self._setControlValues()
        self._bindControls()

    def _layoutControls(self, parent: SizedPanel):
        pass

    def _setControlValues(self):
        pass

    def _bindControls(self):
        pass