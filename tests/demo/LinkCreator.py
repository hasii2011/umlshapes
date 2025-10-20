
from typing import Union
from typing import cast
from typing import Dict
from typing import NewType
from typing import Tuple

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutNote import PyutNote

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.links.eventhandlers.UmlNoteLinkEventHandler import UmlNoteLinkEventHandler

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlNoteLink import UmlNoteLink

from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
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
    associationClass:   type[UmlAssociation]  = cast(type[UmlAssociation], None)
    linkType:           PyutLinkType          = PyutLinkType.ASSOCIATION


RelationshipDescription = NewType('RelationshipDescription', Dict[ID_REFERENCE, AssociationDescription])


class LinkCreator:
    """
    Not those kinds, dork
    """
    def __init__(self, diagramFrame: ClassDiagramFrame, umlPubSubEngine: UmlPubSubEngine):

        self._diagramFrame:    ClassDiagramFrame = diagramFrame
        self._umlPubSubEngine: UmlPubSubEngine   = umlPubSubEngine

        self.logger:           Logger         = getLogger(__name__)
        self._preferences:     UmlPreferences = UmlPreferences()
        self._currentPosition: UmlPosition    = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        self._classCounter:       int = 0
        self._associationCounter: int = 0
        self._inheritanceCounter: int = 0

        association: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.ASSOCIATION,
            associationClass=UmlAssociation
        )
        composition: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.COMPOSITION,
            associationClass=UmlComposition
        )
        aggregation: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.AGGREGATION,
            associationClass=UmlAggregation
        )
        self._associations: RelationshipDescription = RelationshipDescription(
            {
                Identifiers.ID_DISPLAY_UML_ASSOCIATION: association,
                Identifiers.ID_DISPLAY_UML_COMPOSITION: composition,
                Identifiers.ID_DISPLAY_UML_AGGREGATION: aggregation,
            }
        )

    def displayAssociation(self, idReference: ID_REFERENCE):

        associationDescription: AssociationDescription = self._associations[idReference]

        sourceUmlClass, destinationUmlClass = self._createClassPair()
        self.logger.info(f'{sourceUmlClass.id=} {destinationUmlClass.id=}')

        pyutLink = self._createAssociationPyutLink()

        pyutLink.name = f'{associationDescription.linkType}-{self._associationCounter}'
        self._associationCounter += 1

        umlAssociation: UmlAssociation = associationDescription.associationClass(pyutLink=pyutLink)

        umlAssociation.umlFrame = self._diagramFrame
        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceUmlClass.addLink(umlLink=umlAssociation, destinationClass=destinationUmlClass)

        self._diagramFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)

        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation)

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

    def displayUmlInheritance(self):
        """
        """
        baseUmlClass, subUmlClass = self._createClassPair()
        baseUmlClass.pyutClass.name = 'Base Class'
        subUmlClass.pyutClass.name  = 'SubClass'

        pyutInheritance: PyutLink = self._createInheritancePyutLink(baseUmlClass=baseUmlClass, subUmlClass=subUmlClass)

        umlInheritance: UmlInheritance = UmlInheritance(pyutLink=pyutInheritance, baseClass=baseUmlClass, subClass=subUmlClass)
        umlInheritance.umlFrame = self._diagramFrame
        umlInheritance.MakeLineControlPoints(n=2)       # Make this configurable

        # REMEMBER:   from subclass to base class
        subUmlClass.addLink(umlLink=umlInheritance, destinationClass=baseUmlClass)

        self._diagramFrame.umlDiagram.AddShape(umlInheritance)
        umlInheritance.Show(True)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInheritance)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlInheritance.GetEventHandler())
        umlInheritance.SetEventHandler(eventHandler)

    def displayUmlInterface(self):

        interfaceClass, implementingClass = self._createClassPair()

        interfaceClass.pyutClass.name     = f'InterfaceClass-{self._classCounter}'
        self._classCounter += 1
        implementingClass.pyutClass.name  = f'ImplementingClass-{self._classCounter}'
        self._classCounter += 1

        pyutInterface: PyutLink = self._createInterfacePyutLink()

        pyutInterface.destination  = implementingClass.pyutClass
        pyutInterface.source       = interfaceClass.pyutClass

        umlInterface: UmlInterface = UmlInterface(pyutLink=pyutInterface, interfaceClass=interfaceClass, implementingClass=implementingClass)
        umlInterface.umlFrame = self._diagramFrame
        umlInterface.MakeLineControlPoints(n=2)

        implementingClass.addLink(umlLink=umlInterface, destinationClass=interfaceClass)

        self._diagramFrame.umlDiagram.AddShape(umlInterface)
        umlInterface.Show(True)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInterface)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlInterface.GetEventHandler())
        umlInterface.SetEventHandler(eventHandler)

    def displayNoteLink(self):
        classPosition: UmlPosition = UmlPosition(x=450, y=100)

        umlNote: UmlNote = self._createUmlNote()

        pyutClass: PyutClass = self._createSimplePyutClass(classCounter=self._classCounter)
        umlClass:  UmlClass  = UmlClass(pyutClass=pyutClass, size=UmlDimensions(100, 50))

        self._displayUmlClass(umlClass=umlClass, umlPosition=classPosition)

        pyutLink:    PyutLink    = PyutLink(linkType=PyutLinkType.NOTELINK)
        umlNoteLink: UmlNoteLink = UmlNoteLink(pyutLink=pyutLink)
        umlNoteLink.MakeLineControlPoints(2)
        umlNoteLink.sourceNote       = umlNote
        umlNoteLink.destinationClass = umlClass
        umlNoteLink.umlPubSubEngine  = self._umlPubSubEngine

        umlNote.umlFrame  = self._diagramFrame

        umlClass.umlFrame = self._diagramFrame
        umlNote.addLink(umlNoteLink=umlNoteLink, umlClass=umlClass)

        self._diagramFrame.umlDiagram.AddShape(umlNote)
        self._diagramFrame.umlDiagram.AddShape(umlClass)
        self._diagramFrame.umlDiagram.AddShape(umlNoteLink)

        umlNote.Show(True)
        umlNoteLink.Show(True)

        self._associateClassEventHandler(umlClass=umlClass)
        self._associateNoteLinkEventHandler(umlNoteLink=umlNoteLink)

        umlNote.addLink(umlNoteLink=umlNoteLink, umlClass=umlClass)

        self._diagramFrame.refresh()

    def _createClassPair(self) -> Tuple[UmlClass, UmlClass]:

        sourcePosition:       UmlPosition = UmlPosition(x=100, y=100)       # fix this should be input
        destinationPosition:  UmlPosition = UmlPosition(x=200, y=300)

        sourcePyutClass:      PyutClass   = self._createSimplePyutClass(classCounter=self._classCounter)
        self._classCounter += 1
        destinationPyutClass: PyutClass   = self._createSimplePyutClass(classCounter=self._classCounter)
        self._classCounter += 1

        sourceUmlClass:      UmlClass = UmlClass(pyutClass=sourcePyutClass)
        destinationUmlClass: UmlClass = UmlClass(pyutClass=destinationPyutClass)

        self._displayUmlClass(umlClass=sourceUmlClass, umlPosition=sourcePosition)
        self._displayUmlClass(umlClass=destinationUmlClass, umlPosition=destinationPosition)

        self._associateClassEventHandler(umlClass=sourceUmlClass)
        self._associateClassEventHandler(umlClass=destinationUmlClass)

        return sourceUmlClass, destinationUmlClass

    def _createSimplePyutClass(self, classCounter: int) -> PyutClass:

        className: str = f'{self._preferences.defaultClassName}-{classCounter}'
        classCounter += 1
        pyutClass: PyutClass  = PyutClass(name=className)

        return pyutClass

    def _createAssociationPyutLink(self) -> PyutLink:

        name: str = f'{self._preferences.defaultAssociationName}-{self._associationCounter}'
        pyutLink: PyutLink = PyutLink(name=name, linkType=PyutLinkType.ASSOCIATION)

        pyutLink.sourceCardinality      = 'src Card'
        pyutLink.destinationCardinality = 'dst Card'

        return pyutLink

    def _createInheritancePyutLink(self, baseUmlClass: UmlClass, subUmlClass: UmlClass) -> PyutLink:

        name: str = f'Inheritance-{self._inheritanceCounter}'

        pyutInheritance: PyutLink = PyutLink(name=name, linkType=PyutLinkType.INHERITANCE)

        pyutInheritance.destination  = baseUmlClass.pyutClass
        pyutInheritance.source       = subUmlClass.pyutClass

        self._inheritanceCounter += 1
        return pyutInheritance

    def _createInterfacePyutLink(self):

        name: str = f'implements'
        pyutInterface: PyutLink = PyutLink(name=name, linkType=PyutLinkType.INTERFACE)

        return pyutInterface

    def _associateClassEventHandler(self, umlClass: UmlClass):

        eventHandler: UmlClassEventHandler = UmlClassEventHandler()

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetShape(umlClass)
        eventHandler.SetPreviousHandler(umlClass.GetEventHandler())

        umlClass.SetEventHandler(eventHandler)

    def _associateNoteLinkEventHandler(self, umlNoteLink: UmlNoteLink):

        eventHandler: UmlNoteLinkEventHandler = UmlNoteLinkEventHandler(umlNoteLink=umlNoteLink)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine

        eventHandler.SetPreviousHandler(umlNoteLink.GetEventHandler())
        umlNoteLink.SetEventHandler(eventHandler)

    def _createUmlNote(self) -> UmlNote:

        pyutNote: PyutNote = PyutNote(content='I am a great note')
        umlNote:  UmlNote  = UmlNote(pyutNote=pyutNote)

        notePosition:  UmlPosition = UmlPosition(x=100, y=100)

        umlNote.size     = UmlDimensions(width=150, height=50)
        umlNote.pyutNote = pyutNote
        umlNote.position = notePosition

        eventHandler: UmlNoteEventHandler = UmlNoteEventHandler()

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetShape(umlNote)
        eventHandler.SetPreviousHandler(umlNote.GetEventHandler())
        umlNote.SetEventHandler(eventHandler)

        return umlNote

    def _displayUmlClass(self, umlClass: UmlClass, umlPosition: UmlPosition):

        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        umlClass.position = umlPosition
        umlClass.umlFrame = self._diagramFrame

        diagram.AddShape(umlClass)
        umlClass.Show(show=True)

        self._diagramFrame.refresh()
