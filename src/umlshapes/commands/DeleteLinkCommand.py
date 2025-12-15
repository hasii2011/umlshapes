
from typing import List
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from datetime import datetime

from wx import Command

from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlLinkGenre
    from umlshapes.ShapeTypes import UmlShapeGenre
    from umlshapes.shapes.UmlClass import UmlClass
    from umlshapes.shapes.UmlNote import UmlNote
    from umlshapes.links.UmlInterface import UmlInterface
    from umlshapes.links.UmlAssociation import UmlAssociation
    from umlshapes.links.UmlInheritance import UmlInheritance
    from umlshapes.links.UmlNoteLink import UmlNoteLink

MODEL_ASSOCIATION_LINK_TYPE: List[LinkType] = [LinkType.ASSOCIATION, LinkType.AGGREGATION, LinkType.COMPOSITION]

class DeleteLinkCommand(Command):

    def __init__(self, partialName: str, umlLink: 'UmlLinkGenre', umlPubSubEngine: IUmlPubSubEngine):

        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.frames.UmlFrame import UmlFrame

        self.logger: Logger = getLogger(__name__)

        self._name:            str              = f'{partialName}-{self.timeStamp}'      # Because Command.GetName() does not really work
        #
        # Only use this for deletion;  Will be re-created on Undo
        self._umlLink:         UmlLinkGenre     = umlLink
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        # So we can recreate the Link
        self._modelLink: Link = umlLink.modelLink
        #
        # Save the ends for Undo
        #
        self._sourceUmlShape:      UmlShapeGenre = umlLink.sourceShape
        self._destinationUmlShape: UmlShapeGenre = umlLink.destinationShape
        self._umlFrame:            UmlFrame      = umlLink.umlFrame

        super().__init__(canUndo=True, name=self._name)

    @property
    def timeStamp(self) -> int:

        dt = datetime.now()

        return dt.microsecond

    def Do(self) -> bool:
        from umlshapes.links.UmlAssociation import UmlAssociation
        from umlshapes.UmlDiagram import UmlDiagram

        if isinstance(self._umlLink, UmlAssociation):
            umlAssociation: UmlAssociation = self._umlLink
            umlDiagram:     UmlDiagram     = self._umlFrame.umlDiagram

            umlDiagram.RemoveShape(umlAssociation.associationName)
            umlDiagram.RemoveShape(umlAssociation.sourceCardinality)
            umlDiagram.RemoveShape(umlAssociation.destinationCardinality)

        self._umlLink.selected = False  # To remove handles
        self._umlLink.Delete()

        self._umlFrame.refresh()

        return True

    def Undo(self) -> bool:
        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.links.UmlAssociation import UmlAssociation
        from umlshapes.links.UmlInheritance import UmlInheritance
        from umlshapes.links.UmlInterface import UmlInterface
        from umlshapes.links.UmlNoteLink import UmlNoteLink

        sourceUmlShape:      UmlClass   = cast(UmlClass, self._sourceUmlShape)
        destinationUmlShape: UmlClass   = cast(UmlClass, self._destinationUmlShape)
        umlDiagram:          UmlDiagram = self._umlFrame.umlDiagram
        #
        # HAVE TO HANDLE ALL THE OTHER LINKS,  INTERFACE, INHERITANCE, NOTE LINK
        #
        if self._modelLink.linkType in MODEL_ASSOCIATION_LINK_TYPE:
            umlAssociation: UmlAssociation = self._createUmlAssociation(destinationUmlShape, sourceUmlShape)

            umlDiagram.AddShape(umlAssociation)
            umlAssociation.Show(True)
            # RECREATED !!!
            self._umlLink = umlAssociation
        elif self._modelLink.linkType == LinkType.INHERITANCE:
            umlInheritance: UmlInheritance = self._createInheritanceLink(baseClass=destinationUmlShape, subClass=sourceUmlShape)

            umlDiagram.AddShape(umlInheritance)
            umlInheritance.Show(True)
            # RECREATED !!!
            self._umlLink = umlInheritance
        elif self._modelLink.linkType == LinkType.INTERFACE:
            umlInterface: UmlInterface = self._createInterfaceLink(interfaceClass=destinationUmlShape, implementingClass=sourceUmlShape)

            umlDiagram.AddShape(umlInterface)
            umlInterface.Show(True)
            # RECREATED !!!
            self._umlLink = umlInterface
        elif self._modelLink.linkType == LinkType.NOTELINK:

            umlNote: UmlNote = cast(UmlNote, sourceUmlShape)

            umlNoteLink: UmlNoteLink = self._createNoteLink(umlClass=destinationUmlShape, umlNote=umlNote)

            umlDiagram.AddShape(umlNoteLink)
            umlNoteLink.Show(True)
            # RECREATED !!!
            self._umlLink = umlNoteLink

        return True

    def _createUmlAssociation(self, sourceUmlShape: 'UmlClass', destinationUmlShape: 'UmlClass') -> 'UmlAssociation':
        """

        Args:
            sourceUmlShape:         The source of the association
            destinationUmlShape:    The destination for the association

        Returns:  The appropriate UML Association based on the model Link Type
        """
        from umlshapes.links.UmlAssociation import UmlAssociation
        from umlshapes.links.UmlComposition import UmlComposition
        from umlshapes.links.UmlAggregation import UmlAggregation

        from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler

        if self._modelLink.linkType == LinkType.COMPOSITION:
            umlAssociation: UmlAssociation = UmlComposition(link=self._modelLink)
        elif self._modelLink.linkType == LinkType.AGGREGATION:
            umlAssociation = UmlAggregation(link=self._modelLink)
        else:
            umlAssociation = UmlAssociation(link=self._modelLink)

        umlAssociation.umlFrame = self._umlFrame
        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.MakeLineControlPoints(n=2)  # Make this configurable

        # Looks weird but we do not need the result
        UmlAssociationEventHandler(umlAssociation=umlAssociation, umlPubSubEngine=self._umlPubSubEngine)

        sourceUmlShape.addLink(umlLink=umlAssociation, destinationClass=destinationUmlShape)

        return umlAssociation

    def _createInheritanceLink(self, baseClass: 'UmlClass', subClass: 'UmlClass') -> 'UmlInheritance':
        """

        Args:
            baseClass:  The base class that represents the inheritance
            subClass:   the bas class that UML subclasses from the base class

        Returns:  The appropriate UML Inheritance Link
        """
        from umlshapes.links.UmlInheritance import UmlInheritance
        from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler

        umlInheritance: UmlInheritance = UmlInheritance(link=self._modelLink, baseClass=baseClass, subClass=subClass)
        umlInheritance.umlFrame = self._umlFrame
        umlInheritance.MakeLineControlPoints(n=2)       # Make this configurable

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInheritance, previousEventHandler=umlInheritance.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlInheritance.SetEventHandler(eventHandler)

        # REMEMBER:   from subclass to base class
        subClass.addLink(umlLink=umlInheritance, destinationClass=baseClass)

        return umlInheritance

    def _createInterfaceLink(self, interfaceClass: 'UmlClass', implementingClass: 'UmlClass') -> 'UmlInterface':
        from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
        from umlshapes.links.UmlInterface import UmlInterface

        umlInterface: UmlInterface = UmlInterface(link=self._modelLink, interfaceClass=interfaceClass, implementingClass=implementingClass)
        umlInterface.umlFrame = self._umlFrame
        umlInterface.MakeLineControlPoints(n=2)     # Make this configurable

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInterface, previousEventHandler=umlInterface.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlInterface.SetEventHandler(eventHandler)

        implementingClass.addLink(umlLink=umlInterface, destinationClass=interfaceClass)

        return umlInterface

    def _createNoteLink(self, umlClass: 'UmlClass', umlNote: 'UmlNote') -> 'UmlNoteLink':
        from umlshapes.links.UmlNoteLink import UmlNoteLink

        from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler

        umlNoteLink: UmlNoteLink = UmlNoteLink(link=self._modelLink)
        umlNoteLink.umlFrame  = self._umlFrame
        umlNoteLink.MakeLineControlPoints(2)        # Make this configurable

        umlNoteLink.sourceNote       = umlNote
        umlNoteLink.destinationClass = umlClass
        umlNoteLink.umlPubSubEngine  = self._umlPubSubEngine

        eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink, previousEventHandler=umlNoteLink.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlNoteLink.SetEventHandler(eventHandler)

        umlNote.addLink(umlNoteLink=umlNoteLink, umlClass=umlClass)

        return umlNoteLink

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True
