
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.Actor import Actor

from umlshapes.commands.BaseCreateCommand import BaseCreateCommand
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.types.UmlPosition import UmlPosition


class CreateUmlActorCommand(BaseCreateCommand):

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine):

        self._uniqueId: int = self.timeStamp

        name: str = f'Create Actor-{self._uniqueId}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def Undo(self) -> bool:

        assert isinstance(self._shape, UmlActor), 'It can only be this for this command'

        umlActor:   UmlActor = self._shape
        modelClass: Actor    = umlActor.modelActor
        self._removeLinkedUmlShapeFromFrame(umlFrame=self._umlFrame, umlShape=self._shape, modelClass=modelClass)

        self.logger.debug(f'Undo create: {modelClass}')

        return True

    def _createPrototypeInstance(self) -> UmlActor:
        """
        Creates an appropriate UML shape for the new command

        Returns:    The newly created Actor
        """
        modelActor: Actor = Actor(actorName=self._umlPreferences.defaultNameActor)

        umlActor: UmlActor = UmlActor(modelActor)

        return umlActor

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlActor:   UmlActor = cast(UmlActor, self._shape)       # noqa        # get old
        modelActor: Actor    = umlActor.modelActor

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlActor, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.EDIT_ACTOR, frameId=self._umlFrame.id, modelActor=modelActor)
