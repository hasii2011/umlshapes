from dataclasses import dataclass

from typing import Callable

from logging import Logger
from logging import getLogger

from wx import EVT_TEXT
from wx import EVT_SPINCTRL
from wx import CommandEvent
from wx import ID_ANY
from wx import Size
from wx import SpinCtrl
from wx import StaticText

from wx.lib.sized_controls import SizedPanel

DEFAULT_MIN_SPINNER_VALUE: int = 0
DEFAULT_MAX_SPINNER_VALUE: int = 1000
DEFAULT_SPINNER_WIDTH:     int = 80
DEFAULT_SPINNER_HEIGHT:    int = -1
SPINNER_SPACING_RIGHT:     int = 10
LABEL_SPACING_RIGHT:       int = 5
DEFAULT_FIRST_LABEL:       str = 'W:'
DEFAULT_SECOND_LABEL:      str = 'H:'

DualSpinnerChangeCallback = Callable[[int, int], None]


@dataclass
class DualSpinnerPanelParameters:
    firstLabel:           str                              = DEFAULT_FIRST_LABEL
    secondLabel:          str                              = DEFAULT_SECOND_LABEL
    valueChangedCallback: DualSpinnerChangeCallback | None = None
    minValue:             int                              = DEFAULT_MIN_SPINNER_VALUE
    maxValue:             int                              = DEFAULT_MAX_SPINNER_VALUE
    spinnerWidth:         int                              = DEFAULT_SPINNER_WIDTH


class DualSpinnerPanel(SizedPanel):
    """
    A standalone, reusable horizontal panel containing two labeled SpinCtrl widgets.
    Can be hosted in any container (such as TitledPanel, SizedDialog, or SizedPanel).
    """

    def __init__(self, parent: SizedPanel, parameters: DualSpinnerPanelParameters):
        """
        Initialize the horizontal dual-spinner panel.

        Args:
            parent:     The parent container hosting this panel.
            parameters: Configuration parameters for labels, ranges, width, and callback.
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)
        self.SetSizerType('horizontal')
        self.SetSizerProps(expand=False)

        self._valueChangedCallback: DualSpinnerChangeCallback | None = parameters.valueChangedCallback

        firstStaticText: StaticText = StaticText(self, ID_ANY, parameters.firstLabel)
        firstStaticText.SetSizerProps(valign='centre', border=(('right',), LABEL_SPACING_RIGHT))

        spinnerSize: Size = Size(parameters.spinnerWidth, DEFAULT_SPINNER_HEIGHT)

        self._spinner0: SpinCtrl = SpinCtrl(self, size=spinnerSize)
        self._spinner0.SetRange(parameters.minValue, parameters.maxValue)
        self._spinner0.SetSizerProps(valign='centre', border=(('right',), SPINNER_SPACING_RIGHT))

        secondStaticText: StaticText = StaticText(self, ID_ANY, parameters.secondLabel)
        secondStaticText.SetSizerProps(valign='centre', border=(('right',), LABEL_SPACING_RIGHT))

        self._spinner1: SpinCtrl = SpinCtrl(self, size=spinnerSize)
        self._spinner1.SetRange(parameters.minValue, parameters.maxValue)
        self._spinner1.SetSizerProps(valign='centre')

        self.Bind(EVT_TEXT, self._onSpinnerChanged, self._spinner0)
        self.Bind(EVT_TEXT, self._onSpinnerChanged, self._spinner1)
        self.Bind(EVT_SPINCTRL, self._onSpinnerChanged, self._spinner0)
        self.Bind(EVT_SPINCTRL, self._onSpinnerChanged, self._spinner1)

    @property
    def values(self) -> tuple[int, int]:
        """
        Retrieve current integer values from both spinners.

        Returns:
            Tuple of (firstValue, secondValue).
        """
        currentValues: tuple[int, int] = (self._spinner0.GetValue(), self._spinner1.GetValue())
        return currentValues

    @values.setter
    def values(self, values: tuple[int, int]):
        """
        Set values on both spinners.

        Args:
            values: Tuple of (firstValue, secondValue).
        """
        self._spinner0.SetValue(values[0])
        self._spinner1.SetValue(values[1])

    def SetToolTip(self, tip: str):
        """
        Set tooltip description on the container and both child spin controls.

        Args:
            tip: The tooltip text string.
        """
        super().SetToolTip(tip)
        self._spinner0.SetToolTip(tip)
        self._spinner1.SetToolTip(tip)

    def _onSpinnerChanged(self, _event: CommandEvent):
        """
        Internal handler invoked whenever either spinner value changes.
        """
        if self._valueChangedCallback is not None:
            self._valueChangedCallback(self._spinner0.GetValue(), self._spinner1.GetValue())
