from typing import Optional

from logging import Logger
from logging import getLogger

from wx import PENSTYLE_DOT
from wx import BRUSHSTYLE_TRANSPARENT
from wx import PENSTYLE_TRANSPARENT

from wx import Pen
from wx import Brush
from wx import MemoryDC

from umlshapes.lib.ogl import RectangleShape

from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.preferences.UmlPreferences import UmlPreferences


class SDInstanceConstrainer(RectangleShape, TopLeftMixin):
    """
    The constraining shape for the UML SD Instance.  Internal shape
    required by wx ogl composite shapes
    """

    def __init__(self, width: Optional[int] = None):

        self._preferences:  UmlPreferences = UmlPreferences()
        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

        initialWidth: int
        if width is not None:
            initialWidth = width
        else:
            initialWidth = instanceDimensions.width

        super().__init__(w=initialWidth, h=instanceDimensions.height)
        TopLeftMixin.__init__(self, umlShape=self, width=initialWidth, height=instanceDimensions.height)

        self.logger: Logger = getLogger(__name__)

    def OnDraw(self, dc: MemoryDC):
        """

        Args:
            dc:
        """
        # self.logger.info(f'x: {self.GetX()} y: {self.GetY()}  {self.position=}')
        brush: Brush = self.GetBrush()
        brush.SetStyle(BRUSHSTYLE_TRANSPARENT)
        self.SetBrush(brush)

        pen: Pen = self.GetPen()
        if self._preferences.debugSDInstance:
            pen.SetStyle(PENSTYLE_DOT)
        else:
            pen.SetStyle(PENSTYLE_TRANSPARENT)

        self.SetPen(pen)

        super().OnDraw(dc)

    def HitTest(self, x: float, y: float) -> tuple[int, float] | bool:
        """
        Pass-through hit test so background constraining shape does not intercept mouse clicks.
        """
        return False
