
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from wx import CB_READONLY
from wx import CommandEvent
from wx import EVT_COMBOBOX
from wx import ID_ANY

from wx import ComboBox
from wx import StaticText
from wx import Window

from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.types.UmlDimensions import UmlDimensions

ASSOCIATION_LABEL_MIN_SIZE: int = 20


class AssociationPreferencesPanel(BasePreferencesPanel):
    """
    The few preferences for association lines
    """

    def __init__(self, parent: Window):

        self.logger:       Logger         = getLogger(__name__)
        super().__init__(parent)
        self.SetSizerType('vertical')

        self._textFontSize:         ComboBox          = cast(ComboBox, None)
        self._diamondSize:          ComboBox          = cast(ComboBox, None)
        self._associationLabelSize: DimensionsControl = cast(DimensionsControl, None)

        self._layoutControls(parentPanel=self)
        self._setControlValues()

        self.Bind(EVT_COMBOBOX, self._onTextFontSizedChanged, self._textFontSize)
        self.Bind(EVT_COMBOBOX, self._onDiamondSizeChanged,   self._diamondSize)

    def _layoutControls(self, parentPanel: SizedPanel):

        fontSizes:    List[str] = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
        diamondSizes: List[str] = ['6', '7', '8', '10', '11', '12', '13', '14', '15']

        formPanel: SizedPanel = SizedPanel(parentPanel)
        formPanel.SetSizerType('form')

        # First Line
        StaticText(formPanel, ID_ANY, 'Font Size')
        self._textFontSize = ComboBox(formPanel, choices=fontSizes, style=CB_READONLY)

        # Second Line
        StaticText(formPanel, ID_ANY, 'Diamond Size')
        self._diamondSize = ComboBox(formPanel, choices=diamondSizes, style=CB_READONLY)

        # This not in the form
        self._associationsLabelDimensions = DimensionsControl(sizedPanel=parentPanel,
                                                              displayText='Association Label Width/Height',
                                                              valueChangedCallback=self._onAssociationLabelDimensionsChanged,
                                                              minValue=ASSOCIATION_LABEL_MIN_SIZE,
                                                              setControlsSize=False
                                                              )

    def _setControlValues(self):

        self._textFontSize.SetValue(str(self._preferences.associationTextFontSize))
        self._diamondSize.SetValue(str(self._preferences.diamondSize))

        self._associationsLabelDimensions.dimensions = self._preferences.associationLabelSize

    def _onTextFontSizedChanged(self, event: CommandEvent):
        newFontSize: str = event.GetString()
        self._preferences.associationTextFontSize = int(newFontSize)

    def _onDiamondSizeChanged(self, event: CommandEvent):
        newDiamondSize: str = event.GetString()
        self._preferences.diamondSize = int(newDiamondSize)

    def _onAssociationLabelDimensionsChanged(self, newValue: UmlDimensions):
        self._preferences.associationLabelSize = newValue
