
from typing import cast

from dataclasses import dataclass

from wx import Point

from umlshapes.ShapeTypes import UmlShapeGenre


@dataclass
class UmlShapeSelectedData:

    shape:    UmlShapeGenre = cast(UmlShapeGenre, None)
    position: Point         = cast(Point, None)
