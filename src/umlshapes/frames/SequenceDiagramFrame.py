
from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.frames.UmlFrame import UmlFrame


class SequenceDiagramFrame(UmlFrame):
    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
            umlPubSubEngine:
        """
        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)

        self.umlDiagram.SetSnapToGrid(False)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SHAPE_MOVING,  frameId=self.id, listener=self._shapeMovingListener)

    def _shapeMovingListener(self, deltaXY: DeltaXY):
        self.logger.warning(f'{deltaXY}')
