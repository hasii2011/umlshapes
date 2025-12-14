
from typing import Dict
from typing import List
from typing import NewType
from typing import Union

from umlmodel.Actor import Actor
from umlmodel.Class import Class
from umlmodel.Note import Note
from umlmodel.UseCase import UseCase

from umlshapes.links.UmlNoteLink import UmlNoteLink
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

LinkableUmlShapes = NewType('LinkableUmlShapes', Dict[str, LinkableUmlShape])

LinkableModelClass = Union[Class, Actor, UseCase, Note]


def linkableUmlShapesFactory() -> LinkableUmlShapes:
    return LinkableUmlShapes({})


UmlShape = UmlActor | UmlClass | UmlNote | UmlText | UmlUseCase

UmlShapeGenre = UmlActor | UmlClass | UmlNote | UmlText | UmlUseCase
UmlLinkGenre  = UmlInheritance | UmlInterface | UmlAssociation | UmlComposition | UmlAggregation | UmlNoteLink


UmlAssociationGenre = UmlAssociation | UmlComposition | UmlAggregation

UmlShapes = NewType('UmlShapes', List[UmlShapeGenre | UmlLinkGenre])
UmlLinks  = NewType('UmlLinks',  List[UmlLinkGenre])


def umlShapesFactory() -> UmlShapes:
    return UmlShapes([])
