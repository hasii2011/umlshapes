from typing import Dict
from typing import NewType
from typing import Union

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlUseCase import UmlUseCase

LinkableUmlShape = Union[UmlClass, UmlNote, UmlActor, UmlUseCase]

LinkableUmlShapes = NewType('LinkableUmlShapes', Dict[int, LinkableUmlShape])

LinkableModelClass = Union[PyutClass, PyutActor, PyutUseCase, PyutNote]


def linkableUmlShapesFactory() -> LinkableUmlShapes:
    return LinkableUmlShapes({})
