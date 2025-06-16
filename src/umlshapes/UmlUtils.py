
from typing import cast
from typing import List
from typing import Tuple

from logging import Logger
from logging import getLogger
from logging import DEBUG

from wx import BLACK
from wx import Bitmap
from wx import Brush
from wx import FONTFAMILY_MODERN
from wx import FONTFAMILY_ROMAN
from wx import FONTFAMILY_SCRIPT
from wx import FONTFAMILY_SWISS
from wx import FONTFAMILY_TELETYPE
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_NORMAL
from wx import PENSTYLE_SHORT_DASH
from wx import PENSTYLE_SOLID
from wx import Point
from wx import RED

from wx import Font
from wx import MemoryDC
from wx import DC
from wx import Pen
from wx import Size

from wx.lib.ogl import EllipseShape
from wx.lib.ogl import RectangleShape

from human_id import generate_id

from umlshapes.links.LollipopInflator import LollipopInflator
from umlshapes.resources.images.Display import embeddedImage as displayImage
from umlshapes.resources.images.DoNotDisplay import embeddedImage as doNotDisplayImage
from umlshapes.resources.images.UnSpecified import embeddedImage as unSpecifiedImage

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.mixins.TopLeftMixin import Rectangle

from umlshapes.types.Common import AttachmentSide
from umlshapes.types.Common import LollipopCoordinates
from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions


class UmlUtils:

    clsLogger: Logger = getLogger(__name__)

    BLACK_SOLID_PEN:  Pen  = cast(Pen, None)
    RED_SOLID_PEN:    Pen  = cast(Pen, None)
    RED_DASHED_PEN:   Pen  = cast(Pen, None)
    BLACK_DASHED_PEN: Pen  = cast(Pen, None)

    DEFAULT_FONT:     Font = cast(Font, None)

    DEFAULT_BACKGROUND_BRUSH: Brush = cast(Brush, None)

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
            dist: float = UmlUtils.distance(pt1=referencePosition, pt2=position)
            if dist < lastDistance:
                closest      = position
                lastDistance = dist
                UmlUtils.clsLogger.debug(f'{dist}')

        return closest

    @classmethod
    def lollipopHitTest(cls, x: int, y: int, attachmentSide: AttachmentSide, lollipopCoordinates: LollipopCoordinates) -> bool:
        """
        This located here for testability

        Args:
            x:
            y:
            attachmentSide:
            lollipopCoordinates:

        Returns:
        """
        ans: bool = False

        rectangle: Rectangle = LollipopInflator.inflateLollipop(
            attachmentSide=attachmentSide,
            lollipopCoordinates=lollipopCoordinates
        )

        left:   int = rectangle.left
        right:  int = rectangle.right
        top:    int = rectangle.top
        bottom: int = rectangle.bottom

        # noinspection PyChainedComparisons
        if x >= left and x <= right and y >= top and y <= bottom:
            ans = True

        return ans

    # noinspection PyTypeChecker
    @classmethod
    def attachmentSide(cls, x, y, rectangle: Rectangle) -> AttachmentSide:

        if y == rectangle.top:
            return AttachmentSide.TOP
        if y == rectangle.bottom:
            return AttachmentSide.BOTTOM
        if x == rectangle.left:
            return AttachmentSide.LEFT
        if x == rectangle.right:
            return AttachmentSide.RIGHT

        assert False, 'Only works for points on the perimeter'

    @classmethod
    def isVerticalSide(cls, side: AttachmentSide) -> bool:
        """

        Args:
            side:

        Returns: 'True' if the side is vertical axis, else it returns 'False'
        """
        return side == AttachmentSide.LEFT or side == AttachmentSide.RIGHT

    @classmethod
    def computeLineCentum(cls, attachmentSide: AttachmentSide, umlPosition: UmlPosition, rectangle: Rectangle) -> float:
        """
        Computes a value between 0.1 and 0.9.  That value is the relative location of the input position
        Args:
            attachmentSide:
            umlPosition:  The xy position on the perimeter of the input rectangle
            rectangle:

        Returns:  A value 0.1 and 0.9
        """
        distance: float = 0.1
        if UmlUtils.isVerticalSide(side=attachmentSide) is True:
            height:         int = rectangle.bottom - rectangle.top
            relativeHeight: int = umlPosition.y - rectangle.top
            distance = relativeHeight / height
        elif attachmentSide == AttachmentSide.TOP or attachmentSide == AttachmentSide.BOTTOM:
            width:         int = rectangle.right - rectangle.left
            relativeWidth: int = umlPosition.x - rectangle.left
            distance = relativeWidth / width

        distance = round(distance, 1)
        if distance < 0.1:
            distance = 0.1
        elif distance > 0.9:
            distance = 0.9

        return distance

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
        UmlUtils.clsLogger.debug(f'{m=}')
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

    @classmethod
    def getID(cls) -> str:
        return generate_id(separator='.')

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

    # noinspection PyTypeChecker
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
