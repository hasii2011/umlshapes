
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.Class import Class

from umlshapes.commands.BaseCreateCommand import BaseCreateCommand
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPosition


class CreateUmlClassCommand(BaseCreateCommand):

    clsCounter: int = 1

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine):
        """
        If the caller provides a ready-made class this command uses it and does not
        invoke the class editor

        Args:
            umlPosition:
            umlPubSubEngine:
        """
        name: str = f'Create Class- {CreateUmlClassCommand.clsCounter}'
        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def Undo(self) -> bool:

        self.logger.info(f'{self._umlFrame=}')
        # SD Instance will not appear here
        assert isinstance(self._shape, UmlClass), 'It can only be this for this command'
        umlClass:   UmlClass = self._shape
        modelClass: Class    = umlClass.modelClass
        self._removeUmlShapeFromFrame(umlFrame=self._umlFrame, umlShape=self._shape, modelClass=modelClass)

        return True

    def _createPrototypeInstance(self) -> UmlClass:
        """
        Creates an appropriate class for the new command

        Returns:    The newly created class
        """
        className: str       = f'{self._umlPreferences.defaultClassName}{CreateUmlClassCommand.clsCounter}'
        modelClass: Class    = Class(name=className)
        umlClass:   UmlClass = UmlClass(modelClass)

        CreateUmlClassCommand.clsCounter += 1

        return umlClass

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlClass:   UmlClass = cast(UmlClass, self._shape)      # noqa        # get old
        modelClass: Class    = umlClass.modelClass

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlClass, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        # TODO:  Use the Uml Pub Sub Engine
        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.EDIT_CLASS, frameId=self._umlFrame.id, modelClass=modelClass)
