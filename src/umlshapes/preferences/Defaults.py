
from umlshapes.links.UmlAssociationLabelFormat import UmlAssociationLabelFormat

from umlshapes.types.UmlDimensions import UmlDimensions

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720

DEFAULT_ASSOCIATION_LABEL_SIZE:   str = str(UmlDimensions(width=75, height=24))

DEFAULT_ASSOCIATION_LABEL_FORMAT: str = (
    f'{UmlAssociationLabelFormat.FORMAT_CENTER_HORIZONTAL.value},'
    f'{UmlAssociationLabelFormat.FORMAT_CENTER_VERTICAL.value}'
)
