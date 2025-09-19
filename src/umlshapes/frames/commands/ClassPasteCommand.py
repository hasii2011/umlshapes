
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from datetime import datetime
from typing import cast

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutClass import PyutClass

from umlshapes.frames.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class ClassPasteCommand(BasePasteCommand):

    def __init__(self, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            pyutObject:         We will build the appropriate UML Shape from this
            umlPosition:        Where we will paste it
            umlFrame:           Where we are pasting
            umlPubSubEngine:    The event handlers need these injected
        """
        from umlshapes.shapes.UmlClass import UmlClass

        self.logger: Logger = getLogger(__name__)

        self._name:            str              = f'ClassPasteCommand-{self.timeStamp}'

        super().__init__(name=self._name, pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlClass: UmlClass = cast(UmlClass, None)

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):

        return True

    def Do(self) -> bool:

        umlShape: UmlShape = self._createPastedShape(pyutObject=self._pyutObject)

        self._umlFrame.umlDiagram.AddShape(umlShape)
        umlShape.position = self._umlPosition
        umlShape.umlFrame = self._umlFrame
        umlShape.Show(True)

        self._umlFrame.Refresh()

        return True

    def Undo(self) -> bool:

        # TODO TODO TODO TODO TODO TODO
        # from umlshapes.frames.DiagramFrame import DiagramFrame
        # from umlshapes.UmlDiagram import UmlDiagram
        #
        # umlFrame:   DiagramFrame = self._umlFrame
        # umlDiagram: UmlDiagram   = umlFrame.umlDiagram
        #
        # self._baseWxCreateLogger.info(f'Undo create {self._shape}')
        # umlDiagram.RemoveShape(self._shape)
        # umlFrame.refresh()

        return True

    def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:

        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

        umlShape     = UmlClass(cast(PyutClass, pyutObject))
        eventHandler = UmlClassEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape

    @property
    def timeStamp(self) -> int:

        dt = datetime.now()

        return dt.microsecond

