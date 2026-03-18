
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

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine):

        name: str = f'Create Note- {self.timeStamp}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

    def _createPrototypeInstance(self) -> UmlNote:
        """
        Creates an appropriate UML shape for the new command

        Returns:    The newly created note
        """
        noteName: str = f'UmlNote{self.timeStamp}'

        modelNote: Note = Note(content=self._umlPreferences.noteText)
        modelNote.name = noteName

        umlNote: UmlNote  = UmlNote(modelNote)

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
