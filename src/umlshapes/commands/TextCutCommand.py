
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutText import PyutText

from umlshapes.commands.BaseCutCommand import BaseCutCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlText import UmlText


class TextCutCommand(BaseCutCommand):
    def __init__(self, umlText: 'UmlText', umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlText:         The shape to cut
            umlPosition:     The location to paste it to
            umlFrame:        The UML Frame we are pasting to
            umlPubSubEngine: The event handler that is injected
        """
        from umlshapes.shapes.UmlText import UmlText

        super().__init__(partialName='TextCutCommand', pyutObject=umlText.pyutText, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

        self._umlText: UmlText = umlText

    def Do(self) -> bool:
        self._umlText.selected = False  # To remove handles
        self._removeShape(umlShape=self._umlText)

        return True

    def Undo(self) -> bool:

        umlShape: UmlShape = self._createCutShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlText = umlShape   # type: ignore

        return True

    def _createCutShape(self, pyutObject: PyutObject) -> UmlShape:

        from umlshapes.shapes.UmlText import UmlText
        from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler

        umlShape:     UmlText             = UmlText(cast(PyutText, pyutObject))
        eventHandler: UmlTextEventHandler = UmlTextEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
