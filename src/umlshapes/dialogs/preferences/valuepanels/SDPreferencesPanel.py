
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_TEXT
from wx import EVT_CHOICE
from wx import EVT_CHECKBOX
from wx import EVT_SPINCTRL
from wx import EVT_SPINCTRLDOUBLE

from wx import CheckBox
from wx import Choice
from wx import CommandEvent
from wx import Size
from wx import SpinCtrl
from wx import SpinCtrlDouble
from wx import SpinDoubleEvent
from wx import ToolTip
from wx import Window

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.TitledPanel import TitledPanel

from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel
from umlshapes.dialogs.preferences.TitledDimensionsControl import TitledDimensionsControl
from umlshapes.dialogs.preferences.TitledDimensionsControl import TitledDimensionsParameters
from umlshapes.sd.SDMessageLabelPlacement import SDMessageLabelPlacement
from umlshapes.types.UmlDimensions import UmlDimensions

POPUP_BUTTON_CHROME_PADDING:             int = 60
DEFAULT_CHOICE_HEIGHT:                   int = -1

MIN_INSTANCE_DIMENSION:                  int = 100
MAX_INSTANCE_DIMENSION:                  int = 1000

MIN_INSTANCE_NAME_RELATIVE_HEIGHT:       float = 0.05
MAX_INSTANCE_NAME_RELATIVE_HEIGHT:       float = 0.95
INCREMENT_INSTANCE_NAME_RELATIVE_HEIGHT: float = 0.05
DIGITS_INSTANCE_NAME_RELATIVE_HEIGHT:    int = 2

MIN_MESSAGE_ARROW_HEAD_SIZE:             float = 4.0
MAX_MESSAGE_ARROW_HEAD_SIZE:             float = 40.0
INCREMENT_MESSAGE_ARROW_HEAD_SIZE:       float = 1.0
DIGITS_MESSAGE_ARROW_HEAD_SIZE:          int = 1

MIN_REFLEXIVE_MESSAGE_WIDTH:             int = 20
MAX_REFLEXIVE_MESSAGE_WIDTH:             int = 150

MIN_TIME_STEP_HEIGHT:                    int = 20
MAX_TIME_STEP_HEIGHT:                    int = 200

MIN_INITIAL_LIFELINE_LENGTH:             int = 100
MAX_INITIAL_LIFELINE_LENGTH:             int = 2000

INSTANCE_POSITION_TOOLTIP:               str = 'The default vertical (Y) coordinate where sequence diagram instance headers are placed'
INSTANCE_DIMENSIONS_TOOLTIP:             str = 'The default width and height of sequence diagram instance header shapes'
INSTANCE_NAME_RELATIVE_HEIGHT_TOOLTIP:   str = 'Ratio of instance header height allocated to the participant name text compartment'
LABEL_PLACEMENT_TOOLTIP:                 str = 'Determines how message labels are positioned along message lines (Centered, Proportional, or Fixed)'
MESSAGE_ARROW_HEAD_SIZE_TOOLTIP:         str = 'Size of arrowheads on sequence diagram message lines'
REFLEXIVE_MESSAGE_WIDTH_TOOLTIP:         str = 'Width in pixels of sequence diagram reflexive message loops'
TIME_STEP_HEIGHT_TOOLTIP:                str = 'Vertical spacing in pixels between sequence diagram message time steps'
INITIAL_LIFELINE_LENGTH_TOOLTIP:         str = 'Default starting length in pixels for new instance lifelines'
AUTO_GROW_LIFELINES_TOOLTIP:             str = 'Automatically extend lifeline length when messages are placed or dragged beyond the current bottom'
UNIFORM_LIFELINE_LENGTH_TOOLTIP:         str = 'Keep all lifelines at equal length when any lifeline is resized or auto-grown'


