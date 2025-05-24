
from typing import cast
from typing import List
from typing import Tuple

from logging import Logger
from logging import getLogger
from logging import DEBUG

from time import time as pyTime

from wx import BLACK
from wx import Bitmap
from wx import Brush
from wx import FONTFAMILY_DEFAULT
from wx import FONTFAMILY_MODERN
from wx import FONTFAMILY_ROMAN
from wx import FONTFAMILY_SCRIPT
from wx import FONTFAMILY_SWISS
from wx import FONTFAMILY_TELETYPE
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_NORMAL
from wx import PENSTYLE_SHORT_DASH
from wx import PENSTYLE_SOLID
from wx import RED

from wx import Font
from wx import MemoryDC
from wx import DC
from wx import Pen
from wx import Size

from wx.lib.ogl import EllipseShape
from wx.lib.ogl import RectangleShape

from hrid import HRID

from umlshapes.resources.images.Display import embeddedImage as displayImage
from umlshapes.resources.images.DoNotDisplay import embeddedImage as doNotDisplayImage
from umlshapes.resources.images.UnSpecified import embeddedImage as unSpecifiedImage

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.UmlColor import UmlColor

from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.types.UmlPosition import UmlPosition


class UmlUtils:

    clsLogger: Logger = getLogger(__name__)

    BLACK_SOLID_PEN:  Pen  = cast(Pen, None)
    RED_SOLID_PEN:    Pen  = cast(Pen, None)
    RED_DASHED_PEN:   Pen  = cast(Pen, None)
    BLACK_DASHED_PEN: Pen  = cast(Pen, None)

    DEFAULT_FONT:     Font = cast(Font, None)

    DEFAULT_BACKGROUND_BRUSH: Brush = cast(Brush, None)

    ID_GENERATOR: HRID = cast(HRID, None)

    @classmethod
    def getID(cls) -> str:
        if UmlUtils.ID_GENERATOR is None:
            UmlUtils.ID_GENERATOR = HRID(delimiter='.', seed=round(pyTime() * 1000))
        uuid = UmlUtils.ID_GENERATOR.generate()

        return uuid

    @staticmethod
    def snapCoordinatesToGrid(x: int, y: int, gridInterval: int) -> Tuple[int, int]:

        xDiff: float = x % gridInterval
        yDiff: float = y % gridInterval

        snappedX: int = round(x - xDiff)
        snappedY: int = round(y - yDiff)

        return snappedX, snappedY

    @classmethod
    def drawSelectedRectangle(cls, dc: MemoryDC, shape: RectangleShape):

        dc.SetPen(UmlUtils.redDashedPen())
        sx = shape.GetX()
        sy = shape.GetY()

        if isinstance(sx, float):
            sx = UmlUtils.fixBadFloat(badFloat=sx, message='sx is float')

        if isinstance(sy, float):
            sy = UmlUtils.fixBadFloat(badFloat=sy, message='sy is float')

        width = shape.GetWidth() + 3
        height = shape.GetHeight() + 3

        if isinstance(width, float):
            width = UmlUtils.fixBadFloat(badFloat=width, message='width is float')

        if isinstance(height, float):
            height = UmlUtils.fixBadFloat(badFloat=height, message='height is float')

        x1 = sx - width // 2
        y1 = sy - height // 2

        dc.DrawRectangle(x1, y1, width, height)

    @classmethod
    def drawSelectedEllipse(cls, dc: MemoryDC, shape: EllipseShape):

        dc.SetPen(UmlUtils.redDashedPen())

        dc.DrawEllipse(int(shape.GetX() - shape.GetWidth() / 2.0), int(shape.GetY() - shape.GetHeight() / 2.0), shape.GetWidth(), shape.GetHeight())

    @classmethod
    def blackSolidPen(cls) -> Pen:

        if UmlUtils.BLACK_SOLID_PEN is None:
            UmlUtils.BLACK_SOLID_PEN = Pen(BLACK, 1, PENSTYLE_SOLID)

        return UmlUtils.BLACK_SOLID_PEN

    @classmethod
    def redSolidPen(cls) -> Pen:

        if UmlUtils.RED_SOLID_PEN is None:
            UmlUtils.RED_SOLID_PEN = Pen(RED, 1, PENSTYLE_SOLID)

        return UmlUtils.RED_SOLID_PEN

    @classmethod
    def redDashedPen(cls) -> Pen:
        if UmlUtils.RED_DASHED_PEN is None:
            UmlUtils.RED_DASHED_PEN = Pen(RED, 1, PENSTYLE_SHORT_DASH)

        return UmlUtils.RED_DASHED_PEN

    @classmethod
    def blackDashedPen(cls) -> Pen:
        if UmlUtils.BLACK_DASHED_PEN is None:
            UmlUtils.BLACK_DASHED_PEN = Pen(BLACK, 1, PENSTYLE_SHORT_DASH)

        return UmlUtils.BLACK_DASHED_PEN

    @classmethod
    def defaultFont(cls) -> Font:
        if UmlUtils.DEFAULT_FONT is None:
            fontSize:      int           = UmlPreferences().textFontSize
            fontFamilyStr: UmlFontFamily = UmlPreferences().textFontFamily
            fontFamily:    int           = UmlUtils.umlFontFamilyToWxFontFamily(fontFamilyStr)

            UmlUtils.DEFAULT_FONT = Font(fontSize, fontFamily, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL)
            UmlUtils.clsLogger.debug(f'{UmlUtils.DEFAULT_FONT=}')

        return UmlUtils.DEFAULT_FONT

    @classmethod
    def backGroundBrush(cls) -> Brush:
        if UmlUtils.DEFAULT_BACKGROUND_BRUSH is None:
            backGroundColor: UmlColor = UmlPreferences().backGroundColor
            brush:           Brush    = Brush()
            brush.SetColour(UmlColor.toWxColor(backGroundColor))

            UmlUtils.DEFAULT_BACKGROUND_BRUSH = brush

        return UmlUtils.DEFAULT_BACKGROUND_BRUSH

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
        if UmlUtils.clsLogger.isEnabledFor(DEBUG):
            UmlUtils.clsLogger.debug(f'{srcPosition=}  {dstPosition=}')
        x1 = srcPosition.x
        y1 = srcPosition.y
        x2 = dstPosition.x
        y2 = dstPosition.y

        midPointX = abs(x1 + x2) // 2
        midPointY = abs(y1 + y2) // 2

        return UmlPosition(x=midPointX, y=midPointY)

    @classmethod
    def umlFontFamilyToWxFontFamily(cls, enumValue: UmlFontFamily) -> int:

        if enumValue == UmlFontFamily.SWISS:
            return FONTFAMILY_SWISS
        elif enumValue == UmlFontFamily.MODERN:
            return FONTFAMILY_MODERN
        elif enumValue == UmlFontFamily.ROMAN:
            return FONTFAMILY_ROMAN
        elif enumValue == UmlFontFamily.SCRIPT:
            return FONTFAMILY_SCRIPT
        elif enumValue == UmlFontFamily.TELETYPE:
            return FONTFAMILY_TELETYPE
        else:
            return FONTFAMILY_DEFAULT

    @classmethod
    def lineSplitter(cls, text: str, dc: DC, textWidth: int) -> List[str]:
        """
        Split the `text` into lines that fit into `textWidth` pixels.

        Note:  This is a copy of the one in Pyut.  Duplicated here to remove the LineSplitter dependency.

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
                word: str = f'{wordX} '

                # extentSize: Tuple[int, int] = dc.GetTextExtent(word)        # wxPython 4.2.3 update
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

    @classmethod
    def displayIcon(cls) -> Bitmap:
        bmp: Bitmap = displayImage.GetBitmap()
        return bmp

    @classmethod
    def doNotDisplayIcon(cls) -> Bitmap:
        bmp: Bitmap = doNotDisplayImage.GetBitmap()
        return bmp

    @classmethod
    def unspecifiedDisplayIcon(cls) -> Bitmap:
        bmp: Bitmap = unSpecifiedImage.GetBitmap()
        return bmp

    @classmethod
    def fixBadFloat(cls, badFloat: float, message: str) -> int:

        UmlUtils.clsLogger.warning(f'{message}: {badFloat} - rounded')
        goodInt: int = round(badFloat)

        return goodInt
