
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.UseCase import UseCase

from umlshapes.commands.BaseCreateCommand import BaseCreateCommand
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.shapes.UmlUseCase import UmlUseCase
from umlshapes.types.UmlPosition import UmlPosition


class CreateUmlUseCaseCommand(BaseCreateCommand):

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine):

        self._uniqueId: int = self.timeStamp

        name: str = f'Create UseCase-{self._uniqueId}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def Undo(self) -> bool:

        assert isinstance(self._shape, UmlUseCase), 'It can only be this for this command'

        umlUseCase:   UmlUseCase = self._shape
        modelUseCase: UseCase    = umlUseCase.modelUseCase
        self._removeLinkedUmlShapeFromFrame(umlFrame=self._umlFrame, umlShape=self._shape, modelClass=modelUseCase)

        self.logger.debug(f'Undo create: {modelUseCase}')

        return True

    def _createPrototypeInstance(self) -> UmlUseCase:
        """
        Creates an appropriate UML shape for the new command

        Returns:    The newly created Use Case
        """
        modelUseCase: UseCase = UseCase(name=self._umlPreferences.defaultNameUsecase)

        umlUseCase: UmlUseCase = UmlUseCase(modelUseCase)

        return umlUseCase

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlUseCase:   UmlUseCase = cast(UmlUseCase, self._shape)       # get old
        modelUseCase: UseCase    = umlUseCase.modelUseCase

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlUseCase, umlPosition=self._umlPosition)

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.EDIT_USE_CASE, frameId=self._umlFrame.id, modelUseCase=modelUseCase)

        self._umlFrame.refresh()
