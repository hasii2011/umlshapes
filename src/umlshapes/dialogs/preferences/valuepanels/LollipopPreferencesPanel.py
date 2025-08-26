from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_SPINCTRLDOUBLE
from wx import ID_ANY
from wx import SP_ARROW_KEYS

from wx import Size
from wx import SpinCtrlDouble
from wx import SpinDoubleEvent
from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlshapes.dialogs.preferences.NamedSpinCtrl import NSCValueType
from umlshapes.dialogs.preferences.NamedSpinCtrl import NSC_CALLBACK_PARAMETER_TYPE

from umlshapes.dialogs.preferences.NamedSpinCtrl import NamedSpinCtrl
from umlshapes.dialogs.preferences.NamedSpinCtrl import NamedSpinControlDescription

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

NO_SPIN_CTRL: NamedSpinCtrl = cast(NamedSpinCtrl, None)

MIN_LOLLIPOP_LENGTH: int = 50
MAX_LOLLIPOP_LENGTH: int = 150

MIN_LOLLIPOP_CIRCLE_RADIUS: int = 4
MAX_LOLLIPOP_CIRCLE_RADIUS: int = 20

MIN_INTERFACE_NAME_INDENT: int = 2
MAX_INTERFACE_NAME_INDENT: int = 20

MIN_HIT_AREA_INFLATION_RATE: int = 2
MAX_HIT_AREA_INFLATION_RATE: int = 10

MIN_HORIZONTAL_OFFSET: float = 0.1
MAX_HORIZONTAL_OFFSET: float = 1.0

DEFAULT_SPIN_CTRL_SIZE: Size = Size(width=100, height=20)


def onLollipopLengthChanged(newValue: NSC_CALLBACK_PARAMETER_TYPE):
    LollipopPreferencesPanel.clsUmlPreferences.lollipopLineLength = newValue

def onLollipopCircleRadiusChanged(newValue: NSC_CALLBACK_PARAMETER_TYPE):
    LollipopPreferencesPanel.clsUmlPreferences.lollipopCircleRadius = newValue

def onLollipopInterfaceNameIndentChanged(newValue: NSC_CALLBACK_PARAMETER_TYPE):
    LollipopPreferencesPanel.clsUmlPreferences.interfaceNameIndent = newValue

def onHitAreaInflationRationChanged(newValue: NSC_CALLBACK_PARAMETER_TYPE):
    LollipopPreferencesPanel.clsUmlPreferences.hitAreaInflationRate = newValue


LollipopLineLength: NamedSpinControlDescription = NamedSpinControlDescription(
    label='Lollipop Line Length',
    controlSize=DEFAULT_SPIN_CTRL_SIZE,
    minValue=MIN_LOLLIPOP_LENGTH,
    maxValue=MAX_LOLLIPOP_LENGTH,
    valueType=NSCValueType.INT,
    valueChangedCallback=onLollipopLengthChanged
)

LollipopCircleRadius: NamedSpinControlDescription = NamedSpinControlDescription(
    label='Lollipop Circle Radius',
    controlSize=DEFAULT_SPIN_CTRL_SIZE,
    minValue=MIN_LOLLIPOP_CIRCLE_RADIUS,
    maxValue=MAX_LOLLIPOP_CIRCLE_RADIUS,
    valueType=NSCValueType.INT,
    valueChangedCallback = onLollipopCircleRadiusChanged
)

InterfaceNameIndent: NamedSpinControlDescription = NamedSpinControlDescription(
    label='Interface Name Indent',
    controlSize=DEFAULT_SPIN_CTRL_SIZE,
    minValue=MIN_INTERFACE_NAME_INDENT,
    maxValue=MAX_INTERFACE_NAME_INDENT,
    valueType=NSCValueType.INT,
    valueChangedCallback=onLollipopInterfaceNameIndentChanged
)

HitAreaInflationRate:  NamedSpinControlDescription = NamedSpinControlDescription(
    label='Hit Area Inflation Rate',
    controlSize=DEFAULT_SPIN_CTRL_SIZE,
    minValue=MIN_HIT_AREA_INFLATION_RATE,
    maxValue=MAX_HIT_AREA_INFLATION_RATE,
    valueType=NSCValueType.INT,
    valueChangedCallback = onHitAreaInflationRationChanged
)


class LollipopPreferencesPanel(BasePreferencesPanel):

    clsUmlPreferences: UmlPreferences = UmlPreferences()
    """
    I have a class version of the preferences for the class callbacks that need 
    them.  This is cheap since the preferences class is a Singleton
    """

    def __init__(self,  parent: Window):
        self.logger: Logger = getLogger(__name__)

        self._lollipopLineLength:   NamedSpinCtrl = NO_SPIN_CTRL
        self._lollipopCircleRadius: NamedSpinCtrl = NO_SPIN_CTRL
        self._interfaceNameIndent:  NamedSpinCtrl = NO_SPIN_CTRL
        self._hitAreaInflationRate: NamedSpinCtrl = NO_SPIN_CTRL

        self._horizontalOffset: SpinCtrlDouble = cast(SpinCtrlDouble, None)

        super().__init__(parent)

        self._layoutControls(parent=self)
        self._setControlValues()
        self._bindControls(self)

    def _layoutControls(self, parent: SizedPanel):
        """

        Args:
            parent:
        """
        self._lollipopLineLength   = NamedSpinCtrl(parent=parent, description=LollipopLineLength)
        self._lollipopCircleRadius = NamedSpinCtrl(parent=parent, description=LollipopCircleRadius)
        self._interfaceNameIndent  = NamedSpinCtrl(parent=parent, description=InterfaceNameIndent)
        self._hitAreaInflationRate = NamedSpinCtrl(parent=parent, description=HitAreaInflationRate)

        self._layoutHorizontalOffset(parent)

    def _layoutHorizontalOffset(self, parent: SizedPanel):

        panel: SizedStaticBox = SizedStaticBox(parent=parent, label='Horizontal Offset')
        panel.SetSizerType('horizontal')
        panel.SetSizerProps(proportion=1)

        horizontalOffSet: SpinCtrlDouble = SpinCtrlDouble(panel, id=ID_ANY, size=DEFAULT_SPIN_CTRL_SIZE, style=SP_ARROW_KEYS)
        horizontalOffSet.SetRange(MIN_HORIZONTAL_OFFSET, MAX_HORIZONTAL_OFFSET)
        horizontalOffSet.SetIncrement(0.1)

        self._horizontalOffset = horizontalOffSet

    def _setControlValues(self):
        """
        For the NameSpinCtrl that control takes care of handling the
        spinner.  It then calls the provide callback in the spinner
        description
        """
        self._lollipopLineLength.value    = self._preferences.lollipopLineLength
        self._lollipopCircleRadius.value  = self._preferences.lollipopCircleRadius
        self._interfaceNameIndent.value   = self._preferences.interfaceNameIndent
        self._hitAreaInflationRate.value  = self._preferences.hitAreaInflationRate

        self._horizontalOffset.SetValue(self._preferences.horizontalOffset)

    def _bindControls(self, parent: SizedPanel):
        parent.Bind(EVT_SPINCTRLDOUBLE, self._onHorizontalOffSetChanged, self._horizontalOffset)

    def _onHorizontalOffSetChanged(self, event: SpinDoubleEvent):

        newValue: float = event.GetValue()
        self._preferences.horizontalOffset = newValue
