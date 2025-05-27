from typing import Union
from typing import cast
from typing import Dict
from typing import NewType
from typing import Tuple

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import NewIdRef as wxNewIdRef

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutLink import PyutLink

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame
from umlshapes.links.UmlAggregation import UmlAggregation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface

from umlshapes.links.UmlLink import UmlLink
from umlshapes.links.UmlAssociation import UmlAssociation

from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import ID_REFERENCE

INITIAL_X:   int = 100
INITIAL_Y:   int = 100

INCREMENT_X: int = 25
INCREMENT_Y: int = 25

LinkEventHandler = Union[UmlAssociationEventHandler, UmlLinkEventHandler]


@dataclass
class AssociationDescription:
    associationClass:   type[UmlLink]          = cast(type[UmlLink], None)
    linkType:           PyutLinkType           = PyutLinkType.ASSOCIATION
    eventHandler:       type[LinkEventHandler] = cast(type[LinkEventHandler], None)
    associationCounter: int = 0
    classCounter:       int = 0


RelationshipDescription = NewType('RelationshipDescription', Dict[ID_REFERENCE, AssociationDescription])


class RelationshipCreator:
    """
    Not those kinds, dork
    """
    def __init__(self, diagramFrame: UmlClassDiagramFrame):

        self._diagramFrame:    UmlClassDiagramFrame = diagramFrame
        self.logger:           Logger               = getLogger(__name__)
        self._preferences:     UmlPreferences       = UmlPreferences()
        self._currentPosition: UmlPosition          = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        self.ID_DISPLAY_UML_ASSOCIATION: ID_REFERENCE = wxNewIdRef()
        self.ID_DISPLAY_UML_INHERITANCE: ID_REFERENCE = wxNewIdRef()
        self.ID_DISPLAY_UML_COMPOSITION: ID_REFERENCE = wxNewIdRef()
        self.ID_DISPLAY_UML_AGGREGATION: ID_REFERENCE = wxNewIdRef()
        self.ID_DISPLAY_UML_INTERFACE:   ID_REFERENCE = wxNewIdRef()

        association: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.ASSOCIATION,
            eventHandler=UmlAssociationEventHandler,
            associationClass=UmlAssociation
        )
        composition: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.COMPOSITION,
            eventHandler=UmlAssociationEventHandler,
            associationClass=UmlComposition
        )
        aggregation: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.AGGREGATION,
            eventHandler=UmlAssociationEventHandler,
            associationClass=UmlAggregation
        )
        inheritance: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.INHERITANCE,
            eventHandler=UmlLinkEventHandler,
            associationClass=UmlInheritance
        )
        interface: AssociationDescription = AssociationDescription(
            linkType=PyutLinkType.INTERFACE,
            eventHandler=UmlLinkEventHandler,
            associationClass=UmlInterface
        )
        self._relationShips: RelationshipDescription = RelationshipDescription(
            {
                self.ID_DISPLAY_UML_ASSOCIATION: association,
                self.ID_DISPLAY_UML_COMPOSITION: composition,
                self.ID_DISPLAY_UML_AGGREGATION: aggregation,
                self.ID_DISPLAY_UML_INHERITANCE: inheritance,
                self.ID_DISPLAY_UML_INTERFACE:   interface
            }
        )

    def displayRelationship(self, idReference: ID_REFERENCE):

        associationDescription: AssociationDescription = self._relationShips[idReference]

        if associationDescription.linkType == PyutLinkType.INHERITANCE:
            self._displayUmlInheritance(associationDescription=associationDescription)
        else:
            self._displayAssociation(associationDescription=associationDescription)

    def _displayAssociation(self, associationDescription: AssociationDescription):
        """

        Args:
            associationDescription:
        """
        sourceUmlClass, destinationUmlClass = self._createClassPair(associationDescription.classCounter)
        associationDescription.classCounter += 2
        self.logger.info(f'{sourceUmlClass.id=} {destinationUmlClass.id=}')

        pyutLink = self._createAssociationPyutLink(associationDescription.associationCounter)

        associationDescription.associationCounter += 1

        umlAssociation = associationDescription.associationClass(pyutLink=pyutLink)

        umlAssociation.SetCanvas(self._diagramFrame)
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceUmlClass.addLink(umlLink=umlAssociation, destinationClass=destinationUmlClass)

        self._diagramFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)

        if isinstance(umlAssociation, UmlAssociation):
            eventHandler = associationDescription.eventHandler(umlAssociation=umlAssociation)   # type: ignore
        else:
            eventHandler = associationDescription.eventHandler(umlLink=umlAssociation)

        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

    def _displayUmlInheritance(self, associationDescription: AssociationDescription):
        """

        Args:
            associationDescription:
        """

        baseUmlClass, subUmlClass = self._createClassPair(associationDescription.classCounter)
        baseUmlClass.pyutClass.name = 'Base Class'
        subUmlClass.pyutClass.name  = 'SubClass'
        associationDescription.classCounter += 2

        pyutInheritance: PyutLink = self._createInheritancePyutLink(inheritanceCounter=associationDescription.associationCounter, baseUmlClass=baseUmlClass, subUmlClass=subUmlClass)
        associationDescription.associationCounter += 1

        umlInheritance: UmlInheritance = UmlInheritance(pyutLink=pyutInheritance, baseClass=baseUmlClass, subClass=subUmlClass)
        umlInheritance.SetCanvas(self._diagramFrame)
        umlInheritance.MakeLineControlPoints(n=2)       # Make this configurable

        # REMEMBER:   from subclass to base class
        subUmlClass.addLink(umlLink=umlInheritance, destinationClass=baseUmlClass)

        self._diagramFrame.umlDiagram.AddShape(umlInheritance)
        umlInheritance.Show(True)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInheritance)
        eventHandler.SetPreviousHandler(umlInheritance.GetEventHandler())
        umlInheritance.SetEventHandler(eventHandler)

    def _createClassPair(self, classCounter: int) -> Tuple[UmlClass, UmlClass]:

        sourcePosition:       UmlPosition = UmlPosition(x=100, y=100)       # fix this should be input
        destinationPosition:  UmlPosition = UmlPosition(x=200, y=300)

        sourcePyutClass:      PyutClass   = self._createSimplePyutClass(classCounter=classCounter)
        classCounter += 1
        destinationPyutClass: PyutClass   = self._createSimplePyutClass(classCounter=classCounter)
        classCounter += 1

        sourceUmlClass:      UmlClass = UmlClass(pyutClass=sourcePyutClass)
        destinationUmlClass: UmlClass = UmlClass(pyutClass=destinationPyutClass)

        self._displayUmlClass(umlClass=sourceUmlClass,      umlPosition=sourcePosition)
        self._displayUmlClass(umlClass=destinationUmlClass, umlPosition=destinationPosition)

        self._associateClassEventHandler(umlClass=sourceUmlClass)
        self._associateClassEventHandler(umlClass=destinationUmlClass)

        return sourceUmlClass, destinationUmlClass

    def _createSimplePyutClass(self, classCounter: int) -> PyutClass:

        className: str = f'{self._preferences.defaultClassName} {classCounter}'
        classCounter += 1
        pyutClass: PyutClass  = PyutClass(name=className)

        return pyutClass

    def _createAssociationPyutLink(self, associationCounter: int) -> PyutLink:

        name: str = f'{self._preferences.defaultAssociationName} {associationCounter}'

        pyutLink: PyutLink = PyutLink(name=name, linkType=PyutLinkType.ASSOCIATION)

        pyutLink.sourceCardinality      = 'src Card'
        pyutLink.destinationCardinality = 'dst Card'

        return pyutLink

    def _createInheritancePyutLink(self, inheritanceCounter: int, baseUmlClass: UmlClass, subUmlClass: UmlClass) -> PyutLink:

        name: str = f'Inheritance {inheritanceCounter}'

        pyutInheritance: PyutLink = PyutLink(name=name, linkType=PyutLinkType.INHERITANCE)

        pyutInheritance.destination  = baseUmlClass.pyutClass
        pyutInheritance.source       = subUmlClass.pyutClass

        return pyutInheritance

    def _associateClassEventHandler(self, umlClass: UmlClass):

        eventHandler: UmlClassEventHandler = UmlClassEventHandler()
        eventHandler.SetShape(umlClass)
        eventHandler.SetPreviousHandler(umlClass.GetEventHandler())

        umlClass.SetEventHandler(eventHandler)

    def _displayUmlClass(self, umlClass: UmlClass, umlPosition: UmlPosition):

        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        umlClass.position = umlPosition
        umlClass.SetCanvas(self._diagramFrame)

        diagram.AddShape(umlClass)
        umlClass.Show(show=True)

        self._diagramFrame.refresh()
