
from typing import List
from typing import Tuple

from math import atan2
from math import degrees

from wx import DC
from wx import Size

from umlshapes.links.LollipopInflator import LollipopInflator

from umlshapes.types.Common import Rectangle
from umlshapes.types.Common import AttachmentSide
from umlshapes.types.Common import LollipopCoordinates

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.utils.ShapeAnalysis import RelativeRectangleResult
from umlshapes.utils.ShapeAnalysis import Degrees
from umlshapes.utils.ShapeAnalysis import ShapeAnalysis


class UmlUtils:

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
        if UmlUtils.isVerticalSide(side=attachmentSide):
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
        leftTopRectangle, otherRectangle, leftTopIndicator = ShapeAnalysis.identifyLeftMostTopMostRectangle(rectangle1=rectangle1, rectangle2=rectangle2)

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

    @staticmethod
    def snapCoordinatesToGrid(x: int, y: int, gridInterval: int) -> Tuple[int, int]:

        xDiff: float = x % gridInterval
        yDiff: float = y % gridInterval

        snappedX: int = round(x - xDiff)
        snappedY: int = round(y - yDiff)

        return snappedX, snappedY

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
