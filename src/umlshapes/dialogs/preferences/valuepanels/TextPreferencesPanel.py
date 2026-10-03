
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
from wx import Size
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsParameters

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlFontFamily import UmlFontFamily

DEFAULT_COMBOBOX_HEIGHT:   int = -1    # In wxWidgets, passing -1 for height uses the native platform control height
DEFAULT_STATIC_BOX_HEIGHT: int = 58    # On macOS, single-row static boxes require 58px to prevent vertical squashing
DEFAULT_STYLE_BOX_HEIGHT:  int = 75    # Accommodates nested static box and vertically stacked checkboxes

FONT_FAMILY_PANEL_WIDTH: int = 254    # Aligns with DimensionsControl (254px) and hugs the font selectors
FONT_PANEL_SIZE:        Size = Size(width=FONT_FAMILY_PANEL_WIDTH, height=DEFAULT_STATIC_BOX_HEIGHT)

TEXT_STYLE_PANEL_WIDTH: int = 285    # Hugs the background color static box and checkboxes with appropriate margin
TEXT_STYLE_PANEL_SIZE:  Size = Size(width=TEXT_STYLE_PANEL_WIDTH, height=DEFAULT_STYLE_BOX_HEIGHT)

FONT_FAMILY_SELECTOR_SIZE:           Size = Size(width=140, height=DEFAULT_COMBOBOX_HEIGHT)
FONT_SIZE_SELECTOR_SIZE:             Size = Size(width=70,  height=DEFAULT_COMBOBOX_HEIGHT)
TEXT_BACKGROUND_COLOR_SELECTOR_SIZE: Size = Size(width=110, height=DEFAULT_COMBOBOX_HEIGHT)

FONT_SIZES: List[str] = ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']


class TextPreferencesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):

        self.logger:       Logger         = getLogger(__name__)
        super().__init__(parent)

        self.SetSizerType('vertical')

        self._textDefaultText: TextCtrl = self._createDefaultTextPanel(self)

        dimensionsParameters: DimensionsParameters = DimensionsParameters(
            caption='Text Width/Height',
            valueChangedCallback=self._onTextDimensionsChanged,
            expand=False
        )
        self._textDimensions: DimensionsControl = DimensionsControl(parent=self, parameters=dimensionsParameters)
        self._textDimensions.SetSizerProps(expand=False)
        self._boldText:            CheckBox = cast(CheckBox, None)  # noqa
        self._italicizeText:       CheckBox = cast(CheckBox, None)  # noqa
        self._fontSelector:        ComboBox = cast(ComboBox, None)  # noqa
        self._fontSizeSelector:    ComboBox = cast(ComboBox, None)  # noqa
        self._textBackGroundColor: ComboBox = cast(ComboBox, None)  # noqa

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
        directoryPanel.SetSizerProps(expand=True)
        directoryPanel.SetMinSize(Size(-1, DEFAULT_STATIC_BOX_HEIGHT))

        textCtrl: TextCtrl = TextCtrl(directoryPanel)
        textCtrl.SetSizerProps(expand=True, proportion=1)

        return textCtrl

    def _createTextStylePanel(self, parent: SizedPanel):

        stylePanel: SizedStaticBox = SizedStaticBox(parent, label='Text Style')

        stylePanel.SetSizerType('horizontal')
        stylePanel.SetSizerProps(expand=False)
        stylePanel.SetMinSize(TEXT_STYLE_PANEL_SIZE)

        textBackGroundColorSSB: SizedStaticBox = SizedStaticBox(stylePanel, label='Text Background Color')
        textBackGroundColorSSB.SetSizerProps(expand=False, proportion=0)
        textBackGroundColorSSB.SetMinSize(Size(-1, DEFAULT_STATIC_BOX_HEIGHT))

        colorChoices = []
        for cc in UmlColor:
            colorChoices.append(cc.value)
        self._textBackGroundColor = ComboBox(textBackGroundColorSSB, choices=colorChoices, size=TEXT_BACKGROUND_COLOR_SELECTOR_SIZE, style=CB_READONLY)
        self._textBackGroundColor.SetSizerProps(expand=False, halign='left')

        checkBoxPanel: SizedPanel = SizedPanel(stylePanel)
        checkBoxPanel.SetSizerType('vertical')
        checkBoxPanel.SetSizerProps(expand=False, valign='center')

        self._boldText      = CheckBox(parent=checkBoxPanel, label='Bold Text')
        self._italicizeText = CheckBox(parent=checkBoxPanel, label='Italicize Text')

    def _createFontAttributesPanel(self, parent: SizedPanel):

        fontChoices = []
        for fontName in UmlFontFamily:
            fontChoices.append(fontName.value)

        fontPanel: SizedStaticBox = SizedStaticBox(parent, label='Font Family and Size')
        fontPanel.SetSizerType('horizontal')
        fontPanel.SetSizerProps(expand=False)
        fontPanel.SetMinSize(FONT_PANEL_SIZE)

        self._fontSelector = ComboBox(fontPanel, choices=fontChoices, size=FONT_FAMILY_SELECTOR_SIZE, style=CB_READONLY)
        self._fontSelector.SetSizerProps(expand=False, proportion=0)

        self._fontSizeSelector = ComboBox(fontPanel, choices=FONT_SIZES, size=FONT_SIZE_SELECTOR_SIZE, style=CB_READONLY)
        self._fontSizeSelector.SetSizerProps(expand=False, proportion=0)

    # noinspection PyUnusedLocal
    def _onDefaultTextValueChanged(self, _event: CommandEvent):
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
        colorValue: str      = event.GetString()
        colorEnum:  UmlColor = UmlColor(colorValue)

        self._preferences.textBackGroundColor = colorEnum
