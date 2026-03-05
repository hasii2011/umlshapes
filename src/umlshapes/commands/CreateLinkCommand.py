
from typing import TYPE_CHECKING
from typing import cast

from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.commands.BaseLinkCommand import BaseLinkCommand
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlShapeGenre


class CreateLinkCommand(BaseLinkCommand):

    LinkCounter: int = 0

    def __init__(self, partialName: str, sourceShape: 'UmlShapeGenre', destinationShape: 'UmlShapeGenre', linkType: LinkType, umlPubSubEngine: IUmlPubSubEngine):
        super().__init__(
            partialName=partialName,
            umlPubSubEngine=umlPubSubEngine,
        )
        self._preferences: UmlPreferences = UmlPreferences()

        self._sourceUmlShape      = sourceShape
        self._destinationUmlShape = destinationShape

        if linkType == LinkType.ASSOCIATION or linkType == LinkType.AGGREGATION or linkType == LinkType.COMPOSITION:
            self._modelLink = self._createAssociationModelLink(linkType=linkType)
        elif linkType == LinkType.INHERITANCE:
            self._modelLink = self._createInheritanceModelLink(
                baseUmlClass=cast(UmlClass, self._destinationUmlShape),     # noqa
                subUmlClass=cast(UmlClass, self._sourceUmlShape)            # noqa
            )
        elif linkType == LinkType.INTERFACE:
            self._modelLink = self._createInterfaceModelLink()
        elif linkType == LinkType.NOTELINK:
            self._modelLink = Link(linkType=LinkType.NOTELINK)
        else:
            assert False, f'Unhandled link type: {linkType}'

        self._linkType            = linkType
        self._umlFrame            = sourceShape.umlFrame

    def Do(self) -> bool:

        self._createLink()

        return True

    def Undo(self) -> bool:

        self._deleteLink()

        return True

    def _createAssociationModelLink(self, linkType: LinkType) -> Link:

        name: str = f'{self._preferences.defaultAssociationName}-{CreateLinkCommand.LinkCounter}'
        modelLink: Link = Link(name=name, linkType=linkType)

        modelLink.sourceCardinality      = 'src Card'
        modelLink.destinationCardinality = 'dst Card'
        if isinstance(self._sourceUmlShape, UmlClass) and isinstance(self._destinationUmlShape, UmlClass):
            modelLink.source      = self._sourceUmlShape.modelClass
            modelLink.destination = self._destinationUmlShape.modelClass

        CreateLinkCommand.LinkCounter += 1
        return modelLink

    def _createInheritanceModelLink(self, baseUmlClass: UmlClass, subUmlClass: UmlClass) -> Link:

        name: str = f'Inheritance-{CreateLinkCommand.LinkCounter}'

        modelInheritance: Link = Link(name=name, linkType=LinkType.INHERITANCE)

        modelInheritance.destination = baseUmlClass.modelClass
        modelInheritance.source      = subUmlClass.modelClass

        CreateLinkCommand.LinkCounter += 1
        return modelInheritance

    def _createInterfaceModelLink(self):

        name: str = f'implements'
        modelInterface: Link = Link(name=name, linkType=LinkType.INTERFACE)

        return modelInterface
