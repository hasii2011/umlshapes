
from typing import cast

from dataclasses import dataclass

from wx import Point

from umlshapes.types.Common import UmlShape


@dataclass
class UmlShapeSelectedData:

    shape:    UmlShape = cast(UmlShape, None)
    position: Point    = cast(Point, None)
