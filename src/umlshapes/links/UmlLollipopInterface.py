
from typing import Optional
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import BLACK_PEN
from wx import MemoryDC
from wx import RED_PEN
from wx import WHITE_BRUSH

from wx.lib.ogl import Shape

from pyutmodelv2.PyutInterface import PyutInterface

from umlshapes.UmlUtils import UmlUtils
from umlshapes.shapes.TopLeftMixin import Rectangle
from umlshapes.types.Common import AttachmentSide
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass
    from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame

LOLLIPOP_LINE_LENGTH:   int = 90    # Make these
LOLLIPOP_CIRCLE_RADIUS: int = 4     # preferences


@dataclass
class LollipopCoordinates:
    startCoordinates: UmlPosition
    endCoordinates:   UmlPosition


class UmlLollipopInterface(Shape):
    """
    Lollipops are tasty !!
    """
    def __init__(self, pyutInterface: PyutInterface, canvas: Optional['UmlClassDiagramFrame'] = None):
        """

        Args:
            pyutInterface:  The data model
            canvas:         The diagram frame we are on
        """
        self._pyutInterface: PyutInterface = pyutInterface

        super().__init__(canvas=canvas)
        self.logger: Logger = getLogger(__name__)

        self._relativePosition: UmlPosition    = UmlPosition()
        self._attachedTo:       UmlClass       = cast('UmlClass', None)
        self._lineCentum:         float          = 0.1
        self._attachmentSide:   AttachmentSide = cast(AttachmentSide, None)

    @property
    def pyutInterface(self) -> PyutInterface:
        return self._pyutInterface

    @pyutInterface.setter
    def pyutInterface(self, pyutInterface: PyutInterface):
        self._pyutInterface = pyutInterface

    @property
    def relativePosition(self) -> UmlPosition:
        return self._relativePosition

    @relativePosition.setter
    def relativePosition(self, relativePosition: UmlPosition):
        self._relativePosition = relativePosition

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
    def attachmentSide(self):
        return self._attachmentSide

    @attachmentSide.setter
    def attachmentSide(self, attachmentSide: AttachmentSide):
        self._attachmentSide = attachmentSide

    def OnDraw(self, dc: MemoryDC):
        """
        Start coordinates are on the UML Class perimeter
        End coordinates are where the line ends and the circle is drawn

        Args:
            dc:
        """
        dc.SetBrush(WHITE_BRUSH)
        if self.Selected() is True:
            dc.SetPen(RED_PEN)
        else:
            dc.SetPen(BLACK_PEN)

        dc.GetPen().SetWidth(4)

        rectangle: Rectangle = self._attachedTo.rectangle
        lollipopCoordinates: LollipopCoordinates = self._computeLollipopCoordinates(rectangle)

        dc.DrawLine(x1=lollipopCoordinates.startCoordinates.x, y1=lollipopCoordinates.startCoordinates.y,
                    x2=lollipopCoordinates.endCoordinates.x,   y2=lollipopCoordinates.endCoordinates.y)

        dc.DrawCircle(lollipopCoordinates.endCoordinates.x, lollipopCoordinates.endCoordinates.y, LOLLIPOP_CIRCLE_RADIUS)

    def _computeLollipopCoordinates(self, rectangle: Rectangle) -> LollipopCoordinates:
        """

        Args:
            rectangle:

        Returns:    The appropriate coordinates
        """
        if UmlUtils.isVerticalSide(side=self.attachmentSide) is True:
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

        if self.attachmentSide == AttachmentSide.BOTTOM:
            startCoordinates = UmlPosition(x=x, y=rectangle.bottom)
            endCoordinates = UmlPosition(x=startCoordinates.x, y=startCoordinates.y + LOLLIPOP_LINE_LENGTH)
        else:
            startCoordinates = UmlPosition(x=x, y=rectangle.top)
            endCoordinates = UmlPosition(x=startCoordinates.x, y=startCoordinates.y - LOLLIPOP_LINE_LENGTH)

        return LollipopCoordinates(startCoordinates=startCoordinates, endCoordinates=endCoordinates)

    def _computeVerticalSideCoordinates(self, rectangle: Rectangle) -> LollipopCoordinates:
        """

        Args:
            rectangle:

        Returns:  Coordinates for the vertical sides of the class
        """
        height: int = rectangle.bottom - rectangle.top
        y:      int = round(height * self.lineCentum) + rectangle.top

        if self.attachmentSide == AttachmentSide.LEFT:
            startCoordinates: UmlPosition = UmlPosition(x=rectangle.left, y=y)
            endCoordinates: UmlPosition = UmlPosition(x=startCoordinates.x - LOLLIPOP_LINE_LENGTH, y=startCoordinates.y)
        else:
            startCoordinates = UmlPosition(x=rectangle.right, y=y)
            endCoordinates = UmlPosition(x=startCoordinates.x + LOLLIPOP_LINE_LENGTH, y=startCoordinates.y)

        return LollipopCoordinates(startCoordinates=startCoordinates, endCoordinates=endCoordinates)

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
