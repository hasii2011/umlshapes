
from typing import cast
from typing import List
from typing import Tuple

from logging import Logger
from logging import getLogger
from logging import DEBUG

from wx import DC
from wx import FONTFAMILY_DEFAULT
from wx import FONTFAMILY_MODERN
from wx import FONTFAMILY_ROMAN
from wx import FONTFAMILY_SCRIPT
from wx import FONTFAMILY_SWISS
from wx import FONTFAMILY_TELETYPE
from wx import PENSTYLE_SOLID
from wx import Pen
from wx import RED

from wx import NewIdRef as wxNewIdRef

from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.types.UmlPosition import UmlPosition


class UmlUtils:

    clsLogger: Logger = getLogger(__name__)

    RED_FOREGROUND_PEN: Pen = cast(Pen, None)

    @staticmethod
    def snapCoordinatesToGrid(x: int, y: int, gridInterval: int) -> Tuple[int, int]:

        xDiff: float = x % gridInterval
        yDiff: float = y % gridInterval

        snappedX: int = round(x - xDiff)
        snappedY: int = round(y - yDiff)

        return snappedX, snappedY

    @classmethod
    def redSolidPen(cls):

        if UmlUtils.RED_FOREGROUND_PEN is None:
            UmlUtils.RED_FOREGROUND_PEN = Pen(RED, 1, PENSTYLE_SOLID)

        return UmlUtils.RED_FOREGROUND_PEN

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

        midPointX = round(abs(x1 + x2) / 2)
        midPointY = round(abs(y1 + y2) / 2)

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

        Note:  This is a copy of the one in Pyut.  Duplicated here in order to remove the LineSplitter dependency.

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

                extentSize: Tuple[int, int] = dc.GetTextExtent(word)        # width, height
                wordWidth:  int             = extentSize[0]
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
    def assignID(cls, numberOfIds: int) -> List[wxNewIdRef]:
        """
        Assign and return numberOfIds

        Sample use        : [Unique_Id1, Unique_Id2, Unique_Id3] = assignID(3)

        Note:  This is a copy of the one in Pyut.  Duplicated here in order to remove the PyutUtils dependency.

        Args:
            numberOfIds: number of unique IDs to return

        Returns:  List of numbers which contain <numberOfIds> unique IDs
        """
        retList: List[wxNewIdRef] = []
        x: int = 0
        while x < numberOfIds:
            retList.append(wxNewIdRef())
            x += 1
        return retList
