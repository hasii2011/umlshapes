
from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.eventengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.frames.UmlFrame import UmlFrame


class UseCaseDiagramFrame(UmlFrame):
    def __init__(self, parent: Window, umlEventEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
            umlEventEngine:
        """

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent, umlEventEngine=umlEventEngine)
