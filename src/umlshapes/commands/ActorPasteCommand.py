
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.Actor import Actor
from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre


class ActorPasteCommand(BasePasteCommand):

    def __init__(self, umlModelBase: UmlModelBase, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlModelBase:       We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlActor import UmlActor

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='ActorPasteCommand', umlModelBase=umlModelBase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlActor: UmlActor = cast(UmlActor, None)

    def Do(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createPastedShape(umlModelBase=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlActor = umlShape  # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlActor)
        return True

    def _createPastedShape(self, umlModelBase: UmlModelBase) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler

        umlShape:     UmlActor             = UmlActor(cast(Actor, umlModelBase))
        eventHandler: UmlActorEventHandler = UmlActorEventHandler(previousEventHandler=umlShape.GetEventHandler())

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
