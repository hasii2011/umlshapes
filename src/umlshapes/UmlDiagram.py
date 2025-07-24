
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from collections.abc import Iterable
from wx.lib.ogl import Diagram
from wx.lib.ogl import Shape

from umlshapes.frames.DiagramFrame import DiagramFrame

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
    def shapes(self) -> Iterable:
        return self.GetShapeList()
