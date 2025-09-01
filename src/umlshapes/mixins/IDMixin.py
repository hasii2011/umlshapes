
from umlshapes.UmlUtils import UmlUtils

from umlshapes.lib.ogl import Shape

class InvalidOperationError(Exception):
    pass


class IDMixin:
    """
    This is a replacement ID from Shape.  Developers should use the
    properties to get human readable IDs.

    This is still implemented because Lollipop interface has its
    own __equ__ implementation
    """
    def __init__(self, shape: Shape):

        self._shape: Shape = shape
        self._shape.SetId(UmlUtils.getID())

    @property
    def id(self) -> str:
        """
        Syntactic sugar for external consumers;  Hide the underlying implementation

        Returns:  The UML generated ID
        """
        return self._shape.GetId()

    @id.setter
    def id(self, newValue: str):
        self._shape.SetId(newValue)
