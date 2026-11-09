
from dataclasses import dataclass

from wx import Point

from umlshapes.ShapeTypes import UmlShapeGenre


@dataclass
class UmlShapeSelectedData:

    shape:    UmlShapeGenre
    position: Point
