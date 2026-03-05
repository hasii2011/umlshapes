
from typing import TYPE_CHECKING

from umlshapes.commands.BaseLinkCommand import BaseLinkCommand
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlLinkGenre


class DeleteLinkCommand(BaseLinkCommand):

    def __init__(self, partialName: str, umlLink: 'UmlLinkGenre', umlPubSubEngine: IUmlPubSubEngine):

        super().__init__(
            partialName=partialName,
            umlPubSubEngine=umlPubSubEngine,
            linkSourcePosition=umlLink.endPositions.fromPosition,
            linkDestinationPosition=umlLink.endPositions.toPosition
        )
        self._umlLink             = umlLink
        self._sourceUmlShape      = umlLink.sourceShape
        self._destinationUmlShape = umlLink.destinationShape
        self._modelLink           = umlLink.modelLink
        self._linkType            = umlLink.modelLink.linkType
        self._umlFrame            = umlLink.umlFrame

    def Do(self) -> bool:

        self._deleteLink()

        return True

    def Undo(self) -> bool:

        self._createLink()

        return True
