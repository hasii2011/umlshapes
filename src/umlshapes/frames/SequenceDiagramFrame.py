
from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.eventengine.IUmlEventEngine import IUmlEventEngine
from umlshapes.frames.UmlFrame import UmlFrame


class SequenceDiagramFrame(UmlFrame):
    def __init__(self, parent: Window, umlEventEngine: IUmlEventEngine):
        """

        Args:
            parent:
            umlEventEngine:
        """
        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent, umlEventEngine=umlEventEngine)
