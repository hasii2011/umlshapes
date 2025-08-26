
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from wx import CB_READONLY
from wx import CheckBox
from wx import CommandEvent
from wx import EVT_CHECKBOX
from wx import EVT_COMBOBOX
from wx import ID_ANY

from wx import ComboBox
from wx import StaticText
from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.lib.ogl import FORMAT_CENTRE_HORIZ
from umlshapes.lib.ogl import FORMAT_CENTRE_VERT
from umlshapes.lib.ogl import FORMAT_SIZE_TO_CONTENTS
from umlshapes.links.UmlAssociationLabelFormat import UmlAssociationLabelFormat
from umlshapes.types.UmlDimensions import UmlDimensions

ASSOCIATION_LABEL_MIN_SIZE: int = 20

FONT_SIZES:    List[str] = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
DIAMOND_SIZES: List[str] = ['6', '7', '8', '10', '11', '12', '13', '14', '15']


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

        self._formatNone:             CheckBox = cast(CheckBox, None)
        self._formatCenterHorizontal: CheckBox = cast(CheckBox, None)
        self._formatCenterVertical:   CheckBox = cast(CheckBox, None)
        self._formatSizeToContents:   CheckBox = cast(CheckBox, None)

        self._layoutControls(parentPanel=self)
        self._setControlValues()

        self.Bind(EVT_COMBOBOX, self._onTextFontSizedChanged, self._textFontSize)
        self.Bind(EVT_COMBOBOX, self._onDiamondSizeChanged,   self._diamondSize)

        self.Bind(EVT_CHECKBOX, self._onFormatNoneChange,             self._formatNone)
        self.Bind(EVT_CHECKBOX, self._onFormatCenterHorizontalChange, self._formatCenterHorizontal)
        self.Bind(EVT_CHECKBOX, self._onFormatCenterVerticalChange,   self._formatCenterVertical)
        self.Bind(EVT_CHECKBOX, self._onFormatSizeToContentsChange,   self._formatSizeToContents)

    def _layoutControls(self, parentPanel: SizedPanel):

        formPanel: SizedPanel = SizedPanel(parentPanel)
        formPanel.SetSizerType('form')

        # First Line
        StaticText(formPanel, ID_ANY, 'Font Size')
        self._textFontSize = ComboBox(formPanel, choices=FONT_SIZES, style=CB_READONLY)

        # Second Line
        StaticText(formPanel, ID_ANY, 'Diamond Size')
        self._diamondSize = ComboBox(formPanel, choices=DIAMOND_SIZES, style=CB_READONLY)

        # This not in the form
        self._associationsLabelDimensions = DimensionsControl(sizedPanel=parentPanel,
                                                              displayText='Association Label Width/Height',
                                                              valueChangedCallback=self._onAssociationLabelDimensionsChanged,
                                                              minValue=ASSOCIATION_LABEL_MIN_SIZE,
                                                              setControlsSize=False
                                                              )
        self._layoutFormatMode(parentPanel=parentPanel)

    def _layoutFormatMode(self, parentPanel: SizedPanel):

        formatContainer: SizedStaticBox = SizedStaticBox(parent=parentPanel, label='Association Label Format')
        formatContainer.SetSizerProps(expand=True, proportion=2)

        self._formatNone             = CheckBox(formatContainer, ID_ANY, UmlAssociationLabelFormat.FORMAT_NONE.value)
        self._formatCenterHorizontal = CheckBox(formatContainer, ID_ANY, UmlAssociationLabelFormat.FORMAT_CENTER_HORIZONTAL.value)
        self._formatCenterVertical   = CheckBox(formatContainer, ID_ANY, UmlAssociationLabelFormat.FORMAT_CENTER_VERTICAL.value)
        self._formatSizeToContents   = CheckBox(formatContainer, ID_ANY, UmlAssociationLabelFormat.FORMAT_SIZE_TO_CONTENTS.value)

    def _setControlValues(self):

        self._textFontSize.SetValue(str(self._preferences.associationTextFontSize))
        self._diamondSize.SetValue(str(self._preferences.diamondSize))

        self._associationsLabelDimensions.dimensions = self._preferences.associationLabelSize

        labelFormat: int = self._preferences.associationLabelFormat

        if UmlAssociationLabelFormat.isFormatModeSet(wxValue=labelFormat, wxMode=FORMAT_CENTRE_HORIZ):
            self._formatCenterHorizontal.SetValue(True)

        if UmlAssociationLabelFormat.isFormatModeSet(wxValue=labelFormat, wxMode=FORMAT_CENTRE_VERT):
            self._formatCenterVertical.SetValue(True)

        if UmlAssociationLabelFormat.isFormatModeSet(wxValue=labelFormat, wxMode=FORMAT_SIZE_TO_CONTENTS):
            self._formatSizeToContents.SetValue(True)

    def _onTextFontSizedChanged(self, event: CommandEvent):
        newFontSize: str = event.GetString()
        self._preferences.associationTextFontSize = int(newFontSize)

    def _onDiamondSizeChanged(self, event: CommandEvent):
        newDiamondSize: str = event.GetString()
        self._preferences.diamondSize = int(newDiamondSize)

    def _onAssociationLabelDimensionsChanged(self, newValue: UmlDimensions):
        self._preferences.associationLabelSize = newValue

    # noinspection PyUnusedLocal
    def _onFormatNoneChange(self, event: CommandEvent):
        if self._formatNone.GetValue() is True:
            self._clearFormatControls()
            self._disableFormatControls()
            self._preferences.associationLabelFormat = UmlAssociationLabelFormat.FORMAT_NONE.value
        else:
            self._enableFormatControl()

    # noinspection PyUnusedLocal
    def _onFormatCenterHorizontalChange(self, event: CommandEvent):
        self._updatePreference(control=self._formatCenterHorizontal, wxMode=FORMAT_CENTRE_HORIZ)

    # noinspection PyUnusedLocal
    def _onFormatCenterVerticalChange(self, event: CommandEvent):
        self._updatePreference(control=self._formatCenterVertical, wxMode=FORMAT_CENTRE_VERT)

    # noinspection PyUnusedLocal
    def _onFormatSizeToContentsChange(self, event: CommandEvent):
        self._updatePreference(control=self._formatSizeToContents, wxMode=FORMAT_SIZE_TO_CONTENTS)

    def _disableFormatControls(self):
        self._formatCenterHorizontal.Disable()
        self._formatCenterVertical.Disable()
        self._formatSizeToContents.Disable()

    def _enableFormatControl(self):
        self._formatCenterHorizontal.Enable(True)
        self._formatCenterVertical.Enable(True)
        self._formatSizeToContents.Enable(True)

    def _clearFormatControls(self):

        self._formatCenterHorizontal.SetValue(False)
        self._formatCenterVertical.SetValue(False)
        self._formatSizeToContents.SetValue(False)

    def _updatePreference(self, control: CheckBox, wxMode: int):

        # noinspection PyTypeChecker
        currentValue: int = self._preferences.associationLabelFormat
        updatedValue: int = self._getUpdatedValue(control=control, wxMode=wxMode, currentValue=currentValue)
        self._preferences.associationLabelFormat = UmlAssociationLabelFormat.toDelimitedString(updatedValue)

    def _getUpdatedValue(self, control: CheckBox, wxMode: int, currentValue: int) -> int:
        """
        Checks the state of the checkbox control and either clears the value are sets
        it.  Returns the updated value
        Args:
            control:        The checkbox we are 'checking' ;-)
            wxMode:        The wxPython value/bit
            currentValue:   The current value of the format mode

        Returns:  The updated value either set or cleared

        """
        if control.GetValue() is True:
            updatedValue: int = UmlAssociationLabelFormat.setMode(wxMode=wxMode, wxValue=currentValue)
        else:
            updatedValue = UmlAssociationLabelFormat.clearMode(wxMode=wxMode, wxValue=currentValue)

        return updatedValue