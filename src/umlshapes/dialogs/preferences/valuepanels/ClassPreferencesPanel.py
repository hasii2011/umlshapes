
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_SPINCTRL
from wx import EVT_TEXT
from wx import ID_ANY
from wx import SP_ARROW_KEYS
from wx import EVT_CHOICE
from wx import EVT_CHECKBOX

from wx import Size
from wx import CheckBox
from wx import Choice
from wx import SpinCtrl
from wx import SpinEvent
from wx import Window
from wx import StaticText
from wx import TextCtrl
from wx import CommandEvent

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions


class ClassPreferencesPanel(BasePreferencesPanel):
    """
    Create the UI to access all the preferences for the UML Class Shape
    """

    def __init__(self, parent: Window):

        self.logger:       Logger         = getLogger(__name__)

        super().__init__(parent)

        self._className:            TextCtrl          = cast(TextCtrl, None)
        self._classDimensions:      DimensionsControl = cast(DimensionsControl, None)
        self._classTextMargin:      SpinCtrl          = cast(SpinCtrl, None)
        self._classBackgroundColor: Choice            = cast(Choice, None)
        self._classTextColor:       Choice            = cast(Choice, None)

        self._displayDunderMethods: CheckBox      = cast(CheckBox, None)
        self._displayConstructor:   CheckBox      = cast(CheckBox, None)

        self.SetSizerType('vertical')
        self._layoutControls(self)
        #
        # Set the values before binding controls so that the event handlers don't fire
        self._setControlValues()
        self._bindControls(parent)

        self._fixPanelSize(self)

    def _bindControls(self, parent):
        parent.Bind(EVT_TEXT, self._classNameChanged, self._className)
        parent.Bind(EVT_CHOICE, self._onClassBackgroundColorChanged, self._classBackgroundColor)
        parent.Bind(EVT_CHOICE, self._onClassTextColorChanged, self._classTextColor)
        parent.Bind(EVT_CHECKBOX, self._onDisplayDunderMethodsChanged, self._displayDunderMethods)
        parent.Bind(EVT_CHECKBOX, self._onDisplayConstructorChanged, self._displayConstructor)
        parent.Bind(EVT_SPINCTRL, self._onClassTextMarginChanged, self._classTextMargin)

    def _setControlValues(self):
        """
        """
        self._classDimensions.dimensions = self._preferences.classDimensions
        self._classTextMargin.SetValue(self._preferences.classTextMargin)

        oglColors:      List[str] = self._classBackgroundColor.GetItems()
        bgColorSelIdx:  int       = oglColors.index(self._preferences.classBackGroundColor.value)
        self._classBackgroundColor.SetSelection(bgColorSelIdx)

        txtColorSelIdx: int = oglColors.index(self._preferences.classTextColor.value)
        self._classTextColor.SetSelection(txtColorSelIdx)

        self._displayDunderMethods.SetValue(self._preferences.displayDunderMethods)
        self._displayConstructor.SetValue(self._preferences.displayConstructor)

    def _layoutControls(self, parentPanel: SizedPanel):

        self._layoutNameControl(parentPanel)

        self._layoutColorControls(parentPanel)

        # sizedPanel: SizedPanel = SizedPanel(parentPanel)
        # sizedPanel.SetSizerType('horizontal')
        # sizedPanel.SetSizerProps(proportion=1, expand=True)

        self._layoutClassSizeTweaks(parentPanel)

        # noinspection PyUnresolvedReferences
        self._classDimensions.SetSizerProps(proportion=1, expand=True)

        self._layoutMethodDisplayControls(parentPanel)

    def _layoutColorControls(self, parentPanel: SizedPanel):

        colorPanel: SizedPanel = SizedPanel(parentPanel)
        colorPanel.SetSizerType('horizontal')
        colorPanel.SetSizerProps(proportion=1, expand=False)

        self._layoutClassBackgroundControl(parentPanel=colorPanel)
        self._layoutClassTextColorControl(parentPanel=colorPanel)

    def _layoutClassSizeTweaks(self, parentPanel: SizedPanel):

        self._classDimensions = DimensionsControl(sizedPanel=parentPanel,
                                                  displayText='Class Width/Height',
                                                  valueChangedCallback=self._onClassDimensionsChanged,
                                                  setControlsSize=False
                                                  )

        panel: SizedStaticBox = SizedStaticBox(parent=parentPanel, label='Class Text Margin')
        panel.SetSizerProps(expand=True, proportion=1)

        spinCtrl: SpinCtrl = SpinCtrl(panel, id=ID_ANY, size=Size(width=100, height=50), style=SP_ARROW_KEYS)
        spinCtrl.SetRange(1, 100)

        self._classTextMargin = spinCtrl

    def _layoutNameControl(self, parentPanel):

        nameSizedPanel: SizedPanel = SizedPanel(parentPanel)
        nameSizedPanel.SetSizerType('form')
        nameSizedPanel.SetSizerProps(proportion=1, expand=False)

        StaticText(nameSizedPanel, ID_ANY, 'Default Class Name:')
        self._className = TextCtrl(nameSizedPanel, value=self._preferences.defaultClassName, size=Size(160, -1))
        self._className.SetSizerProps(proportion=1, expand=False)

    def _layoutClassBackgroundControl(self, parentPanel: SizedPanel):

        classBackgroundColors = [s.value for s in UmlColor]

        classBackgroundSSB: SizedStaticBox = SizedStaticBox(parentPanel, label='Class Background')
        classBackgroundSSB.SetSizerProps(expand=True, proportion=1)

        self._classBackgroundColor = Choice(classBackgroundSSB, choices=classBackgroundColors)

    def _layoutClassTextColorControl(self, parentPanel: SizedPanel):

        classTextColors = [s.value for s in UmlColor]

        classTextColorSSB: SizedStaticBox = SizedStaticBox(parentPanel, label='Class Text Color')
        classTextColorSSB.SetSizerProps(expand=True, proportion=1)

        self._classTextColor = Choice(classTextColorSSB, choices=classTextColors)

    def _layoutMethodDisplayControls(self, parentPanel: SizedPanel):

        methodDisplayPanel: SizedPanel = SizedPanel(parentPanel)
        methodDisplayPanel.SetSizerType('horizontal')
        methodDisplayPanel.SetSizerProps(proportion=1, expand=True)

        self._displayDunderMethods = CheckBox(parent=methodDisplayPanel, label='Display Dunder Methods')
        self._displayConstructor   = CheckBox(parent=methodDisplayPanel, label='Display Constructor')

    def _classNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.className = newValue

    def _onClassDimensionsChanged(self, newValue: UmlDimensions):
        self._preferences.classDimensions = newValue

    def _onClassBackgroundColorChanged(self, event: CommandEvent):

        colorValue:    str     = event.GetString()
        oglColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.classBackgroundColor = oglColorEnum

    def _onClassTextColorChanged(self, event: CommandEvent):

        colorValue:   str      = event.GetString()
        oglColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.classTextColor = oglColorEnum

    def _onDisplayDunderMethodsChanged(self, event: CommandEvent):

        newValue: bool = event.IsChecked()
        self._preferences.displayDunderMethods = newValue

    def _onDisplayConstructorChanged(self, event: CommandEvent):

        newValue: bool = event.IsChecked()
        self._preferences.displayConstructor = newValue

    def _onClassTextMarginChanged(self, event: SpinEvent):

        newValue: int = event.GetInt()
        self._preferences.classTextMargin = newValue
