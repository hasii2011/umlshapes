
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.BaseAttributes import BaseAttributes
from umlmodel.Class import Class

from umlshapes.commands.BasePasteCommand import BasePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre


class ClassPasteCommand(BasePasteCommand):

    def __init__(self, baseAttributes: BaseAttributes, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            baseAttributes:         We will build the appropriate UML Shape from this
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlClass import UmlClass

        self.logger: Logger = getLogger(__name__)

        super().__init__(partialName='ClassPasteCommand', baseAttributes=baseAttributes, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self._umlClass: UmlClass = cast(UmlClass, None)

    def GetName(self) -> str:
        return self._name

    def Do(self) -> bool:
        from umlshapes.ShapeTypes import UmlShapeGenre

        umlShape: UmlShapeGenre = self._createPastedShape(umlBase=self._baseAttributes)

        self._setupUmlShape(umlShape=umlShape)
        self._umlClass = umlShape   # type: ignore

        return True

    def Undo(self) -> bool:
        self._undo(umlShape=self._umlClass)
        return True

    def _createPastedShape(self, umlBase: BaseAttributes) -> 'UmlShapeGenre':

        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

        umlShape:     UmlClass             = UmlClass(cast(Class, umlBase))
        eventHandler: UmlClassEventHandler = UmlClassEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
