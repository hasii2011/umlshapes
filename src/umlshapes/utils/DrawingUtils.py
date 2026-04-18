from typing import List

from logging import Logger
from logging import getLogger

from wx import DC
from wx import Size
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

    @classmethod
    def lineSplitter(cls, text: str, dc: DC, textWidth: int) -> List[str]:
        """
        Split the `text` into lines that fit into `textWidth` pixels.

        Args:
            text:       The text to split
            dc:         Device Context
            textWidth:  The width of the text in pixels

        Returns:
            A list of strings that are no wider than the input pixel `width`
        """
        splitLines: List[str] = text.splitlines()
        newLines:   List[str] = []

        for line in splitLines:
            words:     List[str] = line.split()
            lineWidth: int       = 0
            newLine:   str       = ""
            for wordX in words:

                word:       str  = f'{wordX} '
                extentSize: Size = dc.GetTextExtent(word)
                wordWidth:  int  = extentSize.width

                if lineWidth + wordWidth <= textWidth:
                    newLine = f'{newLine}{word}'
                    lineWidth += wordWidth
                else:
                    newLines.append(newLine[:-1])   # remove last space
                    newLine = word
                    lineWidth = wordWidth

            newLines.append(newLine[:-1])

        return newLines
