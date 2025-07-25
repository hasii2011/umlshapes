
from typing import Optional
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import BLACK
from wx import BLACK_PEN
from wx import RED
from wx import RED_PEN
from wx import WHITE_BRUSH
from wx import Font
from wx import MemoryDC
from wx import Size

from wx.lib.ogl import Shape

from pyutmodelv2.PyutInterface import PyutInterface

from umlshapes.UmlUtils import UmlUtils

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.mixins.TopLeftMixin import Rectangle

from umlshapes.types.Common import AttachmentSide
from umlshapes.types.Common import LollipopCoordinates
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass
    from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame


class UmlLollipopInterface(Shape):
    """
    Lollipops are tasty !!
    """
    def __init__(self, pyutInterface: PyutInterface, canvas: Optional['ClassDiagramFrame'] = None):
        """

        Args:
            pyutInterface:  The data model
            canvas:         The diagram frame we are on
        """
        self._pyutInterface: PyutInterface  = pyutInterface
        self._preferences:   UmlPreferences = UmlPreferences()

        super().__init__(canvas=canvas)
        self.logger: Logger = getLogger(__name__)

        self._lineCentum:       float = 0.1
        self._defaultFont:      Font  = UmlUtils.defaultFont()
        self._pixelSize:        Size  = self._defaultFont.GetPixelSize()

        self._attachedTo:       UmlClass       = cast('UmlClass', None)
        self._attachmentSide:   AttachmentSide = cast(AttachmentSide, None)

    @property
    def umlFrame(self) -> 'ClassDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'ClassDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def pyutInterface(self) -> PyutInterface:
        return self._pyutInterface

    @pyutInterface.setter
    def pyutInterface(self, pyutInterface: PyutInterface):
        self._pyutInterface = pyutInterface

    @property
    def attachedTo(self) -> 'UmlClass':
        return self._attachedTo

    @attachedTo.setter
    def attachedTo(self, umlClass: 'UmlClass'):
        self._attachedTo = umlClass

    @property
    def lineCentum(self) -> float:
        return self._lineCentum

    @lineCentum.setter
    def lineCentum(self, distance: float):
        self._lineCentum = distance

    @property
    def attachmentSide(self) -> AttachmentSide:
        return self._attachmentSide

    @attachmentSide.setter
    def attachmentSide(self, attachmentSide: AttachmentSide):
        self._attachmentSide = attachmentSide

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    def OnDraw(self, dc: MemoryDC):
        """
        Start coordinates are on the UML Class perimeter
        End coordinates are where the line ends and the circle is drawn

        Args:
            dc:
        """
        dc.SetBrush(WHITE_BRUSH)
        dc.SetFont(self._defaultFont)
        if self.selected:
            dc.SetPen(RED_PEN)
            dc.SetTextForeground(RED)
        else:
            dc.SetPen(BLACK_PEN)
            dc.SetTextForeground(BLACK)

        dc.GetPen().SetWidth(4)

        umlClassRectangle: Rectangle = self._attachedTo.rectangle
        lollipopCoordinates: LollipopCoordinates = self._computeLollipopCoordinates(umlClassRectangle)

        dc.DrawLine(x1=lollipopCoordinates.startCoordinates.x, y1=lollipopCoordinates.startCoordinates.y,
                    x2=lollipopCoordinates.endCoordinates.x,   y2=lollipopCoordinates.endCoordinates.y)

        dc.DrawCircle(lollipopCoordinates.endCoordinates.x, lollipopCoordinates.endCoordinates.y, self._preferences.lollipopCircleRadius)

        extentSize: Size = dc.GetTextExtent(self.pyutInterface.name)

        interfaceNamePosition: UmlPosition = self._determineInterfaceNamePosition(
            start=lollipopCoordinates.startCoordinates,
            side=self._attachmentSide,
            pixelSize=self._pixelSize,
            textSize=extentSize
        )
        dc.DrawText(self.pyutInterface.name, interfaceNamePosition.x, interfaceNamePosition.y)

    def HitTest(self, x, y):
        """
        Override base behavior
        Args:
            x:   The clicked x coordinate
            y:   The clicked y coordinate

        Returns:  `True` if it meets my criteria, else `False`
        """
        rectangle: Rectangle = self._attachedTo.rectangle
        lollipopCoordinates: LollipopCoordinates = self._computeLollipopCoordinates(rectangle)

        lollipopWasAbused: bool = UmlUtils.lollipopHitTest(x=x, y=y, attachmentSide=self.attachmentSide, lollipopCoordinates=lollipopCoordinates)

        if lollipopWasAbused:
            return 0, self
        else:
            return False

    def _computeLollipopCoordinates(self, rectangle: Rectangle) -> LollipopCoordinates:
        """

        Args:
            rectangle:

        Returns:    The appropriate coordinates
        """
        if UmlUtils.isVerticalSide(side=self.attachmentSide):
            lollipopCoordinates: LollipopCoordinates = self._computeVerticalSideCoordinates(rectangle)
        else:
            lollipopCoordinates = self._computeHorizontalSideCoordinates(rectangle)

        return lollipopCoordinates

    def _computeHorizontalSideCoordinates(self, rectangle: Rectangle) -> LollipopCoordinates:
        """

        Args:
            rectangle:

        Returns:  Coordinates for the horizontal sides of the class
        """
        width: int = rectangle.right - rectangle.left
        x:     int = round(width * self.lineCentum) + rectangle.left

        lollipopLineLength: int = self._preferences.lollipopLineLength

        if self.attachmentSide == AttachmentSide.BOTTOM:
            startCoordinates: UmlPosition = UmlPosition(x=x, y=rectangle.bottom)
            endCoordinates:   UmlPosition = UmlPosition(x=startCoordinates.x, y=startCoordinates.y + lollipopLineLength)
        else:
            startCoordinates = UmlPosition(x=x, y=rectangle.top)
            endCoordinates   = UmlPosition(x=startCoordinates.x, y=startCoordinates.y - lollipopLineLength)

        return LollipopCoordinates(startCoordinates=startCoordinates, endCoordinates=endCoordinates)

    def _computeVerticalSideCoordinates(self, rectangle: Rectangle) -> LollipopCoordinates:
        """

        Args:
            rectangle:

        Returns:  Coordinates for the vertical sides of the class
        """
        height: int = rectangle.bottom - rectangle.top
        y:      int = round(height * self.lineCentum) + rectangle.top

        lollipopLineLength: int = self._preferences.lollipopLineLength

        if self.attachmentSide == AttachmentSide.LEFT:
            startCoordinates: UmlPosition = UmlPosition(x=rectangle.left, y=y)
            endCoordinates:   UmlPosition = UmlPosition(x=startCoordinates.x - lollipopLineLength, y=startCoordinates.y)
        else:
            startCoordinates = UmlPosition(x=rectangle.right, y=y)
            endCoordinates   = UmlPosition(x=startCoordinates.x + lollipopLineLength, y=startCoordinates.y)

        return LollipopCoordinates(startCoordinates=startCoordinates, endCoordinates=endCoordinates)

    def _determineInterfaceNamePosition(self, start: UmlPosition, side: AttachmentSide, pixelSize: Size, textSize: Size) -> UmlPosition:

        oglPosition:     UmlPosition    = UmlPosition()

        x: int = start.x
        y: int = start.y

        fHeight: int = pixelSize.height
        tWidth:  int = textSize.width

        lollipopLineLength:   int = self._preferences.lollipopLineLength
        lollipopCircleRadius: int = self._preferences.lollipopCircleRadius
        interfaceNameIndent:  int = self._preferences.interfaceNameIndent

        if side == AttachmentSide.TOP:
            y -= (lollipopLineLength + (lollipopCircleRadius * 2) + interfaceNameIndent)
            x -= (tWidth // 2)
            oglPosition.x = x
            oglPosition.y = y

        elif side == AttachmentSide.BOTTOM:
            y += (lollipopLineLength + lollipopCircleRadius + interfaceNameIndent)
            x -= (tWidth // 2)
            oglPosition.x = x
            oglPosition.y = y

        elif side == AttachmentSide.LEFT:
            y = y - (fHeight * 2)
            originalX: int = x
            x = x - lollipopLineLength - round((tWidth * self._preferences.horizontalOffset))
            while x + tWidth > originalX:
                x -= interfaceNameIndent
            oglPosition.x = x
            oglPosition.y = y

        elif side == AttachmentSide.RIGHT:
            y = y - (fHeight * 2)
            x = x + round(lollipopLineLength * self._preferences.horizontalOffset)
            oglPosition.x = x
            oglPosition.y = y
        else:
            self.logger.error(f'Unknown attachment side: {side}')
            assert False, 'Unknown attachment side'

        return oglPosition

    def _isSameName(self, other: 'UmlLollipopInterface') -> bool:

        ans: bool = False
        if self.pyutInterface.name == other.pyutInterface.name:
            ans = True
        return ans

    def _isSameId(self, other: 'UmlLollipopInterface'):

        ans: bool = False
        if self.GetId() == other.GetId():
            ans = True
        return ans

    def __str__(self) -> str:
        return f'{self.__repr__()} - attached to: {self.attachedTo}'

    def __repr__(self):

        strMe: str = f'UmlLollipopInterface - "{self._pyutInterface.name}"'
        return strMe

    def __eq__(self, other: object):

        if isinstance(other, UmlLollipopInterface):
            if self._isSameName(other) is True and self._isSameId(other) is True:
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):
        return hash(self._pyutInterface.name) + hash(self.GetId())
