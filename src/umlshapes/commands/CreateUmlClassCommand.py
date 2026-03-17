
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
    """
    Command that creates a new UML Class on the UML frame
    """

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine, modelClass: Class = None):
        """
        If the caller provides a ready-made class this command uses it and does not
        invoke the class editor

        Args:
            umlFrame
            umlPosition:
            umlPubSubEngine:
        """
        self._uniqueId:   float          = self.timeStamp
        self._modelClass: Class | None = modelClass     # Must be here before super().__init__()

        name: str = f'Create Class-{self._uniqueId}'
        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def Undo(self) -> bool:

        assert isinstance(self._shape, UmlClass), 'It can only be this for this command'

        umlClass:   UmlClass = self._shape
        modelClass: Class    = umlClass.modelClass
        self._removeLinkedUmlShapeFromFrame(umlFrame=self._umlFrame, umlShape=self._shape, modelClass=modelClass)

        self.logger.debug(f'Undo create: {modelClass}')
        return True

    def _createPrototypeInstance(self) -> UmlClass:
        """
        Creates an appropriate class for the new command

        Returns:    The newly created class
        """
        if self._modelClass is None:
            className:  str   = f'{self._umlPreferences.defaultClassName}{self._uniqueId}'
            modelClass: Class = Class(name=className)
        else:
            modelClass = self._modelClass

        umlClass:   UmlClass = UmlClass(modelClass)

        return umlClass

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlClass:   UmlClass = cast(UmlClass, self._shape)      # noqa        # get old
        modelClass: Class    = umlClass.modelClass

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlClass, umlPosition=self._umlPosition)

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.EDIT_CLASS, frameId=self._umlFrame.id, modelClass=modelClass)

        self._umlFrame.refresh()
