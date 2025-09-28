
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutClass import PyutClass

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame

class ClassPasteCommand(BasePasteCommand):

    def __init__(self, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            pyutObject:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlClass import UmlClass

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='ClassPasteCommand', pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlClass: UmlClass = cast(UmlClass, None)

    def GetName(self) -> str:
        return self._name

    def Do(self) -> bool:

        umlShape: UmlShape = self._createPastedShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlClass = umlShape   # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlClass)
        return True

    def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:

        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

        umlShape:     UmlClass             = UmlClass(cast(PyutClass, pyutObject))
        eventHandler: UmlClassEventHandler = UmlClassEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
