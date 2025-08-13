
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CB_READONLY
from wx import EVT_CHECKBOX
from wx import EVT_COMBOBOX
from wx import EVT_TEXT

from wx import CheckBox
from wx import ComboBox
from wx import CommandEvent
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlFontFamily import UmlFontFamily


class TextPreferencesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):

        self.logger:       Logger         = getLogger(__name__)
        super().__init__(parent)

        self.SetSizerType('vertical')

        self._textDefaultText: TextCtrl = self._createDefaultTextPanel(self)

        self._textDimensions: DimensionsControl = DimensionsControl(sizedPanel=self,
                                                                    displayText='Text Width/Height',
                                                                    valueChangedCallback=self._onTextDimensionsChanged,
                                                                    setControlsSize=False
                                                                    )
        self._boldText:            CheckBox = cast(CheckBox, None)
        self._italicizeText:       CheckBox = cast(CheckBox, None)
        self._fontSelector:        ComboBox = cast(ComboBox, None)
        self._fontSizeSelector:    ComboBox = cast(ComboBox, None)
        self._textBackGroundColor: ComboBox = cast(ComboBox, None)

        self._createFontAttributesPanel(self)
        self._createTextStylePanel(self)
        self._setControlValues()
        self._bindControls()

    def _setControlValues(self):

        self._textDefaultText.SetValue(self._preferences.textValue)
        self._textDimensions.dimensions = self._preferences.textDimensions
        self._boldText.SetValue(self._preferences.textBold)
        self._italicizeText.SetValue(self._preferences.textItalicize)
        self._fontSizeSelector.SetValue(str(self._preferences.textFontSize))
        self._textBackGroundColor.SetValue(self._preferences.textBackGroundColor.value)

    def _bindControls(self):

        self.Bind(EVT_TEXT,     self._onDefaultTextValueChanged,   self._textDefaultText)
        self.Bind(EVT_CHECKBOX, self._onTextBoldValueChanged,      self._boldText)
        self.Bind(EVT_CHECKBOX, self._onTextItalicizeValueChanged, self._italicizeText)

        self.Bind(EVT_COMBOBOX, self._onFontSelectionChanged,       self._fontSelector)
        self.Bind(EVT_COMBOBOX, self._onFontSizeSelectionChanged,   self._fontSizeSelector)
        self.Bind(EVT_COMBOBOX, self._onTextBackGroundColorChanged, self._textBackGroundColor)

    def _createDefaultTextPanel(self, parent: SizedPanel):
        directoryPanel: SizedStaticBox = SizedStaticBox(parent, label='Default Text')

        directoryPanel.SetSizerType('horizontal')
        directoryPanel.SetSizerProps(expand=True, proportion=1)

        textCtrl: TextCtrl = TextCtrl(directoryPanel)
        textCtrl.SetSizerProps(expand=True, proportion=5)

        return textCtrl

    def _createTextStylePanel(self, parent: SizedPanel):

        stylePanel: SizedStaticBox = SizedStaticBox(parent, label='Text Style')

        stylePanel.SetSizerType('horizontal')
        stylePanel.SetSizerProps(expand=True, proportion=2)

        textBackGroundColorSSB: SizedStaticBox = SizedStaticBox(stylePanel, label='Text Background Color')
        textBackGroundColorSSB.SetSizerProps(expand=True, proportion=1)

        colorChoices = []
        for cc in UmlColor:
            colorChoices.append(cc.value)
        self._textBackGroundColor = ComboBox(textBackGroundColorSSB, choices=colorChoices, style=CB_READONLY)

        self._boldText      = CheckBox(parent=stylePanel, label='Bold Text')
        self._italicizeText = CheckBox(parent=stylePanel, label='Italicize Text')

    def _createFontAttributesPanel(self, parent: SizedPanel):

        fontChoices = []
        for fontName in UmlFontFamily:
            fontChoices.append(fontName.value)

        fontPanel: SizedStaticBox = SizedStaticBox(parent, label='Font Family and Size')
        fontPanel.SetSizerType('horizontal')
        fontPanel.SetSizerProps(expand=True, proportion=1)

        self._fontSelector = ComboBox(fontPanel, choices=fontChoices, style=CB_READONLY)
        self._fontSelector.SetSizerProps(expand=True, proportion=1)

        fontSizes: List[str] = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
        self._fontSizeSelector = ComboBox(fontPanel, choices=fontSizes, style=CB_READONLY)
        self._fontSizeSelector.SetSizerProps(expand=True, proportion=1)

    # noinspection PyUnusedLocal
    def _onDefaultTextValueChanged(self, event: CommandEvent):
        self._preferences.textValue = self._textDefaultText.GetValue()

    def _onTextDimensionsChanged(self, newValue: UmlDimensions):
        self._preferences.textDimensions = newValue

    def _onTextBoldValueChanged(self, event: CommandEvent):

        val: bool = event.IsChecked()

        self._preferences.textBold = val

    def _onTextItalicizeValueChanged(self, event: CommandEvent):

        val: bool = event.IsChecked()
        self._preferences.textItalicize = val

    def _onFontSelectionChanged(self, event: CommandEvent):

        newFontName: str           = event.GetString()
        fontEnum:    UmlFontFamily = UmlFontFamily(newFontName)

        self._preferences.textFontFamily = fontEnum

    def _onFontSizeSelectionChanged(self, event: CommandEvent):

        newFontSize: str = event.GetString()

        self._preferences.textFontSize = int(newFontSize)

    def _onTextBackGroundColorChanged(self, event: CommandEvent):
        colorValue:    str      = event.GetString()
        pyutColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.textBackGroundColor = pyutColorEnum
