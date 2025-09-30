
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import DC
from wx import TRANSPARENT_BRUSH

from umlshapes.lib.ogl import RectangleShape

from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.DiagramFrame import DiagramFrame


class ShapeSelector(RectangleShape, TopLeftMixin):
    """
    Used to draw a selection boundary around shapes
    """

    def __init__(self, width: int= 0, height: int = 0):

        self.logger: Logger = getLogger(__name__)

        RectangleShape.__init__(self, w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=width, height=height)

        self._moving:           bool        = False
        self._originalPosition: UmlPosition = cast(UmlPosition, None)

        self.SetCentreResize(False)
        self.SetBrush(TRANSPARENT_BRUSH)

    @property
    def diagramFrame(self) -> 'DiagramFrame':
        return self.GetCanvas()

    @diagramFrame.setter
    def diagramFrame(self, frame: 'DiagramFrame'):
        self.SetCanvas(frame)

    @property
    def originalPosition(self) -> UmlPosition:
        return self._originalPosition

    @originalPosition.setter
    def originalPosition(self, value: UmlPosition):
        self._originalPosition = value

    @property
    def moving(self) -> bool:
        return self._moving

    @moving.setter
    def moving(self, moving: bool):
        self._moving = moving

    def OnDraw(self, dc: DC):

        super().OnDraw(dc)
