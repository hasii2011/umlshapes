
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from dataclasses import dataclass

from wx.lib.ogl import Shape

from umlshapes.ShapeTypes import MoveableUmlShape
from umlshapes.links.UmlLink import UmlLink

from umlshapes.types.Common import EndPositions
from umlshapes.types.UmlPosition import NO_POSITION
from umlshapes.types.UmlPosition import NO_POSITIONS
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions

NO_END_POSITIONS: EndPositions = cast(EndPositions, None)       # noqa


@dataclass
class ShapeMoveInfo:
    umlShape:         MoveableUmlShape
    originalPosition: UmlPosition = NO_POSITION
    finalPosition:    UmlPosition = NO_POSITION


@dataclass
class LinkMoveInfo:
    umlLink:               UmlLink
    originalBendPositions: UmlPositions = NO_POSITIONS
    finalBendPositions:    UmlPositions = NO_POSITIONS
    originalEndPositions:  EndPositions = NO_END_POSITIONS
    finalEndPositions:     EndPositions = NO_END_POSITIONS


ShapeList   = NewType('ShapeList', List[Shape])
ShapeId     = NewType('ShapeId', str)
LinkId      = NewType('LinkId', str)
MovedShapes = NewType('MovedShapes', Dict[ShapeId, ShapeMoveInfo])
MovedLinks  = NewType('MovedLinks', Dict[LinkId, LinkMoveInfo])
