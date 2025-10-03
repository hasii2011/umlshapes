
from umlshapes.UmlUtils import UmlUtils

class InvalidOperationError(Exception):
    pass


class IdentifierMixin:
    """
    This is a replacement ID from Shape.  Developers should use the
    properties to get human readable IDs.

    Today, I will stash strings into a protected variable

    For now keep the move master property since I do not want to create yet another mixin

    """
    def __init__(self):

        self._identifier: str = UmlUtils.getID()
        self._moveMaster: bool = False

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

    @property
    def moveMaster(self) -> bool:
        return self._moveMaster

    @moveMaster.setter
    def moveMaster(self, newValue: bool):
        self._moveMaster = newValue
