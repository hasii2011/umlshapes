from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject

from umlshapes.commands.AbstractBaseCommandMeta import AbstractBaseCommandMeta
from umlshapes.commands.BaseCommand import BaseCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class BaseCutCommand(BaseCommand, metaclass=AbstractBaseCommandMeta):

    def __init__(self, partialName: str, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        self.bccLogger: Logger = getLogger(__name__)

        super().__init__(partialName=partialName, pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

    class Meta(ABC):
        abstract = True

        @abstractmethod
        def _createCutShape(self, pyutObject: PyutObject) -> UmlShape:
            """
            Specific cut types create their version of the shape;  Also the shape
            should have its specific event handler set up

            Args:
                pyutObject:     The model object for the UML Shape

            Returns:  The correct UML Shape

            """
            pass
