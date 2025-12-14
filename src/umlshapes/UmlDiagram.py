
from typing import List
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from collections.abc import Iterable

from umlshapes.lib.ogl import Diagram
from umlshapes.lib.ogl import Shape

from umlshapes.frames.DiagramFrame import DiagramFrame

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame

Shapes = NewType('Shapes', List[Shape])


class UmlDiagram(Diagram):
    """
    Modernity wrapper
    """
    def __init__(self, diagramFrame: DiagramFrame):
        """
        Set the frame at instantiation

        Args:
            diagramFrame:
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__()

        self.SetCanvas(diagramFrame)

    @property
    def associatedFrame(self) -> 'UmlFrame':
        return self.GetCanvas()

    @property
    def shapes(self) -> Iterable:
        return self.GetShapeList()

    @shapes.setter
    def shapes(self, shapeList):
        self._shapeList = shapeList
