
from logging import Logger
from logging import getLogger

from wx import PENSTYLE_DOT
from wx import BRUSHSTYLE_TRANSPARENT

from wx import Pen
from wx import Brush
from wx import MemoryDC

from umlshapes.lib.ogl import RectangleShape

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.preferences.UmlPreferences import UmlPreferences


class SDInstanceConstrainer(RectangleShape):
    """
    The constraining shape for the UML SD Instance.  Internal shape
    required by wx ogl composite shapes
    """

    def __init__(self, diagramFrame: SequenceDiagramFrame):

        self._preferences: UmlPreferences = UmlPreferences()

        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions
        super().__init__(w=instanceDimensions.width, h=instanceDimensions.height)

        self.SetCanvas(diagramFrame)

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
        pen.SetStyle(PENSTYLE_DOT)
        self.SetPen(pen)

        super().OnDraw(dc)
