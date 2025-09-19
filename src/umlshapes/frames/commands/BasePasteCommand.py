from abc import ABC
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from abc import ABCMeta
from abc import abstractmethod

from dataclasses import dataclass

from wx import Command

from pyutmodelv2.PyutObject import PyutObject

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


@dataclass
class PasteCreatorResults:
    umlShape:     UmlShape            = cast(UmlShape, None)
    eventHandler: UmlBaseEventHandler = cast('UmlBaseEventHandler', None)


"""
I have no idea why this works:

https://stackoverflow.com/questions/50085658/inheriting-from-both-abc-and-django-db-models-model-raises-metaclass-exception
"""

class AbstractCommandMeta(ABCMeta, type(Command)):      # type: ignore
    pass


class BasePasteCommand(Command, metaclass=AbstractCommandMeta):

    def __init__(self, name: str, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        self._pyutObject:      PyutObject     = pyutObject
        self._umlPosition:     UmlPosition    = umlPosition
        self._umlFrame:        'UmlFrame'      = umlFrame
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self.logger: Logger = getLogger(__name__)

        super().__init__(canUndo=True, name=name)

    class Meta(ABC):
        abstract = True

        @abstractmethod
        def _createPastedShape(self, pyutObject: PyutObject) -> UmlShape:
            """
            Specific paste types create their version of the shape;  Also the shape
            should have its specific event handler set up

            Args:
                pyutObject:     The model object for the UML Shape

            Returns:  The correct UML Shape

            """
            pass

    def _setupEventHandler(self, umlShape, eventHandler: 'UmlBaseEventHandler'):

        eventHandler.SetShape(umlShape)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
        umlShape.SetEventHandler(eventHandler)
