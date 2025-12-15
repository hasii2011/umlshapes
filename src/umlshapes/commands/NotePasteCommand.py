
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.Note import Note
from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre

class NotePasteCommand(BasePasteCommand):
    def __init__(self, umlModelBase: UmlModelBase, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlModelBase:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlNote import UmlNote

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='NotePasteCommand', umlModelBase=umlModelBase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlNote: UmlNote = cast(UmlNote, None)

    def Do(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createPastedShape(umlModelBase=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlNote = umlShape  # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlNote)
        return True

    def _createPastedShape(self, umlModelBase: UmlModelBase) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler

        umlShape:     UmlNote             = UmlNote(cast(Note, umlModelBase))
        eventHandler: UmlNoteEventHandler = UmlNoteEventHandler(previousEventHandler=umlShape.GetEventHandler())

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
