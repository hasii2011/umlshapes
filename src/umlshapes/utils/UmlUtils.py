from typing import List

from math import atan2
from math import degrees

from wx import DC
from wx import Size

from umlshapes.types.Common import Rectangle

from umlshapes.utils.ShapeAnalysisUtils import RelativeRectangleResult
from umlshapes.utils.ShapeAnalysisUtils import Degrees
from umlshapes.utils.ShapeAnalysisUtils import ShapeAnalysisUtils


class UmlUtils:

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
        leftTopRectangle, otherRectangle, leftTopIndicator = ShapeAnalysisUtils.identifyLeftMostTopMostRectangle(rectangle1=rectangle1, rectangle2=rectangle2)

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
