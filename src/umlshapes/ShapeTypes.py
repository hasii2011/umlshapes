
from typing import Dict
from typing import List
from typing import NewType
from typing import Union

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase


LinkableUmlShape = UmlClass | UmlNote | UmlActor | UmlUseCase

LinkableUmlShapes = NewType('LinkableUmlShapes', Dict[int, LinkableUmlShape])

LinkableModelClass = Union[PyutClass, PyutActor, PyutUseCase, PyutNote]


def linkableUmlShapesFactory() -> LinkableUmlShapes:
    return LinkableUmlShapes({})

UmlShape = UmlActor | UmlClass | UmlNote | UmlText | UmlUseCase

UmlShapeGenre = UmlActor | UmlClass | UmlNote | UmlText | UmlUseCase
UmlLinkGenre  = UmlInheritance | UmlInterface | UmlAssociation | UmlComposition | UmlAggregation

UmlAssociationGenre = UmlAssociation | UmlComposition | UmlAggregation

UmlShapes = NewType('UmlShapes', List[UmlShapeGenre | UmlLinkGenre])
UmlLinks  = NewType('UmlLinks',  List[UmlLinkGenre])


def umlShapesFactory() -> UmlShapes:
    return UmlShapes([])
