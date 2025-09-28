
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutObject import PyutObject

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class NotePasteCommand(BasePasteCommand):
    def __init__(self, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            pyutObject:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlNote import UmlNote

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='NotePasteCommand', pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlNote: UmlNote = cast(UmlNote, None)

    def Do(self) -> bool:
        umlShape: UmlShape = self._createPastedShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlNote = umlShape  # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlNote)
        return True

    def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler

        umlShape:     UmlNote             = UmlNote(cast(PyutNote, pyutObject))
        eventHandler: UmlNoteEventHandler = UmlNoteEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
