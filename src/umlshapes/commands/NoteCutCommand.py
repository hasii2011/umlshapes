
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.Note import Note
from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BaseCutCommand import BaseCutCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlNote import UmlNote
    from umlshapes.ShapeTypes import UmlShapeGenre


class NoteCutCommand(BaseCutCommand):
    def __init__(self, umlNote: 'UmlNote', umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        from umlshapes.shapes.UmlNote import UmlNote

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='ClassCutCommand', umlModelBase=umlNote.modelNote, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlNote: UmlNote = umlNote

    def Do(self) -> bool:

        self._umlNote.selected = False         # To remove handles
        self._removeShape(umlShape=self._umlNote)

        return True

    def Undo(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createCutShape(umlModelBase=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlNote = umlShape   # type: ignore

        return True

    def _createCutShape(self, umlModelBase: UmlModelBase) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler

        umlShape:     UmlNote             = UmlNote(cast(Note, umlModelBase))
        eventHandler: UmlNoteEventHandler = UmlNoteEventHandler(previousEventHandler=umlShape.GetEventHandler())

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
