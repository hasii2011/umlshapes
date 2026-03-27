
from typing import Union
from typing import cast
from typing import Dict
from typing import Tuple
from typing import NewType

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from enum import StrEnum
from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.Note import Note
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.commands.CreateLinkCommand import CreateLinkCommand

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.links.UmlNoteLink import UmlNoteLink
from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlComposition import UmlComposition

from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler

from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions
from umlshapes.types.UmlDimensions import UmlDimensions

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


class SmartPlacement(StrEnum):
    SOURCE_ABOVE  = 'Source Above'
    SOURCE_BELOW  = 'Source Below'
    SOURCE_LEFT   = 'Source Left'
    SOURCE_RIGHT  = 'Source Right'
    SOURCE_225    = 'Source 225'


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

    def displaySmartPlacement(self, diagramFrame: ClassDiagramFrame, placement: SmartPlacement):
        #
        # default to source left
        #
        sourcePosition:      UmlPosition = UmlPosition(x=100, y=100)
        destinationPosition: UmlPosition = UmlPosition(x=200, y=300)

        if placement == SmartPlacement.SOURCE_RIGHT:
            sourcePosition      = UmlPosition(x=200, y=300)
            destinationPosition = UmlPosition(x=100, y=100)
        elif placement == SmartPlacement.SOURCE_ABOVE:
            sourcePosition      = UmlPosition(x=200, y=300)
            destinationPosition = UmlPosition(x=200, y=600)
        elif placement == SmartPlacement.SOURCE_BELOW:
            sourcePosition      = UmlPosition(x=200, y=600)
            destinationPosition = UmlPosition(x=200, y=300)
        elif placement == SmartPlacement.SOURCE_225:
            sourcePosition      = UmlPosition(x=300, y=100)
            destinationPosition = UmlPosition(x=400, y=400)

        sourceUmlClass, destinationUmlClass = self._createClassPair(diagramFrame=diagramFrame, sourcePosition=sourcePosition, destinationPosition=destinationPosition)

        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            partialName=f'{LinkType.AGGREGATION}',
            sourceShape=sourceUmlClass,
            destinationShape=destinationUmlClass,
            linkType=LinkType.AGGREGATION,
            umlPubSubEngine=self._umlPubSubEngine
        )
        diagramFrame.commandProcessor.Submit(command=createLinkCommand, storeIt=True)

    def displayAssociation(self, idReference: ID_REFERENCE, diagramFrame: ClassDiagramFrame):

        associationDescription: AssociationDescription = self._associations[idReference]

        sourceUmlClass, destinationUmlClass = self._createClassPair(diagramFrame=diagramFrame)
        self.logger.info(f'{sourceUmlClass.id=} {destinationUmlClass.id=}')

        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            partialName=f'{associationDescription.linkType}',
            sourceShape=sourceUmlClass,
            destinationShape=destinationUmlClass,
            linkType=associationDescription.linkType,
            umlPubSubEngine=self._umlPubSubEngine
        )
        diagramFrame.commandProcessor.Submit(command=createLinkCommand, storeIt=True)

    def displayUmlInheritance(self, diagramFrame: ClassDiagramFrame):
        """
        """
        baseUmlClass, subUmlClass = self._createClassPair(diagramFrame=diagramFrame)
        baseUmlClass.modelClass.name = 'Base Class'
        subUmlClass.modelClass.name  = 'SubClass'

        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            partialName=f'{LinkType.INHERITANCE}',
            sourceShape=subUmlClass,
            destinationShape=baseUmlClass,
            linkType=LinkType.INHERITANCE,
            umlPubSubEngine=self._umlPubSubEngine
        )
        diagramFrame.commandProcessor.Submit(command=createLinkCommand, storeIt=True)

    def displayUmlInterface(self, diagramFrame: ClassDiagramFrame):

        interfaceClass, implementingClass = self._createClassPair(diagramFrame=diagramFrame)

        interfaceClass.modelClass.name     = f'InterfaceClass-{self._classCounter}'
        self._classCounter += 1
        implementingClass.modelClass.name  = f'ImplementingClass-{self._classCounter}'
        self._classCounter += 1

        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            partialName=f'{LinkType.INTERFACE}',
            sourceShape=implementingClass,
            destinationShape=interfaceClass,
            linkType=LinkType.INTERFACE,
            umlPubSubEngine=self._umlPubSubEngine
        )
        diagramFrame.commandProcessor.Submit(command=createLinkCommand, storeIt=True)

    def displayNoteLink(self, diagramFrame: ClassDiagramFrame):
        classPosition: UmlPosition = UmlPosition(x=450, y=100)

        umlNote: UmlNote = self._createUmlNote()

        modelClass: Class     = self._createSimpleModelClass(classCounter=self._classCounter)
        umlClass:   UmlClass  = UmlClass(modelClass=modelClass, size=UmlDimensions(100, 50))

        umlNote.umlFrame  = diagramFrame
        diagramFrame.umlDiagram.AddShape(umlNote)
        umlNote.Show(True)
        self._associateClassEventHandler(umlClass=umlClass)
        self._displayUmlClass(umlClass=umlClass, umlPosition=classPosition, diagramFrame=diagramFrame)

        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            partialName=f'{LinkType.NOTELINK}',
            sourceShape=umlNote,
            destinationShape=umlClass,
            linkType=LinkType.NOTELINK,
            umlPubSubEngine=self._umlPubSubEngine
        )
        diagramFrame.commandProcessor.Submit(command=createLinkCommand, storeIt=True)

    def displayOrthogonalLink(self, diagramFrame: ClassDiagramFrame):
        baseClassPosition: UmlPosition = UmlPosition(x=180, y=205)
        subClassPosition:  UmlPosition = UmlPosition(x=550, y=480)

        baseModelClass:     Class  = Class(name='BaseClass')
        subClassModelClass: Class = Class(name='SubClass')

        baseUmlClass:     UmlClass = UmlClass(modelClass=baseModelClass)
        subClassUmlClass: UmlClass = UmlClass(modelClass=subClassModelClass)

        self._displayUmlClass(umlClass=baseUmlClass,     umlPosition=baseClassPosition, diagramFrame=diagramFrame)
        self._displayUmlClass(umlClass=subClassUmlClass, umlPosition=subClassPosition,  diagramFrame=diagramFrame)

        self._associateClassEventHandler(umlClass=baseUmlClass)
        self._associateClassEventHandler(umlClass=subClassUmlClass)

        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            partialName=f'{LinkType.INHERITANCE}',
            sourceShape=subClassUmlClass,
            destinationShape=baseUmlClass,
            linkType=LinkType.INHERITANCE,
            umlPubSubEngine=self._umlPubSubEngine,
            linkSourcePosition=UmlPosition(x=625, y=480),
            linkDestinationPosition=UmlPosition(x=327, y=250),
            linkControlPositions=UmlPositions([UmlPosition(x=625, y=250)])
        )
        diagramFrame.commandProcessor.Submit(command=createLinkCommand, storeIt=True)

    def _createClassPair(self,
                         diagramFrame:        ClassDiagramFrame,
                         sourcePosition:      UmlPosition = UmlPosition(x=100, y=100),
                         destinationPosition: UmlPosition = UmlPosition(x=200, y=300),
                         ) -> Tuple[UmlClass, UmlClass]:

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
