
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutObject import PyutObject

from umlshapes.commands.BaseCutCommand import BaseCutCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlClass import UmlClass


class ClassCutCommand(BaseCutCommand):
    def __init__(self, umlClass: 'UmlClass', umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlClass:           The shape to cut
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """

        from umlshapes.shapes.UmlClass import UmlClass

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='ClassCutCommand', pyutObject=umlClass.pyutClass, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlClass: UmlClass = umlClass

    def Do(self) -> bool:

        self._umlClass.selected = False         # To remove handles
        self._removeShape(umlShape=self._umlClass)
        return True

    def Undo(self) -> bool:

        umlShape: UmlShape = self._createCutShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlClass = umlShape   # type: ignore

        return True

    def _createCutShape(self, pyutObject: PyutObject) -> UmlShape:

        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

        umlShape: UmlClass = UmlClass(cast(PyutClass, pyutObject))
        eventHandler = UmlClassEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
