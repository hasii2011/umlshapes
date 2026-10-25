
from umlshapes.links.UmlAssociationLabelFormat import UmlAssociationLabelFormat
from umlshapes.sd.SDMessageLabelPlacement import SDMessageLabelPlacement

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPenStyle import UmlPenStyle

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720

DEFAULT_ASSOCIATION_LABEL_SIZE:   str = str(UmlDimensions(width=75, height=24))

DEFAULT_ASSOCIATION_LABEL_FORMAT: str = (
    f'{UmlAssociationLabelFormat.FORMAT_CENTER_HORIZONTAL.value},'
    f'{UmlAssociationLabelFormat.FORMAT_CENTER_VERTICAL.value}'
)

DEFAULT_MESSAGE_LABEL_PLACEMENT: str = SDMessageLabelPlacement.PROPORTIONAL.value

DEFAULT_AUTO_GROW_LIFELINES:     bool = True
DEFAULT_UNIFORM_LIFELINE_LENGTH: bool = True

DEFAULT_BACKGROUND_COLOR:           str = UmlColor.WHITE.value
DEFAULT_DARK_MODE_BACKGROUND_COLOR: str = UmlColor.DIM_GREY.value

DEFAULT_GRID_LINE_COLOR:           str = UmlColor.AF_BLUE.value
DEFAULT_DARK_MODE_GRID_LINE_COLOR: str = UmlColor.WHITE.value

DEFAULT_CLASS_BACKGROUND_COLOR: str = UmlColor.MINT_CREAM.value
DEFAULT_CLASS_TEXT_COLOR:       str = UmlColor.BLACK.value
DEFAULT_GRID_LINE_STYLE:        str = UmlPenStyle.DOT.value

# When the text value is selected
DEFAULT_TEXT_BACKGROUND_COLOR:  str = UmlColor.WHITE.value

DEFAULT_USE_CASE_SIZE: str = str(UmlDimensions(width=100, height=60))
DEFAULT_ACTOR_SIZE:    str = str(UmlDimensions(width=80, height=100))

DEFAULT_SD_INSTANCE_DIMENSIONS:    str   = str(UmlDimensions(100, 400))
DEFAULT_NAME_RELATIVE_HEIGHT:      float = 0.10
DEFAULT_LIFE_LINE_LENGTH:          int   = 360
DEFAULT_INSTANCE_Y:                int   = 50
DEFAULT_TIME_STEP_HEIGHT:          int   = 40
DEFAULT_REFLEXIVE_MESSAGE_WIDTH:   int   = 50
MIN_REFLEXIVE_MESSAGE_WIDTH:       int   = 20
MAX_REFLEXIVE_MESSAGE_WIDTH:       int   = 150
DEFAULT_EXECUTION_WIDTH:          int   = 14
MIN_EXECUTION_WIDTH:              int   = 8
MAX_EXECUTION_WIDTH:              int   = 40
DEFAULT_EXECUTION_SHIFT_DELTA:    int   = 7
DEFAULT_AUTO_GENERATE_EXECUTIONS:   bool  = True
DEFAULT_LOST_FOUND_MESSAGE_LENGTH: int   = 80
DEFAULT_LOST_FOUND_CIRCLE_RADIUS:  int   = 5
DEFAULT_FRAGMENT_HEADER_WIDTH:     int   = 50
DEFAULT_FRAGMENT_HEADER_HEIGHT:    int   = 20
DEFAULT_FRAGMENT_PADDING:          int   = 15
