
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.Text import Text
from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BaseCutCommand import BaseCutCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlText import UmlText
    from umlshapes.ShapeTypes import UmlShapeGenre


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

        super().__init__(partialName='TextCutCommand', umlModelBase=umlText.modelText, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

        self._umlText: UmlText = umlText

    def Do(self) -> bool:
        self._umlText.selected = False  # To remove handles
        self._removeShape(umlShape=self._umlText)

        return True

    def Undo(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createCutShape(umlModelBase=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlText = umlShape   # type: ignore

        return True

    def _createCutShape(self, umlModelBase: UmlModelBase) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlText import UmlText
        from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler

        umlShape:     UmlText             = UmlText(cast(Text, umlModelBase))
        eventHandler: UmlTextEventHandler = UmlTextEventHandler(previousEventHandler=umlShape.GetEventHandler())

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
