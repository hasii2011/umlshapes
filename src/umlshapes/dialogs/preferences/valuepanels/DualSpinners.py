
from typing import Callable

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import ID_ANY
from wx import EVT_TEXT

from wx import Size
from wx import SpinCtrl
from wx import CommandEvent

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedPanel

SPINNER_WIDTH:  int = 60
SPINNER_HEIGHT: int = 35


@dataclass
class SpinnerValues:
    value0: int = 0
    value1: int = 0


class DualSpinners(SizedPanel):
    """
    A component that pairs two spinners in a horizontal panel;  Callers
    optionally set the minimum and maximum spinner values
    Ideal for subclassing to use as a way to get x,y coordinates or width, height
    sizes

    This is identical to the codeallybasic.ui.widgets.DualSpinnerControl, but this
    is parented by a SizedPanel rather than a SizedStaticBox
    """

    DEFAULT_MIN_VALUE: int = 100
    DEFAULT_MAX_VALUE: int = 300

    def __init__(self, sizedPanel: SizedPanel,
                 valueChangedCallback: Callable,
                 minValue: int = DEFAULT_MIN_VALUE, maxValue: int = DEFAULT_MAX_VALUE,
                 setControlsSize: bool = True,
                 ):
        """

        Args:
            sizedPanel   The parent panel

            valueChangedCallback:  The method to call when the value changes;  The method should expect the
                                   first parameter to be an object of type SpinnerValues
            minValue:       The minimum value for the spinner values
            maxValue:       The maximum value for the spinner values
            setControlsSize:  Whether to specify the spinner size;  This is a hack
            because in some SizedPanels the spinners are appropriately sized and in others they
            are not
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(sizedPanel, ID_ANY)

        self.SetSizerType('horizontal')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self._callback: Callable = valueChangedCallback

        self._wxSpinner0Id: int = wxNewIdRef()
        self._wxSpinner1Id: int = wxNewIdRef()

        if setControlsSize is True:
            self._spinner0: SpinCtrl = SpinCtrl(self, self._wxSpinner0Id, "", size=Size(SPINNER_WIDTH, SPINNER_HEIGHT))
            self._spinner1: SpinCtrl = SpinCtrl(self, self._wxSpinner1Id, "", size=Size(SPINNER_WIDTH, SPINNER_HEIGHT))
        else:
            self._spinner0 = SpinCtrl(self, self._wxSpinner0Id, "")
            self._spinner1 = SpinCtrl(self, self._wxSpinner1Id, "")

        self._spinner0.SetRange(minValue, maxValue)
        self._spinner1.SetRange(minValue, maxValue)

        self._spinnerValues: SpinnerValues = SpinnerValues(minValue, maxValue)
        #
        # Bind to the text control;  Then we can type in or spin
        self.Bind(EVT_TEXT, self._onSpinnerValueChanged, self._spinner0)
        self.Bind(EVT_TEXT, self._onSpinnerValueChanged, self._spinner1)

    def _setSpinnerValues(self, spinnerValues: SpinnerValues):
        """
        Write only;  The appropriate way to retrieve the values is via the change callback
        Args:
            spinnerValues:
        """
        self._spinnerValues = spinnerValues
        self._spinner0.SetValue(spinnerValues.value0)
        self._spinner1.SetValue(spinnerValues.value1)
        self.logger.info(f'range: {self._spinner0.GetRange()} - {self._spinner0.GetValue()=} {self._spinner1.GetValue()=}')

    # noinspection PyTypeChecker
    spinnerValues = property(fset=_setSpinnerValues, doc='Write only property to initialize spinner values')

    def enableControls(self, value: bool):
        """
        Enable or disable the spinner controls

        Args:
            value: `True` to enable, else `False`
        """
        if value is True:
            self._spinner0.Enable()
            self._spinner1.Enable()
        else:
            self._spinner0.Disable()
            self._spinner1.Disable()

    def _onSpinnerValueChanged(self, event: CommandEvent):

        eventId:  int = event.GetId()
        newValue: int = event.GetInt()

        if eventId == self._wxSpinner0Id:
            self._spinnerValues.value0  = newValue
        elif eventId == self._wxSpinner1Id:
            self._spinnerValues.value1  = newValue
        else:
            self.logger.error(f'Unknown spinner event id: {eventId}')

        self._callback(self._spinnerValues)
