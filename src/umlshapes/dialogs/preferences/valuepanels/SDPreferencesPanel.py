
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_TEXT
from wx import EVT_CHOICE

from wx import Choice
from wx import CommandEvent
from wx import SpinCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsParameters
from codeallyadvanced.ui.widgets.TitledPanel import TitledPanel

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.sd.SDMessageLabelPlacement import SDMessageLabelPlacement
from umlshapes.types.UmlDimensions import UmlDimensions


class SDPreferencesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):

        self.logger:       Logger          = getLogger(__name__)
        super().__init__(parent)
        self.SetSizerType('vertical')

        self._instancePosition:     SpinCtrl          = cast(SpinCtrl, None)              # noqa
        self._instanceDimensions:   DimensionsControl = cast(DimensionsControl, None)     # noqa
        self._labelPlacementChoice: Choice            = cast(Choice, None)                # noqa

        self._layoutControls(parentSizedPanel=self)
        self._setControlValues()

    def _layoutControls(self, parentSizedPanel: SizedPanel):

        instanceRow: SizedPanel = SizedPanel(parentSizedPanel)
        instanceRow.SetSizerType('horizontal')
        instanceRow.SetSizerProps(expand=False)

        self._layoutInstancePositionControl(parentSizedPanel=instanceRow)

        dimensionsParameters: DimensionsParameters = DimensionsParameters(
            caption='Instance Width/Height',
            minValue=100,
            maxValue=1000,
            valueChangedCallback=self._noteDimensionsChanged,
            expand=False
        )
        self._instanceDimensions = DimensionsControl(parent=instanceRow, parameters=dimensionsParameters)
        self._instanceDimensions.SetSizerProps(expand=False)

        self._layoutLabelPlacementControl(parentSizedPanel=parentSizedPanel)

    def _layoutLabelPlacementControl(self, parentSizedPanel: SizedPanel):

        placementPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Message Label Placement')
        placementPanel.SetSizerProps(expand=False)

        choices: list[str] = [p.value for p in SDMessageLabelPlacement]

        self._labelPlacementChoice = Choice(placementPanel, choices=choices)
        self.Bind(EVT_CHOICE, self._onPlacementChanged, self._labelPlacementChoice)

    def _setControlValues(self):
        """
        """
        self._instancePosition.SetValue(self._preferences.instanceYPosition)
        width:  int = self._preferences.instanceDimensions.width
        height: int = self._preferences.instanceDimensions.height
        self._instanceDimensions.dimensions = Dimensions(width=width, height=height)

        currentPlacement: SDMessageLabelPlacement = self._preferences.messageLabelPlacement
        self._labelPlacementChoice.SetStringSelection(currentPlacement.value)

    def _layoutInstancePositionControl(self, parentSizedPanel: SizedPanel):

        positionPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Instance Position')
        positionPanel.SetSizerProps(expand=False)
        self._instancePosition = SpinCtrl(parent=positionPanel)

        # Bind to the text control;  Then we can type in or spin
        self.Bind(EVT_TEXT, self._onPositionsChanged, self._instancePosition)

    def _onPositionsChanged(self, event: CommandEvent):

        newValue: int = event.GetInt()
        self._preferences.instanceYPosition = newValue

    def _onPlacementChanged(self, event: CommandEvent):

        selectedString: str = event.GetString()
        self._preferences.messageLabelPlacement = SDMessageLabelPlacement(selectedString)

    def _noteDimensionsChanged(self, newValue: Dimensions):
        self._preferences.instanceDimensions = UmlDimensions(width=newValue.width, height=newValue.height)
