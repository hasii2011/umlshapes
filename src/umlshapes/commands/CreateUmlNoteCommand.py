
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.Note import Note

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.commands.BaseCreateCommand import BaseCreateCommand


class CreateUmlNoteCommand(BaseCreateCommand):
    """
    Command that creates a new UML Note on the UML frame
    """

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine):

        self._uniqueId: int = self.timeStamp

        name: str = f'Create Note-{self._uniqueId}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def Undo(self) -> bool:

        assert isinstance(self._shape, UmlNote), 'It can only be this for this command'

        umlNote:    UmlNote = self._shape
        modelClass: Note    = umlNote.modelNote
        self._removeLinkedUmlShapeFromFrame(umlFrame=self._umlFrame, umlShape=self._shape, modelClass=modelClass)

        self.logger.debug(f'Undo create: {modelClass}')

        return True

    def _createPrototypeInstance(self) -> UmlNote:
        """
        Creates an appropriate UML shape for the new command

        Returns:    The newly created note
        """
        noteName: str = f'UmlNote{self._uniqueId}'

        modelNote: Note = Note(content=self._umlPreferences.noteText)
        modelNote.name = noteName

        umlNote: UmlNote = UmlNote(modelNote)

        return umlNote

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlNote:   UmlNote = cast(UmlNote, self._shape)       # noqa        # get old
        modelNote: Note    = umlNote.modelNote

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlNote, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.EDIT_NOTE, frameId=self._umlFrame.id, modelNote=modelNote)
