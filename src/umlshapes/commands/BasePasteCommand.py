
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject

from umlshapes.commands.BaseCommand import BaseCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame


class BasePasteCommand(BaseCommand):

    def __init__(self, partialName: str, pyutObject: PyutObject, umlPosition: UmlPosition, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        self.basePasteLogger: Logger = getLogger(__name__)

        super().__init__(partialName=partialName, pyutObject=pyutObject, umlPosition=umlPosition, umlFrame=umlFrame, umlPubSubEngine=umlPubSubEngine)

    def _undo(self, umlShape: UmlShape):
        """
        Common code for basic Undo
        Args:
            umlShape:  The shape to remove from the frame

        """
        self._removeShape(umlShape=umlShape)
