
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutText import PyutText

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class TextPasteCommand(BasePasteCommand):
    def __init__(self, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            pyutObject:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlText import UmlText

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='', pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlText: UmlText = cast(UmlText, None)

    def Do(self) -> bool:
        umlShape: UmlShape = self._createPastedShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlText = umlShape  # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlText)
        return True

    def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:
        from umlshapes.shapes.UmlText import UmlText
        from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler

        umlShape:     UmlText             = UmlText(cast(PyutText, pyutObject))
        eventHandler: UmlTextEventHandler = UmlTextEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
