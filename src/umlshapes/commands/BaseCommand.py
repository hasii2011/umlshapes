
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from datetime import datetime

from wx import Command

from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre

class BaseCommand(Command):

    def __init__(self, partialName: str, umlModelBase: UmlModelBase, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        from umlshapes.frames.UmlFrame import UmlFrame

        self._baseAttributes:  UmlModelBase     = umlModelBase
        self._umlPosition:     UmlPosition    = umlPosition
        self._umlFrame:        UmlFrame       = umlFrame
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self.baseLogger: Logger = getLogger(__name__)

        self._name: str = f'{partialName}-{self.timeStamp}'      # Because Command.GetName() does not really work

        super().__init__(canUndo=True, name=self._name)

    @property
    def timeStamp(self) -> int:

        dt = datetime.now()

        return dt.microsecond

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True

    def _setupEventHandler(self, umlShape, eventHandler: 'UmlBaseEventHandler'):

        eventHandler.SetShape(umlShape)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlShape.SetEventHandler(eventHandler)

    def _setupUmlShape(self, umlShape: 'UmlShapeGenre'):

        self._umlFrame.umlDiagram.AddShape(umlShape)
        umlShape.position = self._umlPosition
        umlShape.umlFrame = self._umlFrame
        umlShape.Show(True)

        self._umlFrame.Refresh()

    def _removeShape(self, umlShape: 'UmlShapeGenre'):
        self._umlFrame.umlDiagram.RemoveShape(umlShape)
        self._umlFrame.refresh()
