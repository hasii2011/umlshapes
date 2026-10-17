
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
