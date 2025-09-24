
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutObject import PyutObject

from umlshapes.frames.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class ActorPasteCommand(BasePasteCommand):

        def __init__(self, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
            """

            Args:
                pyutObject:         We will build the appropriate UML Shape from this
                umlPosition:        The location to paste it to
                umlFrame:           The UML Frame we are pasting to
                umlPubSubEngine:    The event handler need this injected
            """
            from umlshapes.shapes.UmlActor import UmlActor

            self.logger: Logger = getLogger(__name__)

            self._name: str = f'ActorPasteCommand-{self.timeStamp}'

            super().__init__(name=self._name, pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

            self._umlActor: UmlActor = cast(UmlActor, None)

        def GetName(self) -> str:
            return self._name

        def Do(self) -> bool:
            umlShape: UmlShape = self._createPastedShape(pyutObject=self._pyutObject)

            self._umlFrame.umlDiagram.AddShape(umlShape)
            umlShape.position = self._umlPosition
            umlShape.umlFrame = self._umlFrame
            umlShape.Show(True)

            self._umlFrame.Refresh()

            self._umlActor = umlShape  # type: ignore

            return True

        def Undo(self) -> bool:

            self._umlFrame.umlDiagram.RemoveShape(self._umlActor)
            self._umlFrame.refresh()
            return True

        def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:
            from umlshapes.shapes.UmlActor import UmlActor
            from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler

            umlShape: UmlActor = UmlActor(cast(PyutActor, pyutObject))
            eventHandler = UmlActorEventHandler()

            self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

            return umlShape

