
from logging import Logger
from logging import getLogger

from wx import MemoryDC

from umlshapes.lib.ogl import EllipseShape
from umlshapes.lib.ogl import RectangleShape

from umlshapes.utils.ResourceUtils import ResourceUtils


class DrawingUtils:
    clsLogger: Logger = getLogger(__name__)

    @classmethod
    def drawSelectedRectangle(cls, dc: MemoryDC, shape: RectangleShape):

        dc.SetPen(ResourceUtils.redDashedPen())
        sx = shape.GetX()
        sy = shape.GetY()

        if isinstance(sx, float):
            sx = DrawingUtils.fixBadFloat(badFloat=sx, message='sx is float')

        if isinstance(sy, float):
            sy = DrawingUtils.fixBadFloat(badFloat=sy, message='sy is float')

        width = shape.GetWidth() + 3
        height = shape.GetHeight() + 3

        if isinstance(width, float):
            width = DrawingUtils.fixBadFloat(badFloat=width, message='width is float')

        if isinstance(height, float):
            height = DrawingUtils.fixBadFloat(badFloat=height, message='height is float')

        x1 = sx - width // 2
        y1 = sy - height // 2

        dc.DrawRectangle(x1, y1, width, height)

    @classmethod
    def drawSelectedEllipse(cls, dc: MemoryDC, shape: EllipseShape):

        dc.SetPen(ResourceUtils.redDashedPen())

        dc.DrawEllipse(int(shape.GetX() - shape.GetWidth() / 2.0), int(shape.GetY() - shape.GetHeight() / 2.0), shape.GetWidth(), shape.GetHeight())

    @classmethod
    def fixBadFloat(cls, badFloat: float, message: str) -> int:

        DrawingUtils.clsLogger.warning(f'{message}: {badFloat} - rounded')
        goodInt: int = round(badFloat)

        return goodInt
