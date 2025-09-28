from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from datetime import datetime

from wx import Command

from pyutmodelv2.PyutObject import PyutObject

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame

class BaseCommand(Command):

    def __init__(self, partialName: str, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        from umlshapes.frames.UmlFrame import UmlFrame

        self._pyutObject:      PyutObject     = pyutObject
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
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
        umlShape.SetEventHandler(eventHandler)

    def _setupUmlShape(self, umlShape: UmlShape):

        self._umlFrame.umlDiagram.AddShape(umlShape)
        umlShape.position = self._umlPosition
        umlShape.umlFrame = self._umlFrame
        umlShape.Show(True)

        self._umlFrame.Refresh()

    def _removeShape(self, umlShape: UmlShape):
        self._umlFrame.umlDiagram.RemoveShape(umlShape)
        self._umlFrame.refresh()
