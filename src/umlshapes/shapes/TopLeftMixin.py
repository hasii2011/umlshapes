
from logging import Logger
from logging import getLogger

from wx import Size
from wx.lib.ogl import Shape

from umlshapes.types.Common import LeftCoordinate
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition


class TopLeftMixin:
    """
    This mixin adjusts the reported position so that it is effectively top left
    It also provides syntactic sugar for the size of the shape.  It caches
    the size but always reports it to the parent shape
    """

    def __init__(self, umlShape: Shape, width: int, height: int):

        self.tlmLogger: Logger = getLogger(__name__)
        self._shape:    Shape  = umlShape
        self._size:     Size   = Size(width=width, height=height)

    @property
    def size(self) -> UmlDimensions:
        """
        Syntactic sugar for external consumers;  Hide the underlying implementation

        Returns:  The UmlClass Size

        """
        return UmlDimensions(
            width=self._size.GetWidth(),
            height=self._size.GetHeight()
        )

    @size.setter
    def size(self, newSize: UmlDimensions):

        self._shape.SetSize(newSize.width, newSize.height)
        self._size.SetWidth(newSize.width)
        self._size.SetHeight(newSize.height)

    @property
    def position(self) -> UmlPosition:
        """
        This method returns the top left position

        Returns:  The shape position
        """
        return UmlPosition(x=self._topLeft.x, y=self._topLeft.y)

    @position.setter
    def position(self, position: UmlPosition):
        """
        Use this method to position the shape where its top left is at the input
        position.

        Args:
            position:
        """
        width:  int = self.size.width
        height: int = self.size.height

        centerX: int = position.x + (width // 2)
        centerY: int = position.y + (height // 2)

        self._shape.SetX(centerX)
        self._shape.SetY(centerY)

    @property
    def _topLeft(self) -> LeftCoordinate:
        """
        This method necessary because ogl reports positions from the center of the shape
        Calculates the left top coordinate

        Returns:  An adjusted coordinate
        """

        x = self._shape.GetX()                 # This points to the center of the rectangle
        y = self._shape.GetY()                 # This points to the center of the rectangle

        width:  int = self.size.width
        height: int = self.size.height

        left: int = x - (width // 2)
        top:  int = y - (height // 2)

        return LeftCoordinate(x=left, y=top)
