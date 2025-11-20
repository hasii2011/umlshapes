
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.UseCase import UseCase
from umlmodel.BaseAttributes import BaseAttributes

from umlshapes.commands.BaseCutCommand import BaseCutCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlUseCase import UmlUseCase
    from umlshapes.ShapeTypes import UmlShapeGenre


class UseCaseCutCommand(BaseCutCommand):

    def __init__(self, umlUseCase: 'UmlUseCase', umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlUseCase:      The shape to cut
            umlPosition:     The location to paste it to
            umlFrame:        The UML Frame we are pasting to
            umlPubSubEngine: The event handler that is injected
        """
        from umlshapes.shapes.UmlUseCase import UmlUseCase

        super().__init__(partialName='TextCutCommand', baseAttributes=umlUseCase.modelUseCase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

        self._umlUseCase: UmlUseCase = umlUseCase

    def Do(self) -> bool:

        self._umlUseCase.selected = False  # To remove handles
        self._removeShape(umlShape=self._umlUseCase)

        return True

    def Undo(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createCutShape(baseAttributes=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlUseCase = umlShape   # type: ignore

        return True

    def _createCutShape(self, baseAttributes: BaseAttributes) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlUseCase import UmlUseCase
        from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

        umlShape:     UmlUseCase             = UmlUseCase(cast(UseCase, baseAttributes))
        eventHandler: UmlUseCaseEventHandler = UmlUseCaseEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
