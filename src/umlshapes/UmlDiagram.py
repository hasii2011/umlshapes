
from logging import Logger
from logging import getLogger

from wx.lib.ogl import Diagram

from umlshapes.DiagramFrame import DiagramFrame


class UmlDiagram(Diagram):
    def __init__(self, diagramFrame: DiagramFrame):
        """
        Set the frame at instantiation

        Args:
            diagramFrame:
        """
        self.logger: Logger = getLogger(__name__)

        super().__init__()

        self.SetCanvas(diagramFrame)
