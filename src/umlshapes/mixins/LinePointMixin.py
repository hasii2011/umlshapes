
from typing import cast
from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING

from wx import MemoryDC
from wx import Point

from wx.lib.ogl import LineShape

if TYPE_CHECKING:
    from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint

LineControlPoints = NewType('LineControlPoints', List[Point])


class LinePointMixin:
    """
    Mixin for LineShape subclasses (UmlLink, UmlSDMessage) that ensures line
    control points, endpoints, center positions, and label positions use
    integer wx.Point coordinates rather than float wx.RealPoint coordinates.
    """

    def __init__(self, lineShape: LineShape):

        self._lineShape: LineShape = lineShape

    @property
    def lineControlPoints(self) -> LineControlPoints:
        return cast(LineControlPoints, self._lineShape._lineControlPoints)

    def MakeLineControlPoints(self, n: int):
        """
        Overrides LineShape.MakeLineControlPoints to store integer wx.Point
        instances rather than float wx.RealPoint instances.

        Args:
            n: Number of line control points
        """
        self._lineShape._lineControlPoints = LineControlPoints([])

        for _ in range(n):
            point: Point = Point(-999, -999)
            self._lineShape._lineControlPoints.append(point)

        self._lineShape._initialised = False

    def InsertLineControlPoint(self, dc: Optional[MemoryDC] = None, point: Optional[Point] = None):
        """
        Overrides LineShape.InsertLineControlPoint to insert an integer wx.Point.

        Args:
            dc:    Optional device context
            point: Optional Point coordinates to insert
        """
        if dc is not None:
            self._lineShape.Erase(dc)

        lineControlPoints: LineControlPoints = self.lineControlPoints
        lineX: int
        lineY: int
        if point is not None:
            lineX = round(point[0])
            lineY = round(point[1])
        else:
            lastPoint:       Point = lineControlPoints[-1]
            secondLastPoint: Point = lineControlPoints[-2]

            lineX = (lastPoint.x + secondLastPoint.x) // 2
            lineY = (lastPoint.y + secondLastPoint.y) // 2

        newPoint: Point = Point(lineX, lineY)
        lineControlPoints.insert(len(lineControlPoints) - 1, newPoint)

    def Initialise(self):
        """
        Overrides LineShape.Initialise to populate intermediate line control
        points as integer wx.Point instances.
        """
        lineControlPoints: LineControlPoints = self.lineControlPoints
        if lineControlPoints:
            firstPoint: Point = lineControlPoints[0]
            lastPoint:  Point = lineControlPoints[-1]

            if not self._lineShape._initialised:
                for i in range(1, len(lineControlPoints)):
                    x1: int
                    x2: int
                    if firstPoint.x < lastPoint.x:
                        x1 = firstPoint.x
                        x2 = lastPoint.x
                    else:
                        x2 = firstPoint.x
                        x1 = lastPoint.x

                    y1: int
                    y2: int
                    if firstPoint.y < lastPoint.y:
                        y1 = firstPoint.y
                        y2 = lastPoint.y
                    else:
                        y2 = firstPoint.y
                        y1 = lastPoint.y

                    lineControlPoints[i] = Point((x2 - x1) // 2 + x1, (y2 - y1) // 2 + y1)
            self._lineShape._initialised = True

    def SetEnds(self, x1: float, y1: float, x2: float, y2: float):
        """
        Overrides LineShape.SetEnds to store integer wx.Point endpoints and
        integer center coordinates.

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
        """
        intX1: int = round(x1)
        intY1: int = round(y1)
        intX2: int = round(x2)
        intY2: int = round(y2)

        lineControlPoints: LineControlPoints = self.lineControlPoints
        lineControlPoints[0] = Point(intX1, intY1)
        lineControlPoints[-1] = Point(intX2, intY2)

        self._lineShape._xpos = (intX1 + intX2) // 2
        self._lineShape._ypos = (intY1 + intY2) // 2

    def GetLabelPosition(self, position: int) -> Tuple[int, int]:
        """
        Overrides LineShape.GetLabelPosition to return integer label coordinates.

        Args:
            position: Region position index

        Returns:
            Tuple of (x, y) integer coordinates
        """
        labelX: float
        labelY: float
        labelX, labelY = LineShape.GetLabelPosition(self._lineShape, position)
        return round(labelX), round(labelY)

    def OnMoveMiddleControlPoint(self, dc: MemoryDC, lpt: 'UmlLineControlPoint', pt) -> bool:
        """
        Overrides LineShape.OnMoveMiddleControlPoint to assign integer coordinates
        to the wx.Point backing the middle control point.

        Args:
            dc:  Device context
            lpt: Line control point being moved
            pt:  New point coordinates

        Returns:
            True
        """
        pointX: int = round(pt[0])
        pointY: int = round(pt[1])
        lpt._xpos = pointX
        lpt._ypos = pointY

        controlPoint: Point = lpt.point
        controlPoint[0] = pointX
        controlPoint[1] = pointY

        self._lineShape.GetEventHandler().OnMoveLink(dc)

        return True
