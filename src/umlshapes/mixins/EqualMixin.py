
from umlshapes.lib.ogl import Shape


class EqualMixin:
    def __init__(self, umlShape: Shape):

        self._umlShape: Shape = umlShape

    def __eq__(self, other):

        if isinstance(other, Shape):
            return self._umlShape.GetId() == other.GetId()

        return False
