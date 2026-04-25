
from logging import Logger
from logging import getLogger

from umlshapes.types.Common import Rectangle
from umlshapes.types.UmlLine import UmlLine
from umlshapes.types.UmlPosition import UmlPoint


class CoordinateUtils:
    clsLogger: Logger = getLogger(__name__)

    @classmethod
    def isShapeInRectangle(cls, boundingRectangle: Rectangle, shapeRectangle: Rectangle) -> bool:
        """

        Args:
            boundingRectangle:  The bounding rectangle
            shapeRectangle:     The shape we need to find out if bound rectangle fully contains it

        Returns:  `True` if all the vertices of the shape rectangle are contained inside the bounding
        rectangle,  Else `False`

        """

        ans: bool = False
        leftTopVertex:     UmlPoint = UmlPoint(x=shapeRectangle.left,  y=shapeRectangle.top)
        rightTopVertex:    UmlPoint = UmlPoint(x=shapeRectangle.right, y=shapeRectangle.top)
        leftBottomVertex:  UmlPoint = UmlPoint(x=shapeRectangle.left,  y=shapeRectangle.bottom)
        rightBottomVertex: UmlPoint = UmlPoint(x=shapeRectangle.right, y=shapeRectangle.bottom)

        if (
                cls.isPointInsideRectangle(point=leftTopVertex,     rectangle=boundingRectangle) is True and
                cls.isPointInsideRectangle(point=rightTopVertex,    rectangle=boundingRectangle) is True and
                cls.isPointInsideRectangle(point=leftBottomVertex,  rectangle=boundingRectangle) is True and
                cls.isPointInsideRectangle(point=rightBottomVertex, rectangle=boundingRectangle) is True
        ):

            ans = True

        return ans

    @classmethod
    def isLineWhollyContainedByRectangle(cls, boundingRectangle: Rectangle, umlLine: UmlLine) -> bool:
        """
        To determine if a line segment is wholly contained within a rectangle we check if both endpoints of
        the line segment are inside the rectangle.

        Args:
            umlLine:    The line segment
            boundingRectangle:  The bounding rectangle

        Returns: `True` if the entire line is inside the rectangle, else `False`
        """
        answer: bool = False
        if cls.isPointInsideRectangle(umlLine.start, boundingRectangle) is True and cls.isPointInsideRectangle(umlLine.end, boundingRectangle) is True:
            answer = True

        return answer

    @classmethod
    def isPointInsideRectangle(cls, point: UmlPoint, rectangle: Rectangle) -> bool:
        """

        Args:
            point:
            rectangle:

        Returns:  `True` if all the point is contained inside the bounding
        rectangle,  Else `False`

        """

        x: int = point.x
        y: int = point.y
        xMin: int = rectangle.left
        yMin: int = rectangle.top
        xMax: int = rectangle.right
        yMax: int = rectangle.bottom

        return xMin <= x <= xMax and yMin <= y <= yMax
