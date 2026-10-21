from dataclasses import dataclass

from typing import Callable

from logging import Logger
from logging import getLogger

from wx import ToolTip

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.TitledPanel import TitledPanel

from umlshapes.dialogs.preferences.DualSpinnerPanel import DualSpinnerPanel
from umlshapes.dialogs.preferences.DualSpinnerPanel import DualSpinnerPanelParameters

DEFAULT_MIN_DIMENSION: int = 100
DEFAULT_MAX_DIMENSION: int = 1000
DEFAULT_SPINNER_WIDTH: int = 80
DEFAULT_FIRST_LABEL:   str = 'W:'
DEFAULT_SECOND_LABEL:  str = 'H:'

DimensionsChangeCallback = Callable[[Dimensions], None]


@dataclass
class TitledDimensionsParameters:
    titleLabel:           str
    valueChangedCallback: DimensionsChangeCallback | None = None
    minValue:             int                             = DEFAULT_MIN_DIMENSION
    maxValue:             int                             = DEFAULT_MAX_DIMENSION
    spinnerWidth:         int                             = DEFAULT_SPINNER_WIDTH
    firstLabel:           str                             = DEFAULT_FIRST_LABEL
    secondLabel:          str                             = DEFAULT_SECOND_LABEL


class TitledDimensionsControl(TitledPanel):
    """
    A paired width and height dual-spinner control encapsulated inside a TitledPanel.
    Harmonizes with other TitledPanel preference sections in styling and font size.
    """

    def __init__(self, parent: SizedPanel, parameters: TitledDimensionsParameters):
        """
        Initialize the titled dimensions control embedding a DualSpinnerPanel.

        Args:
            parent:     The parent container hosting this panel.
            parameters: Configuration parameters including title label, ranges, and callback.
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, titleLabel=parameters.titleLabel)
        self.SetSizerProps(expand=False)

        self._valueChangedCallback: DimensionsChangeCallback | None = parameters.valueChangedCallback

        dualSpinnerParameters: DualSpinnerPanelParameters = DualSpinnerPanelParameters(
            firstLabel=parameters.firstLabel,
            secondLabel=parameters.secondLabel,
            valueChangedCallback=self._onSpinnerValuesChanged,
            minValue=parameters.minValue,
            maxValue=parameters.maxValue,
            spinnerWidth=parameters.spinnerWidth
        )
        self._dualSpinnerPanel: DualSpinnerPanel = DualSpinnerPanel(
            parent=self,
            parameters=dualSpinnerParameters
        )

    @property
    def dimensions(self) -> Dimensions:
        """
        Retrieve current width and height dimensions from the embedded dual spinner panel.

        Returns:
            Dimensions containing current width and height.
        """
        width: int
        height: int
        width, height = self._dualSpinnerPanel.values
        currentDimensions: Dimensions = Dimensions(width=width, height=height)
        return currentDimensions

    @dimensions.setter
    def dimensions(self, dimensions: Dimensions):
        """
        Update the dual spinner panel with the given dimensions.

        Args:
            dimensions: The new Dimensions values to set.
        """
        self._dualSpinnerPanel.values = (dimensions.width, dimensions.height)

    def SetToolTip(self, tip: ToolTip):
        """
        Set tooltip description across the titled container and embedded spinners.

        Args:
            tip: The tooltip instance.
        """
        super().SetToolTip(tip)
        self._dualSpinnerPanel.SetToolTip(tip)

    def _onSpinnerValuesChanged(self, firstValue: int, secondValue: int):
        """
        Internal handler invoked whenever embedded spinners change, forwarding Dimensions.
        """
        if self._valueChangedCallback is not None:
            newDimensions: Dimensions = Dimensions(width=firstValue, height=secondValue)
            self._valueChangedCallback(newDimensions)
