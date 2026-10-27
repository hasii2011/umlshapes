
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.frames.UmlFrame import UmlFrame

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDInstance import UmlSDInstance


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
        self.logger.debug(f'{deltaXY=}')

    def getSDInstances(self) -> list['UmlSDInstance']:
        """
        Retrieve all UmlSDInstance shapes currently on this diagram frame.
        """
        from umlshapes.sd.UmlSDInstance import UmlSDInstance

        instances: list[UmlSDInstance] = []
        for shape in self.umlShapes:
            if isinstance(shape, UmlSDInstance):
                instances.append(shape)
        return instances

    def setAllLifeLinesLength(self, length: int):
        """
        Resize all lifelines on this diagram frame to maintain uniform length.

        Args:
            length: The new lifeline length in pixels.
        """
        from umlshapes.sd.UmlSDInstance import UmlSDInstance

        for shape in self.umlShapes:
            if isinstance(shape, UmlSDInstance):
                shape.setLifeLineLength(newLength=length)
        self.refresh()

    def reFitAllInstancesWidth(self):
        """
        Re-fit all instances on this diagram to match their participant names.
        """
        from umlshapes.sd.UmlSDInstance import UmlSDInstance

        for shape in self.umlShapes:
            if isinstance(shape, UmlSDInstance):
                shape.reFitWidth()
        self.refresh()
