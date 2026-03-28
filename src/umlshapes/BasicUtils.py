from typing import cast

from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import LinkableUmlShape
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlLink import UmlLink


class BasicUtils:

    @classmethod
    def rationalizeTheLinkDataModel(cls, umlLink: UmlLink):
        """
        Updates one of the following lists in a LinkedObject data model

        ._parents   for Inheritance and Interface links (modelClass.addParent()
        ._links     for all other link types (modelClass.addLink())

        Note:  Abuses the fact that objects are passed by reference.
        So we access the shapes on the link and update their data model

        Args:
            umlLink:       A UML Link
        """
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.UmlUseCase import UmlUseCase

        modelLink: Link = umlLink.modelLink

        if modelLink.linkType == LinkType.INHERITANCE:
            inheritanceLink: UmlInheritance = cast(UmlInheritance, umlLink)
            inheritanceLink.subClass.modelClass.addParent(inheritanceLink.baseClass.modelClass)

        elif modelLink.linkType == LinkType.INTERFACE:
            interfaceLink: UmlInterface = cast(UmlInterface, umlLink)
            interfaceLink.implementingClass.modelClass.addParent(interfaceLink.interfaceClass.modelClass)

        else:
            srcShape: LinkableUmlShape = umlLink.sourceShape

            if isinstance(srcShape, UmlClass):
                srcShape.modelClass.addLink(modelLink)
            elif isinstance(srcShape, UmlNote):
                srcShape.modelNote.addLink(modelLink)
            elif isinstance(srcShape, UmlActor):
                srcShape.modelActor.addLink(modelLink)
            elif isinstance(srcShape, UmlUseCase):
                srcShape.modelUseCase.addLink(modelLink)
