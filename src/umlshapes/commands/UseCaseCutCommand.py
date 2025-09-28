
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger
from typing import cast

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.commands.BaseCutCommand import BaseCutCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlUseCase import UmlUseCase


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

        super().__init__(partialName='TextCutCommand', pyutObject=umlUseCase.pyutUseCase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

        self._umlUseCase: UmlUseCase = umlUseCase

    def Do(self) -> bool:

        self._umlUseCase.selected = False  # To remove handles
        self._removeShape(umlShape=self._umlUseCase)

        return True

    def Undo(self) -> bool:

        umlShape: UmlShape = self._createCutShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlUseCase = umlShape   # type: ignore

        return True

    def _createCutShape(self, pyutObject: PyutObject) -> UmlShape:

        from umlshapes.shapes.UmlUseCase import UmlUseCase
        from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

        umlShape:     UmlUseCase             \
            = UmlUseCase(cast(PyutUseCase, pyutObject))
        eventHandler: UmlUseCaseEventHandler = UmlUseCaseEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