class SDPreferencesPanel(BasePreferencesPanel):

    def __init__(self, parent: Window):

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent)
        self.SetSizerType('vertical')

        self._instancePosition:           SpinCtrl                = cast(SpinCtrl, None)                # noqa
        self._instanceDimensions:         TitledDimensionsControl = cast(TitledDimensionsControl, None) # noqa
        self._instanceNameRelativeHeight: SpinCtrlDouble          = cast(SpinCtrlDouble, None)          # noqa
        self._labelPlacementChoice:       Choice                  = cast(Choice, None)                  # noqa
        self._messageArrowHeadSize:       SpinCtrlDouble          = cast(SpinCtrlDouble, None)          # noqa
        self._reflexiveMessageWidth:      SpinCtrl                = cast(SpinCtrl, None)                # noqa
        self._timeStepHeight:             SpinCtrl                = cast(SpinCtrl, None)                # noqa
        self._initialLifeLineLength:      SpinCtrl                = cast(SpinCtrl, None)                # noqa
        self._autoGrowLifeLines:          CheckBox                = cast(CheckBox, None)                # noqa
        self._uniformLifeLineLength:      CheckBox                = cast(CheckBox, None)                # noqa

        self._layoutControls(parentSizedPanel=self)
        self._setControlValues()

    def _layoutControls(self, parentSizedPanel: SizedPanel):

        instanceRow: SizedPanel = SizedPanel(parentSizedPanel)
        instanceRow.SetSizerType('horizontal')
        instanceRow.SetSizerProps(expand=False)

        self._layoutInstancePositionControl(parentSizedPanel=instanceRow)

        dimensionsParameters: TitledDimensionsParameters = TitledDimensionsParameters(
            titleLabel='Instance Width/Height',
            minValue=MIN_INSTANCE_DIMENSION,
            maxValue=MAX_INSTANCE_DIMENSION,
            valueChangedCallback=self._noteDimensionsChanged
        )
        self._instanceDimensions = TitledDimensionsControl(parent=instanceRow, parameters=dimensionsParameters)
        self._instanceDimensions.SetToolTip(ToolTip(INSTANCE_DIMENSIONS_TOOLTIP))

        instanceNameRow: SizedPanel = SizedPanel(parentSizedPanel)
        instanceNameRow.SetSizerType('horizontal')
        instanceNameRow.SetSizerProps(expand=False)

        self._layoutInstanceNameRelativeHeightControl(parentSizedPanel=instanceNameRow)

        messageRow: SizedPanel = SizedPanel(parentSizedPanel)
        messageRow.SetSizerType('horizontal')
        messageRow.SetSizerProps(expand=False)

        self._layoutLabelPlacementControl(parentSizedPanel=messageRow)
        self._layoutMessageArrowHeadSizeControl(parentSizedPanel=messageRow)
        self._layoutReflexiveMessageWidthControl(parentSizedPanel=messageRow)
        self._layoutTimeStepHeightControl(parentSizedPanel=messageRow)

        lifelineRow: SizedPanel = SizedPanel(parentSizedPanel)
        lifelineRow.SetSizerType('horizontal')
        lifelineRow.SetSizerProps(expand=False)

        self._layoutInitialLifeLineLengthControl(parentSizedPanel=lifelineRow)
        self._layoutLifelinePreferences(parentSizedPanel=lifelineRow)

    def _layoutLabelPlacementControl(self, parentSizedPanel: SizedPanel):

        placementPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Message Label Placement')
        placementPanel.SetSizerProps(expand=False)

        choices: list[str] = [p.value for p in SDMessageLabelPlacement]

        self._labelPlacementChoice = Choice(placementPanel, choices=choices)
        minWidth: int = self._computeMinChoiceWidth(choiceControl=self._labelPlacementChoice, choices=choices)
        self._labelPlacementChoice.SetMinSize(Size(width=minWidth, height=DEFAULT_CHOICE_HEIGHT))
        self._labelPlacementChoice.SetSizerProps(expand=True)
        self._labelPlacementChoice.SetToolTip(LABEL_PLACEMENT_TOOLTIP)
        self.Bind(EVT_CHOICE, self._onPlacementChanged, self._labelPlacementChoice)

    def _computeMinChoiceWidth(self, choiceControl: Choice, choices: list[str]) -> int:
        """
        Compute the minimum required pixel width to display all choice options
        without ellipsis truncation, accounting for font metrics and macOS popup chrome.

        Args:
            choiceControl: The Choice control whose active font metrics are queried.
            choices:       List of choice label strings to measure.

        Returns:
            The minimum required width in pixels.
        """
        maxTextWidth: int = 0
        for choiceText in choices:
            textWidth: int
            textWidth, _ = choiceControl.GetTextExtent(choiceText)
            if textWidth > maxTextWidth:
                maxTextWidth = textWidth

        minWidth: int = maxTextWidth + POPUP_BUTTON_CHROME_PADDING
        return minWidth

    def _layoutLifelinePreferences(self, parentSizedPanel: SizedPanel):

        lifelinePanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Lifelines')
        lifelinePanel.SetSizerProps(expand=False)

        self._autoGrowLifeLines     = CheckBox(parent=lifelinePanel, label='Auto-grow Lifelines')
        self._autoGrowLifeLines.SetToolTip(AUTO_GROW_LIFELINES_TOOLTIP)
        self._uniformLifeLineLength = CheckBox(parent=lifelinePanel, label='Uniform Lifeline Length')
        self._uniformLifeLineLength.SetToolTip(UNIFORM_LIFELINE_LENGTH_TOOLTIP)

        self.Bind(EVT_CHECKBOX, self._onAutoGrowChanged, self._autoGrowLifeLines)
        self.Bind(EVT_CHECKBOX, self._onUniformLengthChanged, self._uniformLifeLineLength)

    def _setControlValues(self):
        """
        """
        self._instancePosition.SetValue(self._preferences.instanceYPosition)
        width:  int = self._preferences.instanceDimensions.width
        height: int = self._preferences.instanceDimensions.height
        self._instanceDimensions.dimensions = Dimensions(width=width, height=height)
        self._instanceNameRelativeHeight.SetValue(self._preferences.instanceNameRelativeHeight)

        currentPlacement: SDMessageLabelPlacement = self._preferences.messageLabelPlacement
        self._labelPlacementChoice.SetStringSelection(currentPlacement.value)
        self._messageArrowHeadSize.SetValue(self._preferences.messageArrowHeadSize)
        self._reflexiveMessageWidth.SetValue(self._preferences.reflexiveMessageWidth)
        self._timeStepHeight.SetValue(self._preferences.timeStepHeight)

        self._initialLifeLineLength.SetValue(self._preferences.initialLifeLineLength)
        self._autoGrowLifeLines.SetValue(self._preferences.autoGrowLifeLines)
        self._uniformLifeLineLength.SetValue(self._preferences.uniformLifeLineLength)

    def _layoutInstanceNameRelativeHeightControl(self, parentSizedPanel: SizedPanel):

        nameHeightPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Instance Name Height Ratio')
        nameHeightPanel.SetSizerProps(expand=False)

        self._instanceNameRelativeHeight = SpinCtrlDouble(
            parent=nameHeightPanel,
            min=MIN_INSTANCE_NAME_RELATIVE_HEIGHT,
            max=MAX_INSTANCE_NAME_RELATIVE_HEIGHT,
            initial=self._preferences.instanceNameRelativeHeight,
            inc=INCREMENT_INSTANCE_NAME_RELATIVE_HEIGHT
        )
        self._instanceNameRelativeHeight.SetDigits(DIGITS_INSTANCE_NAME_RELATIVE_HEIGHT)
        self._instanceNameRelativeHeight.SetToolTip(INSTANCE_NAME_RELATIVE_HEIGHT_TOOLTIP)
        self.Bind(EVT_SPINCTRLDOUBLE, self._onInstanceNameRelativeHeightChanged, self._instanceNameRelativeHeight)

    def _layoutMessageArrowHeadSizeControl(self, parentSizedPanel: SizedPanel):

        arrowHeadPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Arrowhead Size')
        arrowHeadPanel.SetSizerProps(expand=False)

        self._messageArrowHeadSize = SpinCtrlDouble(
            parent=arrowHeadPanel,
            min=MIN_MESSAGE_ARROW_HEAD_SIZE,
            max=MAX_MESSAGE_ARROW_HEAD_SIZE,
            initial=self._preferences.messageArrowHeadSize,
            inc=INCREMENT_MESSAGE_ARROW_HEAD_SIZE
        )
        self._messageArrowHeadSize.SetDigits(DIGITS_MESSAGE_ARROW_HEAD_SIZE)
        self._messageArrowHeadSize.SetToolTip(MESSAGE_ARROW_HEAD_SIZE_TOOLTIP)
        self.Bind(EVT_SPINCTRLDOUBLE, self._onMessageArrowHeadSizeChanged, self._messageArrowHeadSize)

    def _layoutReflexiveMessageWidthControl(self, parentSizedPanel: SizedPanel):

        widthPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Reflexive Message Width')
        widthPanel.SetSizerProps(expand=False)

        self._reflexiveMessageWidth = SpinCtrl(
            parent=widthPanel,
            min=MIN_REFLEXIVE_MESSAGE_WIDTH,
            max=MAX_REFLEXIVE_MESSAGE_WIDTH,
            initial=self._preferences.reflexiveMessageWidth
        )
        self._reflexiveMessageWidth.SetToolTip(REFLEXIVE_MESSAGE_WIDTH_TOOLTIP)
        self.Bind(EVT_SPINCTRL, self._onReflexiveMessageWidthChanged, self._reflexiveMessageWidth)
        self.Bind(EVT_TEXT, self._onReflexiveMessageWidthChanged, self._reflexiveMessageWidth)

    def _layoutTimeStepHeightControl(self, parentSizedPanel: SizedPanel):

        timeStepPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Time Step Height')
        timeStepPanel.SetSizerProps(expand=False)

        self._timeStepHeight = SpinCtrl(
            parent=timeStepPanel,
            min=MIN_TIME_STEP_HEIGHT,
            max=MAX_TIME_STEP_HEIGHT,
            initial=self._preferences.timeStepHeight
        )
        self._timeStepHeight.SetToolTip(TIME_STEP_HEIGHT_TOOLTIP)
        self.Bind(EVT_SPINCTRL, self._onTimeStepHeightChanged, self._timeStepHeight)
        self.Bind(EVT_TEXT, self._onTimeStepHeightChanged, self._timeStepHeight)

    def _layoutInitialLifeLineLengthControl(self, parentSizedPanel: SizedPanel):

        lengthPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Initial Lifeline Length')
        lengthPanel.SetSizerProps(expand=False)

        self._initialLifeLineLength = SpinCtrl(
            parent=lengthPanel,
            min=MIN_INITIAL_LIFELINE_LENGTH,
            max=MAX_INITIAL_LIFELINE_LENGTH,
            initial=self._preferences.initialLifeLineLength
        )
        self._initialLifeLineLength.SetToolTip(INITIAL_LIFELINE_LENGTH_TOOLTIP)
        self.Bind(EVT_SPINCTRL, self._onInitialLifeLineLengthChanged, self._initialLifeLineLength)
        self.Bind(EVT_TEXT, self._onInitialLifeLineLengthChanged, self._initialLifeLineLength)

    def _layoutInstancePositionControl(self, parentSizedPanel: SizedPanel):

        positionPanel: TitledPanel = TitledPanel(parent=parentSizedPanel, titleLabel='Instance Position')
        positionPanel.SetSizerProps(expand=False)
        self._instancePosition = SpinCtrl(parent=positionPanel)
        self._instancePosition.SetToolTip(INSTANCE_POSITION_TOOLTIP)

        # Bind to the text control;  Then we can type in or spin
        self.Bind(EVT_TEXT, self._onPositionsChanged, self._instancePosition)

    def _onPositionsChanged(self, event: CommandEvent):

        newValue: int = event.GetInt()
        self._preferences.instanceYPosition = newValue

    def _onPlacementChanged(self, event: CommandEvent):

        selectedString: str = event.GetString()
        self._preferences.messageLabelPlacement = SDMessageLabelPlacement(selectedString)

    def _onAutoGrowChanged(self, event: CommandEvent):

        newValue: bool = event.IsChecked()
        self._preferences.autoGrowLifeLines = newValue

    def _onUniformLengthChanged(self, event: CommandEvent):

        newValue: bool = event.IsChecked()
        self._preferences.uniformLifeLineLength = newValue

    def _noteDimensionsChanged(self, newValue: Dimensions):
        self._preferences.instanceDimensions = UmlDimensions(width=newValue.width, height=newValue.height)

    def _onInstanceNameRelativeHeightChanged(self, event: SpinDoubleEvent):

        newValue: float = event.GetValue()
        self._preferences.instanceNameRelativeHeight = newValue

    def _onMessageArrowHeadSizeChanged(self, event: SpinDoubleEvent):

        newValue: float = event.GetValue()
        self._preferences.messageArrowHeadSize = newValue

    def _onReflexiveMessageWidthChanged(self, _event: CommandEvent):

        newValue: int = self._reflexiveMessageWidth.GetValue()
        self._preferences.reflexiveMessageWidth = newValue

    def _onTimeStepHeightChanged(self, _event: CommandEvent):

        newValue: int = self._timeStepHeight.GetValue()
        self._preferences.timeStepHeight = newValue

    def _onInitialLifeLineLengthChanged(self, _event: CommandEvent):

        newValue: int = self._initialLifeLineLength.GetValue()
        self._preferences.initialLifeLineLength = newValue
