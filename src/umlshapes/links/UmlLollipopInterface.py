
from typing import Optional
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import BLACK_PEN
from wx import MemoryDC
from wx import RED_PEN
from wx.core import WHITE_BRUSH

from wx.lib.ogl import Shape

from pyutmodelv2.PyutInterface import PyutInterface

from umlshapes.UmlUtils import UmlUtils
from umlshapes.types.Common import AttachmentSide
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass
    from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame

LOLLIPOP_LINE_LENGTH:   int = 90    # Make these
LOLLIPOP_CIRCLE_RADIUS: int = 4     # preferences


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

        self._relativePosition: UmlPosition = UmlPosition()
        self._attachedTo:       UmlClass    = cast('UmlClass', None)

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
        startCoordinates: UmlPosition = UmlUtils.convertToAbsoluteCoordinates(relativePosition=self._relativePosition, rectangle=self._attachedTo.rectangle)

        attachmentSide: AttachmentSide = UmlUtils.attachmentSide(
            x=startCoordinates.x,
            y=startCoordinates.y,
            rectangle=self._attachedTo.rectangle
        )
        if attachmentSide == AttachmentSide.TOP:
            endCoordinates:   UmlPosition = UmlPosition(x=startCoordinates.x, y=startCoordinates.y - LOLLIPOP_LINE_LENGTH)
        elif attachmentSide == AttachmentSide.BOTTOM:
            endCoordinates = UmlPosition(x=startCoordinates.x, y=startCoordinates.y + LOLLIPOP_LINE_LENGTH)
        elif attachmentSide == AttachmentSide.LEFT:
            endCoordinates = UmlPosition(x=startCoordinates.x - LOLLIPOP_LINE_LENGTH, y=startCoordinates.y)
        else:
            endCoordinates = UmlPosition(x=startCoordinates.x + LOLLIPOP_LINE_LENGTH, y=startCoordinates.y)

        dc.DrawLine(x1=startCoordinates.x, y1=startCoordinates.y, x2=endCoordinates.x, y2=endCoordinates.y)
        dc.DrawCircle(endCoordinates.x, endCoordinates.y, LOLLIPOP_CIRCLE_RADIUS)

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
