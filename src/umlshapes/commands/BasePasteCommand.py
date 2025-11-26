
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from abc import ABC
from abc import abstractmethod

from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.commands.BaseCommand import BaseCommand
from umlshapes.commands.AbstractBaseCommandMeta import AbstractBaseCommandMeta

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapeGenre


class BasePasteCommand(BaseCommand, metaclass=AbstractBaseCommandMeta):

    def __init__(self, partialName: str, umlModelBase: UmlModelBase, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        self.basePasteLogger: Logger = getLogger(__name__)

        super().__init__(partialName=partialName, umlModelBase=umlModelBase, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

    class Meta(ABC):
        abstract = True

        @abstractmethod
        def _createPastedShape(self, umlModelBase: UmlModelBase) -> 'UmlShapeGenre':
            """
            Specific paste types create their version of the shape;  Also the shape
            should have its specific event handler set up

            Args:
                umlModelBase:     The model object for the UML Shape

            Returns:  The correct UML Shape

            """
            pass

    def _undo(self, umlShape: 'UmlShapeGenre'):
        """
        Common code for basic Undo
        Args:
            umlShape:  The shape to remove from the frame

        """
        self._removeShape(umlShape=umlShape)
