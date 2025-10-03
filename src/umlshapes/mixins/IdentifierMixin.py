
from umlshapes.UmlUtils import UmlUtils

class InvalidOperationError(Exception):
    pass


class IdentifierMixin:
    """
    This is a replacement ID from Shape.  Developers should use the
    properties to get human readable IDs.

    Today, I will stash strings into a protected variable
    """
    def __init__(self):

        self._identifier: str = UmlUtils.getID()
        # print(f'{self._shape._id=}')

    @property
    def id(self) -> str:
        """
        Syntactic sugar for external consumers;  Hide the underlying implementation

        Returns:  The UML generated ID
        """
        return self._identifier

    @id.setter
    def id(self, newValue: str):
        self._identifier = newValue

    def __eq__(self, other):

        if isinstance(other, IdentifierMixin):
            return self.id == other.id

        return False

    def SetId(self, i):
        raise InvalidOperationError('Use the id property')

    def GetId(self):
        raise InvalidOperationError('Use the id property')

