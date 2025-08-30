
from umlshapes.UmlUtils import UmlUtils

from umlshapes.lib.ogl import Shape

class InvalidOperationError(Exception):
    pass


class IDMixin:
    """
    This is a replacement ID from Shape.  Developers should use the
    properties to get human readable IDs.

    In the future, I will prohibit the use of .GetId and .SetId
    Today, I will stash strings into what Shape says is an integer
    """
    def __init__(self, shape: Shape):

        self._shape: Shape = shape
        self._shape.SetId(UmlUtils.getID())
        # print(f'{self._shape._id=}')

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

    # def SetId(self, i):
    #     raise InvalidOperationError('Use the id property')
    #
    # def GetId(self):
    #     raise InvalidOperationError('Use the id property')

