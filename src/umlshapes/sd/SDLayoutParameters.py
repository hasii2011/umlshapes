from dataclasses import dataclass

DEFAULT_COLUMN_SPACING:          int = 220
DEFAULT_TIME_STEP_HEIGHT:        int = 40
DEFAULT_TOP_PADDING:             int = 20
DEFAULT_BOTTOM_PADDING:          int = 40
DEFAULT_START_X:                 int = 100
DEFAULT_START_Y:                 int = 50
DEFAULT_REFLEXIVE_MESSAGE_WIDTH: int = 50


@dataclass
class SDLayoutParameters:
    """
    Configuration parameters for sequence diagram layout calculation.
    """

    columnSpacing:         int = DEFAULT_COLUMN_SPACING
    timeStepHeight:        int = DEFAULT_TIME_STEP_HEIGHT
    topPadding:            int = DEFAULT_TOP_PADDING
    bottomPadding:         int = DEFAULT_BOTTOM_PADDING
    startX:                int = DEFAULT_START_X
    startY:                int = DEFAULT_START_Y
    reflexiveMessageWidth: int = DEFAULT_REFLEXIVE_MESSAGE_WIDTH
