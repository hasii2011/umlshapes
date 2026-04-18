
from typing import Dict
from typing import List
from typing import NewType

from dataclasses import dataclass

from umlshapes.lib.ogl import Shape

from umlshapes.ShapeTypes import UmlShapeGenre

from umlshapes.types.UmlPosition import UmlPosition


@dataclass
class ShapeMovedInfo:
    umlShape:         UmlShapeGenre
    originalPosition: UmlPosition


ShapeList   = NewType('ShapeList', List[Shape])
ShapeId     = NewType('ShapeId', str)
MovedShapes = NewType('MovedShapes', Dict[ShapeId, ShapeMovedInfo])
