
from typing import Callable

from logging import Logger
from logging import getLogger

from enum import Enum

from dataclasses import dataclass

from wx import EVT_SPINCTRL
from wx import ID_ANY
from wx import SP_ARROW_KEYS

from wx import Size
from wx import SpinCtrl
from wx import SpinEvent
from wx import StaticText

from wx.lib.sized_controls import SizedPanel

NSC_CALLBACK_PARAMETER_TYPE = str | int

NSCValueChangedCallback = Callable[[NSC_CALLBACK_PARAMETER_TYPE], None]

class NSCValueType(Enum):
    STRING = 'String'
    INT    = 'Int'

@dataclass
class NamedSpinControlDescription:
    label:       str
    controlSize: Size
    minValue:    int
    maxValue:    int
    valueType:   NSCValueType
    valueChangedCallback: NSCValueChangedCallback

class NamedSpinCtrl(SizedPanel):
    """
    TODO: Move to code-ally-advanced

    An opinionated Spin Control Widget that has a name
    Provides a way to get and set the final value.
    The parameters to set up the widget are provided by a
    NamedSpinControlDescription
    """
    def __init__(self, parent: SizedPanel, description: NamedSpinControlDescription):
        """

        Args:
            parent:         The parent panel
            description:    The description of the control to create
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self.SetSizerType('vertical')

        self._staticText: StaticText = StaticText(self, ID_ANY, description.label)

        spinCtrl: SpinCtrl = SpinCtrl(self, id=ID_ANY, size=description.controlSize, style=SP_ARROW_KEYS)
        spinCtrl.SetRange(description.minValue, description.maxValue)

        self._spinCtrl:  SpinCtrl     = spinCtrl
        self._valueType: NSCValueType = description.valueType

        self._valueChangedCallback: NSCValueChangedCallback = description.valueChangedCallback

        parent.Bind(EVT_SPINCTRL, self._onValueChanged, self._spinCtrl)

    def _setToolTip(self, tip: str):
        self._spinCtrl.SetToolTip(tip)

    # noinspection PyPropertyDefinition
    # noinspection PyTypeChecker
    toolTip = property(fget=None, fset=_setToolTip, fdel=None, doc='Write only property to set tooltip on spin control')

    @property
    def value(self):
        return self._spinCtrl.GetValue()

    @value.setter
    def value(self, newValue):
        self._spinCtrl.SetValue(newValue)

    def _onValueChanged(self, event: SpinEvent):

        if self._valueType == NSCValueType.INT:
            newInterval: NSC_CALLBACK_PARAMETER_TYPE = event.GetInt()
        else:
            newInterval = event.GetString()

        self._valueChangedCallback(newInterval)
