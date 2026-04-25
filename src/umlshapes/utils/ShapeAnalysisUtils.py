
from typing import NewType

from logging import Logger
from logging import getLogger
from logging import DEBUG

from enum import StrEnum

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
