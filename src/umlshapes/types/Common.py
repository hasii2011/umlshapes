
from typing import List
from typing import NewType
from typing import TYPE_CHECKING
from typing import Union
from typing import cast

from dataclasses import dataclass

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutText import PyutText
from pyutmodelv2.PyutUseCase import PyutUseCase


if TYPE_CHECKING:
    from umlshapes.shapes.UmlActor import UmlActor                  # noqa
    from umlshapes.shapes.UmlClass import UmlClass                  # noqa
    from umlshapes.shapes.UmlNote import UmlNote                    # noqa
    from umlshapes.shapes.UmlText import UmlText                    # noqa
    from umlshapes.shapes.UmlUseCase import UmlUseCase              # noqa
    from umlshapes.links.UmlAssociation import UmlAssociation       # noqa
    from umlshapes.links.UmlAggregation import UmlAggregation       # noqa
    from umlshapes.links.UmlComposition import UmlComposition       # noqa
    from umlshapes.links.UmlInterface import UmlInterface           # noqa
    from umlshapes.links.UmlInheritance import UmlInheritance       # noqa
    from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface    # noqa

ModelObject = Union[PyutText, PyutNote, PyutActor, PyutClass, PyutUseCase, PyutLink, PyutInterface, None]


NOT_SET_INT: int = cast(int, None)
TAB:         str = '\t'


@dataclass
class LeftCoordinate:
    x: int = 0
    y: int = 0


UmlShape = Union[
    'UmlActor', 'UmlClass', 'UmlNote', 'UmlText', 'UmlUseCase',
]
UmlRelationShips = Union[
    'UmlAssociation', 'UmlAggregation', 'UmlComposition', 'UmlInterface', 'UmlInheritance', 'UmlLollipopInterface',
]
UmlShapeList = NewType('UmlShapeList', List[UmlShape])

NAME_IDX:                    int = 0
SOURCE_CARDINALITY_IDX:      int = 1
DESTINATION_CARDINALITY_IDX: int = 2
