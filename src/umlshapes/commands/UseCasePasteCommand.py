
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger
from typing import cast

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class UseCasePasteCommand(BasePasteCommand):
    def __init__(self, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            pyutObject:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlUseCase import UmlUseCase

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='UseCasePasteCommand', pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlUseCase: UmlUseCase = cast(UmlUseCase, None)

    def Do(self) -> bool:
        umlShape: UmlShape = self._createPastedShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlUseCase = umlShape  # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlUseCase)
        return True

    def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:
        from umlshapes.shapes.UmlUseCase import UmlUseCase
        from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

        umlShape:     UmlUseCase             = UmlUseCase(cast(PyutUseCase, pyutObject))
        eventHandler: UmlUseCaseEventHandler = UmlUseCaseEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
