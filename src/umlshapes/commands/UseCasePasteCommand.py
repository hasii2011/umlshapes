
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger
from typing import cast

from umlmodel.UseCase import UseCase
from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine


from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre


class UseCasePasteCommand(BasePasteCommand):
    def __init__(self, umlModelBase: UmlModelBase, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlModelBase:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlUseCase import UmlUseCase

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='UseCasePasteCommand', umlModelBase=umlModelBase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlUseCase: UmlUseCase = cast(UmlUseCase, None)

    def Do(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createPastedShape(baseAttributes=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlUseCase = umlShape  # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlUseCase)
        return True

    def _createPastedShape(self, baseAttributes: UmlModelBase) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlUseCase import UmlUseCase
        from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

        umlShape:     UmlUseCase             = UmlUseCase(cast(UseCase, baseAttributes))
        eventHandler: UmlUseCaseEventHandler = UmlUseCaseEventHandler(previousEventHandler=umlShape.GetEventHandler())

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
