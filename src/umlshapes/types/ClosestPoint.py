
from dataclasses import dataclass


@dataclass
class LinePoint:
    x: int = 0
    y: int = 0


@dataclass
class FromPoint(LinePoint):
    pass


@dataclass
class ClosestPoint(LinePoint):
    pass


def determineClosestPoint(startPoint: LinePoint, endPoint: LinePoint, fromPoint: FromPoint) -> ClosestPoint:
    """
    Given line defined as startPoint-->endPoint and a reference point fromPoint return the closest
    point on the line

    https://stackoverflow.com/questions/47177493/python-point-on-a-line-closest-to-third-point

    Args:
        startPoint:     start of line
        endPoint:     end of line
        fromPoint:  The reference point

    Returns:  The closest point from fromPoint on the line p1-->p2
    """
    x1: int = startPoint.x
    y1: int = startPoint.y
    x2: int = endPoint.x
    y2: int = endPoint.y
    x3: int = fromPoint.x
    y3: int = fromPoint.y

    dx: int = x2 - x1
    dy: int = y2 - y1

    det: int   = dx * dx + dy * dy
    a:   float = (dy * (y3 - y1) + dx * (x3 - x1)) / det

    cX: float = x1 + a * dx
    cY: float = y1 + a * dy

    return ClosestPoint(
        x=round(cX),
        y=round(cY)
    )
