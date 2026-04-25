from logging import Logger
from logging import getLogger

from wx import Point

from umlshapes.types.Common import Rectangle
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions


class ProximityUtils:
    clsLogger: Logger = getLogger(__name__)

    @classmethod
    def distance(cls, pt1: UmlPosition, pt2: UmlPosition) -> float:
        """

        Args:
            pt1:
            pt2:

        Returns:    This distance between the 2 points
        """
        x1: int = pt1.x
        y1: int = pt1.y
        x2: int = pt2.x
        y2: int = pt2.y

        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        return distance

    @classmethod
    def closestPoint(cls, referencePosition: UmlPosition, umlPositions: UmlPositions) -> UmlPosition:

        closest:      UmlPosition = UmlPosition()
        lastDistance: float       = 10000000.0          # some large number to start
        for position in umlPositions:
            dist: float = ProximityUtils.distance(pt1=referencePosition, pt2=position)
            if dist < lastDistance:
                closest      = position
                lastDistance = dist
                ProximityUtils.clsLogger.debug(f'{dist}')

        return closest

    @classmethod
    def getNearestPointOnRectangle(cls, x, y, rectangle: Rectangle) -> UmlPosition:
        """
        https://stackoverflow.com/questions/20453545/how-to-find-the-nearest-point-in-the-perimeter-of-a-rectangle-to-a-given-point

        Args:
            x:  The x coordinate we are measuring from
            y:  The y coordinate we are measuring from
            rectangle:  The rectangle that describes our shape

        Returns:  The near point on the rectangle
        """
        point: Point = Point()
        point.x = max(rectangle.left, min(rectangle.right, x))
        point.y = max(rectangle.top,  min(rectangle.bottom, y))

        dl: int = abs(point.x - rectangle.left)
        dr: int = abs(point.x - rectangle.right)
        dt: int = abs(point.y - rectangle.top)
        db: int = abs(point.y - rectangle.bottom)

        m: int = min([dl, dr, dt, db])
        ProximityUtils.clsLogger.debug(f'{m=}')
        #
        # TODO: Rewrite this to have a single exit point
        #
        if m == dt:
            return UmlPosition(point.x, rectangle.top)
        if m == db:
            return UmlPosition(point.x, rectangle.bottom)
        if m == dl:
            return UmlPosition(rectangle.left, point.y)

        return UmlPosition(rectangle.right, point.y)
