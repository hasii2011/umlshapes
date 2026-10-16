from dataclasses import dataclass

DEFAULT_COLUMN_SPACING: int = 220
DEFAULT_SLOT_HEIGHT:    int = 40
DEFAULT_TOP_PADDING:    int = 20
DEFAULT_BOTTOM_PADDING: int = 40
DEFAULT_START_X:        int = 100
DEFAULT_START_Y:        int = 50


@dataclass
class SDLayoutParameters:
    """
    Configuration parameters for sequence diagram layout calculation.
    """

    columnSpacing: int = DEFAULT_COLUMN_SPACING
    slotHeight:    int = DEFAULT_SLOT_HEIGHT
    topPadding:    int = DEFAULT_TOP_PADDING
    bottomPadding: int = DEFAULT_BOTTOM_PADDING
    startX:        int = DEFAULT_START_X
    startY:        int = DEFAULT_START_Y
