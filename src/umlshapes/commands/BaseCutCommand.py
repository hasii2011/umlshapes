
from typing import TYPE_CHECKING

from abc import ABC
from abc import abstractmethod

from logging import Logger
from logging import getLogger

from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BaseCommand import BaseCommand
from umlshapes.commands.AbstractBaseCommandMeta import AbstractBaseCommandMeta

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre


class BaseCutCommand(BaseCommand, metaclass=AbstractBaseCommandMeta):

    def __init__(self, partialName: str, umlModelBase: UmlModelBase, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        self.bccLogger: Logger = getLogger(__name__)

        super().__init__(partialName=partialName, umlModelBase=umlModelBase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

    class Meta(ABC):
        abstract = True

        @abstractmethod
        def _createCutShape(self, baseAttributes: UmlModelBase) -> 'UmlShapeGenre':
            """
            Specific cut types create their version of the shape;  Also the shape
            should have its specific event handler set up

            Args:
                baseAttributes:     The model object for the UML Shape

            Returns:  The correct UML Shape

            """
            pass
