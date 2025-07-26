
from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.frames.UmlFrame import UmlFrame


class UseCaseDiagramFrame(UmlFrame):
    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
            umlPubSubEngine:
        """

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)
