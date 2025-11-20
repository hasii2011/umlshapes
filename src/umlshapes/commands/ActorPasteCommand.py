
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.Actor import Actor
from umlmodel.BaseAttributes import BaseAttributes

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre


class ActorPasteCommand(BasePasteCommand):

        def __init__(self, baseAttributes: BaseAttributes, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
            """

            Args:
                baseAttributes:         We will build the appropriate UML Shape from this
                umlPosition:        The location to paste it to
                umlFrame:           The UML Frame we are pasting to
                umlPubSubEngine:    The event handler that is injected
            """
            from umlshapes.shapes.UmlActor import UmlActor

            self.logger: Logger = getLogger(__name__)

            super().__init__(partialName='ActorPasteCommand', baseAttributes=baseAttributes, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

            self._umlActor: UmlActor = cast(UmlActor, None)

        def Do(self) -> bool:
            from umlshapes.ShapeTypes import UmlShapeGenre

            umlShape: UmlShapeGenre = self._createPastedShape(pyutObject=self._baseAttributes)

            self._setupUmlShape(umlShape=umlShape)
            self._umlActor = umlShape  # type: ignore

            return True

        def Undo(self) -> bool:
            self._undo(umlShape=self._umlActor)
            return True

        def _createPastedShape(self, pyutObject: BaseAttributes) -> 'UmlShapeGenre':
            from umlshapes.shapes.UmlActor import UmlActor
            from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler

            umlShape:     UmlActor             = UmlActor(cast(Actor, pyutObject))
            eventHandler: UmlActorEventHandler = UmlActorEventHandler()

            self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

            return umlShape
