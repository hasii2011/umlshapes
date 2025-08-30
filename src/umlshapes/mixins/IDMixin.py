
from umlshapes.lib.ogl import Shape


class IDMixin:
    clsId: int = 1000

    def __init__(self, umlShape: Shape):

        self._umlShape: Shape = umlShape
        self._umlShape.SetId(IDMixin.clsId)

        IDMixin.clsId += 1

    @property
    def id(self) -> int:
        """
        Syntactic sugar for external consumers;  Hide the underlying implementation

        Returns:  The UML generated ID
        """
        return self._umlShape.GetId()

    @id.setter
    def id(self, newValue: int):
        self._umlShape.SetId(newValue)
