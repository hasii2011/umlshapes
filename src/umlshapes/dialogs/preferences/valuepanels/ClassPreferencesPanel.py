
from typing import List
from typing import cast
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import EVT_TEXT
from wx import EVT_CHOICE
from wx import EVT_SPINCTRL
from wx import SP_ARROW_KEYS
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

from codeallybasic.Dimensions import Dimensions

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

from umlshapes.dialogs.preferences.valuepanels.DualSpinners import DualSpinners
from umlshapes.dialogs.preferences.valuepanels.DualSpinners import SpinnerValues

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions

class ClassDimensions(DualSpinners):
    """
    Syntactic sugar around dual spinners
    """
    def __init__(self, sizedPanel: SizedPanel,
                 valueChangedCallback: Callable,
                 minValue: int = DualSpinners.DEFAULT_MIN_VALUE, maxValue: int = DualSpinners.DEFAULT_MAX_VALUE,
                 setControlsSize: bool = True):

        self._dimensionsChangedCallback: Callable   = valueChangedCallback
        self._dimensions:                Dimensions = Dimensions()

        super().__init__(sizedPanel, valueChangedCallback=self._onSpinValueChangedCallback, minValue=minValue, maxValue=maxValue, setControlsSize=setControlsSize)

    def _setDimensions(self, newValue: Dimensions):
        self._dimensions = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.width, value1=newValue.height)

    # noinspection PyTypeChecker
    dimensions = property(fset=_setDimensions, doc='Write only property to set dimensions on control')

    def _onSpinValueChangedCallback(self, spinnerValues: SpinnerValues):
        self.logger.info(f'{spinnerValues}')

        self._dimensions.width = spinnerValues.value0
        self._dimensions.height = spinnerValues.value1

        self._dimensionsChangedCallback(self._dimensions)


class ClassPreferencesPanel(BasePreferencesPanel):
    """
    Create the UI to access all the preferences for the UML Class Shape
    """

    def __init__(self, parent: Window):

        self.logger:       Logger         = getLogger(__name__)

        super().__init__(parent)

        self._className:            TextCtrl        = cast(TextCtrl, None)
        self._classDimensions:      ClassDimensions = cast(ClassDimensions, None)
        self._classTextMargin:      SpinCtrl        = cast(SpinCtrl, None)
        self._classBackgroundColor: Choice          = cast(Choice, None)
        self._classTextColor:       Choice          = cast(Choice, None)

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
        parent.Bind(EVT_TEXT,     self._onClassNameChanged,            self._className)
        parent.Bind(EVT_CHOICE,   self._onClassBackgroundColorChanged, self._classBackgroundColor)
        parent.Bind(EVT_CHOICE,   self._onClassTextColorChanged,       self._classTextColor)
        parent.Bind(EVT_CHECKBOX, self._onDisplayDunderMethodsChanged, self._displayDunderMethods)
        parent.Bind(EVT_CHECKBOX, self._onDisplayConstructorChanged,   self._displayConstructor)
        parent.Bind(EVT_SPINCTRL, self._onClassTextMarginChanged,      self._classTextMargin)

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

        self._layoutClassAttributesForm(parentPanel)

        self._layoutMethodDisplayControls(parentPanel)

    def _layoutClassAttributesForm(self, parentPanel):
        """

        Args:
            parentPanel:

        Returns:
        """

        nameFormPanel: SizedPanel = SizedPanel(parentPanel)
        nameFormPanel.SetSizerType('form')
        nameFormPanel.SetSizerProps(expand=True, halign='center')

        StaticText(nameFormPanel, ID_ANY, 'Default Class Name')
        self._className = TextCtrl(nameFormPanel, value=self._preferences.defaultClassName)
        self._className.SetSizerProps(expand=True)

        classBackgroundColors = [s.value for s in UmlColor]

        StaticText(nameFormPanel, ID_ANY, 'Class Background')
        self._classBackgroundColor = Choice(nameFormPanel, choices=classBackgroundColors)

        classTextColors = [s.value for s in UmlColor]
        StaticText(nameFormPanel, ID_ANY, 'Class Text Color')
        self._classTextColor = Choice(nameFormPanel, choices=classTextColors)

        StaticText(nameFormPanel, ID_ANY, 'Class Text Margin')
        self._classTextMargin = SpinCtrl(nameFormPanel, id=ID_ANY, size=Size(width=100, height=-1), style=SP_ARROW_KEYS)
        self._classTextMargin .SetRange(1, 100)

        StaticText(nameFormPanel, ID_ANY, 'Class Width/Height')
        self._classDimensions = ClassDimensions(sizedPanel=nameFormPanel,
                                                valueChangedCallback=self._onClassDimensionsChanged,
                                                setControlsSize=False
                                                )

    def _layoutMethodDisplayControls(self, parentPanel: SizedPanel):

        self._displayDunderMethods = CheckBox(parent=parentPanel, label='Display Dunder Methods')
        self._displayConstructor   = CheckBox(parent=parentPanel, label='Display Constructor')

    def _onClassNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultClassName = newValue

    def _onClassDimensionsChanged(self, newValue: UmlDimensions):
        self._preferences.classDimensions = newValue

    def _onClassBackgroundColorChanged(self, event: CommandEvent):

        colorValue:    str     = event.GetString()
        oglColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.classBackGroundColor = oglColorEnum

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
