
from wx.lib.ogl import Shape

from umlshapes.UmlUtils import UmlUtils


class IDMixin:
    def __init__(self, umlShape: Shape):

        self._umlShape: Shape = umlShape

        self._umlShape.SetId(UmlUtils.getID())

    @property
    def id(self) -> str:
        """
        Syntactic sugar for external consumers;  Hide the underlying implementation

        Returns:  The UML generated ID
        """
        return self._umlShape.GetId()

    @id.setter
    def id(self, newValue: str):
        self._umlShape.SetId(newValue)
