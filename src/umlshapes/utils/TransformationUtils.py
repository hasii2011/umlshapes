
from typing import Tuple

from umlshapes.types.Common import Rectangle
from umlshapes.types.UmlPosition import UmlPosition


class TransformationUtils:

    @classmethod
    def convertToAbsoluteCoordinates(cls, relativePosition: UmlPosition, rectangle: Rectangle) -> UmlPosition:

        left: int = rectangle.left      # x
        top: int = rectangle.top        # y

        absoluteX: int = relativePosition.x + left
        absoluteY: int = relativePosition.y + top

        absoluteCoordinates: UmlPosition = UmlPosition(x=absoluteX, y=absoluteY)

        return absoluteCoordinates

    @classmethod
    def convertToRelativeCoordinates(cls, absolutePosition: UmlPosition, rectangle: Rectangle) -> UmlPosition:

        left: int = rectangle.left      # x
        top: int = rectangle.top        # y

        relativeX: int = absolutePosition.x - left
        relativeY: int = absolutePosition.y - top

        relativeCoordinates: UmlPosition = UmlPosition(x=relativeX, y=relativeY)
        return relativeCoordinates

    @staticmethod
    def snapCoordinatesToGrid(x: int, y: int, gridInterval: int) -> Tuple[int, int]:

        xDiff: float = x % gridInterval
        yDiff: float = y % gridInterval

        snappedX: int = round(x - xDiff)
        snappedY: int = round(y - yDiff)

        return snappedX, snappedY
