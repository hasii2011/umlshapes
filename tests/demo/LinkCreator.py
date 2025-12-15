
from typing import Union
from typing import cast
from typing import Dict
from typing import NewType
from typing import Tuple

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.Note import Note
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlNoteLink import UmlNoteLink

from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import Identifiers
from tests.demo.DemoCommon import ID_REFERENCE

INITIAL_X:   int = 100
INITIAL_Y:   int = 100

INCREMENT_X: int = 25
INCREMENT_Y: int = 25

LinkEventHandler = Union[UmlAssociationEventHandler, UmlLinkEventHandler]


@dataclass
class AssociationDescription:
    associationClass: type[UmlAssociation] = cast(type[UmlAssociation], None)
    linkType:         LinkType             = LinkType.ASSOCIATION


RelationshipDescription = NewType('RelationshipDescription', Dict[ID_REFERENCE, AssociationDescription])


class LinkCreator:
    """
    Not those kinds, dork
    """
    def __init__(self, umlPubSubEngine: UmlPubSubEngine):

        self._umlPubSubEngine: UmlPubSubEngine   = umlPubSubEngine

        self.logger:           Logger         = getLogger(__name__)
        self._preferences:     UmlPreferences = UmlPreferences()
        self._currentPosition: UmlPosition    = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        self._classCounter:       int = 0
        self._associationCounter: int = 0
        self._inheritanceCounter: int = 0

        association: AssociationDescription = AssociationDescription(
            linkType=LinkType.ASSOCIATION,
            associationClass=UmlAssociation
        )
        composition: AssociationDescription = AssociationDescription(
            linkType=LinkType.COMPOSITION,
            associationClass=UmlComposition
        )
        aggregation: AssociationDescription = AssociationDescription(
            linkType=LinkType.AGGREGATION,
            associationClass=UmlAggregation
        )
        self._associations: RelationshipDescription = RelationshipDescription(
            {
                Identifiers.ID_DISPLAY_UML_ASSOCIATION: association,
                Identifiers.ID_DISPLAY_UML_COMPOSITION: composition,
                Identifiers.ID_DISPLAY_UML_AGGREGATION: aggregation,
            }
        )

    def displayAssociation(self, idReference: ID_REFERENCE, diagramFrame: ClassDiagramFrame):

        associationDescription: AssociationDescription = self._associations[idReference]

        sourceUmlClass, destinationUmlClass = self._createClassPair(diagramFrame=diagramFrame)
        self.logger.info(f'{sourceUmlClass.id=} {destinationUmlClass.id=}')

        modelLink = self._createAssociationModelLink(linkType=associationDescription.linkType)

        modelLink.name = f'{associationDescription.linkType}-{self._associationCounter}'
        self._associationCounter += 1

        umlAssociation: UmlAssociation = associationDescription.associationClass(link=modelLink)

        umlAssociation.umlFrame = diagramFrame
        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceUmlClass.addLink(umlLink=umlAssociation, destinationClass=destinationUmlClass)

        diagramFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)
        #
        # I know this looks weird but we do not need the variable
        UmlAssociationEventHandler(umlAssociation=umlAssociation, umlPubSubEngine=self._umlPubSubEngine)

    def displayUmlInheritance(self, diagramFrame: ClassDiagramFrame):
        """
        """
        baseUmlClass, subUmlClass = self._createClassPair(diagramFrame=diagramFrame)
        baseUmlClass.modelClass.name = 'Base Class'
        subUmlClass.modelClass.name  = 'SubClass'

        modelInheritance: Link = self._createInheritanceModelLink(baseUmlClass=baseUmlClass, subUmlClass=subUmlClass)

        umlInheritance: UmlInheritance = UmlInheritance(link=modelInheritance, baseClass=baseUmlClass, subClass=subUmlClass)
        umlInheritance.umlFrame = diagramFrame
        umlInheritance.MakeLineControlPoints(n=2)       # Make this configurable

        # REMEMBER:   from subclass to base class
        subUmlClass.addLink(umlLink=umlInheritance, destinationClass=baseUmlClass)

        diagramFrame.umlDiagram.AddShape(umlInheritance)
        umlInheritance.Show(True)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInheritance, previousEventHandler=umlInheritance.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlInheritance.SetEventHandler(eventHandler)

    def displayUmlInterface(self, diagramFrame: ClassDiagramFrame):

        interfaceClass, implementingClass = self._createClassPair(diagramFrame=diagramFrame)

        interfaceClass.modelClass.name     = f'InterfaceClass-{self._classCounter}'
        self._classCounter += 1
        implementingClass.modelClass.name  = f'ImplementingClass-{self._classCounter}'
        self._classCounter += 1

        modelInterface: Link = self._createInterfaceModelLink()

        modelInterface.destination  = implementingClass.modelClass
        modelInterface.source       = interfaceClass.modelClass

        umlInterface: UmlInterface = UmlInterface(link=modelInterface, interfaceClass=interfaceClass, implementingClass=implementingClass)
        umlInterface.umlFrame = diagramFrame
        umlInterface.MakeLineControlPoints(n=2)

        implementingClass.addLink(umlLink=umlInterface, destinationClass=interfaceClass)

        diagramFrame.umlDiagram.AddShape(umlInterface)
        umlInterface.Show(True)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInterface, previousEventHandler=umlInterface.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlInterface.SetEventHandler(eventHandler)

    def displayNoteLink(self, diagramFrame: ClassDiagramFrame):
        classPosition: UmlPosition = UmlPosition(x=450, y=100)

        umlNote: UmlNote = self._createUmlNote()

        modelClass: Class = self._createSimpleModelClass(classCounter=self._classCounter)
        umlClass:  UmlClass  = UmlClass(modelClass=modelClass, size=UmlDimensions(100, 50))

        self._displayUmlClass(umlClass=umlClass, umlPosition=classPosition, diagramFrame=diagramFrame)

        modelLink:    Link    = Link(linkType=LinkType.NOTELINK)
        umlNoteLink: UmlNoteLink = UmlNoteLink(link=modelLink)
        umlNoteLink.MakeLineControlPoints(2)
        umlNoteLink.sourceNote       = umlNote
        umlNoteLink.destinationClass = umlClass
        umlNoteLink.umlPubSubEngine  = self._umlPubSubEngine

        umlNote.umlFrame  = diagramFrame

        umlClass.umlFrame = diagramFrame

        diagramFrame.umlDiagram.AddShape(umlNote)
        diagramFrame.umlDiagram.AddShape(umlClass)
        diagramFrame.umlDiagram.AddShape(umlNoteLink)

        umlNote.Show(True)
        umlNoteLink.Show(True)

        self._associateClassEventHandler(umlClass=umlClass)
        self._associateNoteLinkEventHandler(umlNoteLink=umlNoteLink)

        umlNote.addLink(umlNoteLink=umlNoteLink, umlClass=umlClass)

        diagramFrame.refresh()

    def _createClassPair(self, diagramFrame: ClassDiagramFrame) -> Tuple[UmlClass, UmlClass]:

        sourcePosition:       UmlPosition = UmlPosition(x=100, y=100)       # fix this should be input
        destinationPosition:  UmlPosition = UmlPosition(x=200, y=300)

        sourceModelClass:      Class   = self._createSimpleModelClass(classCounter=self._classCounter)
        self._classCounter += 1
        destinationModelClass: Class   = self._createSimpleModelClass(classCounter=self._classCounter)
        self._classCounter += 1

        sourceUmlClass:      UmlClass = UmlClass(modelClass=sourceModelClass)
        destinationUmlClass: UmlClass = UmlClass(modelClass=destinationModelClass)

        self._displayUmlClass(umlClass=sourceUmlClass, umlPosition=sourcePosition, diagramFrame=diagramFrame)
        self._displayUmlClass(umlClass=destinationUmlClass, umlPosition=destinationPosition, diagramFrame=diagramFrame)

        self._associateClassEventHandler(umlClass=sourceUmlClass)
        self._associateClassEventHandler(umlClass=destinationUmlClass)

        return sourceUmlClass, destinationUmlClass

    def _createSimpleModelClass(self, classCounter: int) -> Class:

        className: str = f'{self._preferences.defaultClassName}-{classCounter}'
        classCounter += 1
        modelClass: Class  = Class(name=className)

        return modelClass

    def _createAssociationModelLink(self, linkType: LinkType) -> Link:

        name: str = f'{self._preferences.defaultAssociationName}-{self._associationCounter}'
        modelLink: Link = Link(name=name, linkType=linkType)

        modelLink.sourceCardinality      = 'src Card'
        modelLink.destinationCardinality = 'dst Card'

        return modelLink

    def _createInheritanceModelLink(self, baseUmlClass: UmlClass, subUmlClass: UmlClass) -> Link:

        name: str = f'Inheritance-{self._inheritanceCounter}'

        modelInheritance: Link = Link(name=name, linkType=LinkType.INHERITANCE)

        modelInheritance.destination  = baseUmlClass.modelClass
        modelInheritance.source       = subUmlClass.modelClass

        self._inheritanceCounter += 1
        return modelInheritance

    def _createInterfaceModelLink(self):

        name: str = f'implements'
        modelInterface: Link = Link(name=name, linkType=LinkType.INTERFACE)

        return modelInterface

    def _associateClassEventHandler(self, umlClass: UmlClass):

        eventHandler: UmlClassEventHandler = UmlClassEventHandler(previousEventHandler=umlClass.GetEventHandler())

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetShape(umlClass)

        umlClass.SetEventHandler(eventHandler)

    def _associateNoteLinkEventHandler(self, umlNoteLink: UmlNoteLink):

        eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink, previousEventHandler=umlNoteLink.GetEventHandler())
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlNoteLink.SetEventHandler(eventHandler)

    def _createUmlNote(self) -> UmlNote:

        modelNote: Note    = Note(content='I am a great note')
        umlNote:   UmlNote = UmlNote(note=modelNote)

        notePosition:  UmlPosition = UmlPosition(x=100, y=100)

        umlNote.size     = UmlDimensions(width=150, height=50)
        umlNote.modelNote = modelNote
        umlNote.position = notePosition

        eventHandler: UmlNoteEventHandler = UmlNoteEventHandler(previousEventHandler=umlNote.GetEventHandler())

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetShape(umlNote)
        umlNote.SetEventHandler(eventHandler)

        return umlNote

    def _displayUmlClass(self, umlClass: UmlClass, umlPosition: UmlPosition, diagramFrame: ClassDiagramFrame):

        diagram: UmlDiagram = diagramFrame.umlDiagram

        umlClass.position = umlPosition
        umlClass.umlFrame = diagramFrame

        diagram.AddShape(umlClass)
        umlClass.Show(show=True)

        diagramFrame.refresh()
