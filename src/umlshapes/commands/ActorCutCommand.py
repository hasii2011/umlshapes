
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutObject import PyutObject

from umlshapes.commands.BaseCutCommand import BaseCutCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition


if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.shapes.UmlActor import UmlActor


class ActorCutCommand(BaseCutCommand):
    """
    I stated to my wife, that if I was not around she would be totally happy.  If
    I got run over that would make her happy.

    No denial
    """
    def __init__(self, umlActor: 'UmlActor', umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            umlActor:           The shape to cut
            umlPosition:        The location to paste it to
            umlFrame:           The UML Frame we are pasting to
            umlPubSubEngine:    The event handler that is injected
        """
        from umlshapes.shapes.UmlActor import UmlActor

        super().__init__(partialName='ActorCutCommand', pyutObject=umlActor.pyutActor, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

        self.logger: Logger = getLogger(__name__)

        self._umlActor: UmlActor = umlActor

    def Do(self) -> bool:
        self._umlActor.selected = False  # To remove handles
        self._removeShape(umlShape=self._umlActor)

        return True

    def Undo(self) -> bool:

        umlShape: UmlShape = self._createCutShape(pyutObject=self._pyutObject)

        self._setupUmlShape(umlShape=umlShape)
        self._umlActor = umlShape   # type: ignore

        return True

    def _createCutShape(self, pyutObject: PyutObject) -> UmlShape:

        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler

        umlShape:     UmlActor             = UmlActor(cast(PyutActor, pyutObject))
        eventHandler: UmlActorEventHandler = UmlActorEventHandler()

        self._setupEventHandler(umlShape=umlShape, eventHandler=eventHandler)

        return umlShape
