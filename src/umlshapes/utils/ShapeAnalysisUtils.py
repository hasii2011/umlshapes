
from typing import NewType

from logging import Logger
from logging import getLogger
from logging import DEBUG

from enum import StrEnum

from math import atan2
from math import degrees

from umlshapes.types.Common import Rectangle
from umlshapes.types.UmlPosition import UmlPosition

from dataclasses import dataclass

Degrees = NewType('Degrees', float)


class LeftTopRectangleIndicator(StrEnum):
    RECTANGLE_1 = 'Rectangle 1'
    RECTANGLE_2 = 'Rectangle 2'
    NotSet      = 'Not Set'


@dataclass
class RelativeRectangleResult:
    leftMostTopMostShape: LeftTopRectangleIndicator = LeftTopRectangleIndicator.NotSet
    isOtherToRight:   bool    = False
    isOtherToBottom:  bool    = False
    directionToOther: Degrees = Degrees(0.0)


class ShapeAnalysisUtils:
    clsLogger: Logger = getLogger(__name__)

    @classmethod
    def identifyLeftMostTopMostRectangle(cls, rectangle1: Rectangle, rectangle2: Rectangle) -> tuple[Rectangle, Rectangle, LeftTopRectangleIndicator]:
        """
        Identify the leftmost/topmost shape

        Args:
            rectangle1:
            rectangle2:

        Returns:  A tuple that has the values leftTopRectangle, otherRectangle, leftTopIndicator

        """

        if rectangle1.left < rectangle2.left:
            leftTopRectangle, otherRectangle, leftTopIndicator = rectangle1, rectangle2, LeftTopRectangleIndicator.RECTANGLE_1
        elif rectangle2.left < rectangle1.left:
            leftTopRectangle, otherRectangle, leftTopIndicator = rectangle2, rectangle1, LeftTopRectangleIndicator.RECTANGLE_2
        else:
            # Same left coordinate, use top coordinate as tie-breaker
            if rectangle1.top <= rectangle2.top:
                leftTopRectangle, otherRectangle, leftTopIndicator = rectangle1, rectangle2, LeftTopRectangleIndicator.RECTANGLE_1
            else:
                leftTopRectangle, otherRectangle, leftTopIndicator = rectangle2, rectangle1, LeftTopRectangleIndicator.RECTANGLE_2

        return leftTopRectangle, otherRectangle, leftTopIndicator

    @classmethod
    def computeMidPoint(cls, srcPosition: UmlPosition, dstPosition: UmlPosition) -> UmlPosition:
        """

        Args:
            srcPosition:        Tuple x,y source position
            dstPosition:       Tuple x,y destination position

        Returns:
                A tuple that is the x,y position between `srcPosition` and `dstPosition`

            [Reference]: https://mathbitsnotebook.com/Geometry/CoordinateGeometry/CGmidpoint.html
        """
        if ShapeAnalysisUtils.clsLogger.isEnabledFor(DEBUG):
            ShapeAnalysisUtils.clsLogger.debug(f'{srcPosition=}  {dstPosition=}')
        x1 = srcPosition.x
        y1 = srcPosition.y
        x2 = dstPosition.x
        y2 = dstPosition.y

        midPointX = abs(x1 + x2) // 2
        midPointY = abs(y1 + y2) // 2

        return UmlPosition(x=midPointX, y=midPointY)

    @classmethod
    def computeRelativeRectanglePosition(cls, rectangle1: Rectangle, rectangle2: Rectangle) -> RelativeRectangleResult:
        """
        Computes the relative position and direction between two LTRB rectangles.
        Identifies the leftmost and topmost rectangle and computes direction
        towards the other rectangle.

        Note:  This code initially authored by Gemini.   I feel so dirty
        Args:
            rectangle1: First rectangle definition
            rectangle2: Second rectangle definition

        Returns:
                A RectangleRelativeResult dataclass
        """
        leftTopRectangle, otherRectangle, leftTopIndicator = ShapeAnalysisUtils.identifyLeftMostTopMostRectangle(rectangle1=rectangle1, rectangle2=rectangle2)

        # Relative positioning: Is otherRectangle to the right/bottom of primary?
        # Based on simple coordinate comparison
        isOtherToRight:  bool = otherRectangle.left > leftTopRectangle.left
        isOtherToBottom: bool = otherRectangle.top > leftTopRectangle.top

        # Centers for direction calculation
        leftTopCenterX: float = (leftTopRectangle.left + leftTopRectangle.right) / 2.0
        leftTopCenterY: float = (leftTopRectangle.top + leftTopRectangle.bottom) / 2.0
        otherCenterX:   float = (otherRectangle.left + otherRectangle.right) / 2.0
        otherCenterY:   float = (otherRectangle.top + otherRectangle.bottom) / 2.0

        dx:    float = otherCenterX - leftTopCenterX
        dy:    float = otherCenterY - leftTopCenterY
        angle: float = degrees(atan2(dy, dx))

        # Convert to 0-360 degree value
        # 0° = Right
        # 90° = Down
        # 180° = Left
        # 270° = Up
        direction: Degrees = Degrees((angle + 360) % 360)

        result: RelativeRectangleResult = RelativeRectangleResult()

        result.leftMostTopMostShape = leftTopIndicator
        result.isOtherToRight   = isOtherToRight
        result.isOtherToBottom  = isOtherToBottom
        result.directionToOther = direction

        return result
