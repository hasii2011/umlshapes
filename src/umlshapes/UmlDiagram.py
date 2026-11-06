
from typing import List
from typing import NewType
from typing import Tuple
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from collections.abc import Iterable

from wx.lib.ogl import Diagram
from wx.lib.ogl import Shape

from umlshapes.frames.DiagramFrame import DiagramFrame

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame

Shapes = NewType('Shapes', List[Shape])

DEFAULT_GRID_SPACING: int = 5


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

        self._gridSpacing = DEFAULT_GRID_SPACING
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

    def Snap(self, x: int, y: int) -> Tuple[int, int]:
        """
        Snap coordinates to the nearest grid point using integer rounding.

        Args:
            x: Input X coordinate
            y: Input Y coordinate

        Returns:
            Snapped (x, y) integer coordinates
        """
        if self._snapToGrid:
            snappedX: int = round(self._gridSpacing * round(x / self._gridSpacing + 0.5))
            snappedY: int = round(self._gridSpacing * round(y / self._gridSpacing + 0.5))
            return snappedX, snappedY
        return round(x), round(y)
