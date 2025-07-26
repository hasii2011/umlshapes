
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

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
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

from tests.demo.DemoCommon import Identifiers
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


RelationshipDescription = NewType('RelationshipDescription', Dict[ID_REFERENCE, AssociationDescription])


class RelationshipCreator:
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
                Identifiers.ID_DISPLAY_UML_ASSOCIATION: association,
                Identifiers.ID_DISPLAY_UML_COMPOSITION: composition,
                Identifiers.ID_DISPLAY_UML_AGGREGATION: aggregation,
                Identifiers.ID_DISPLAY_UML_INHERITANCE: inheritance,
                Identifiers.ID_DISPLAY_UML_INTERFACE:   interface
            }
        )

    def displayRelationship(self, idReference: ID_REFERENCE):

        associationDescription: AssociationDescription = self._relationShips[idReference]

        if associationDescription.linkType == PyutLinkType.INHERITANCE:
            self._displayUmlInheritance()
        elif associationDescription.linkType == PyutLinkType.INTERFACE:
            self._displayUmlInterface()
        else:
            self._displayAssociation(associationDescription=associationDescription)

    def _displayAssociation(self, associationDescription: AssociationDescription):
        """

        Args:
            associationDescription:
        """
        sourceUmlClass, destinationUmlClass = self._createClassPair()
        self.logger.info(f'{sourceUmlClass.id=} {destinationUmlClass.id=}')

        pyutLink = self._createAssociationPyutLink()

        pyutLink.name = f'{associationDescription.linkType}-{self._associationCounter}'
        self._associationCounter += 1

        umlAssociation = associationDescription.associationClass(pyutLink=pyutLink)

        umlAssociation.umlFrame = self._diagramFrame
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceUmlClass.addLink(umlLink=umlAssociation, destinationClass=destinationUmlClass)

        self._diagramFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)

        if isinstance(umlAssociation, UmlAssociation):
            eventHandler = associationDescription.eventHandler(umlAssociation=umlAssociation)   # type: ignore
        else:
            eventHandler = associationDescription.eventHandler(umlLink=umlAssociation)

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

    def _displayUmlInheritance(self):
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

    def _displayUmlInterface(self):

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

    def _createClassPair(self) -> Tuple[UmlClass, UmlClass]:

        sourcePosition:       UmlPosition = UmlPosition(x=100, y=100)       # fix this should be input
        destinationPosition:  UmlPosition = UmlPosition(x=200, y=300)

        sourcePyutClass:      PyutClass   = self._createSimplePyutClass(classCounter=self._classCounter)
        self._classCounter += 1
        destinationPyutClass: PyutClass   = self._createSimplePyutClass(classCounter=self._classCounter)
        self._classCounter += 1

        sourceUmlClass:      UmlClass = UmlClass(pyutClass=sourcePyutClass)
        destinationUmlClass: UmlClass = UmlClass(pyutClass=destinationPyutClass)

        self._displayUmlClass(umlClass=sourceUmlClass,      umlPosition=sourcePosition)
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
        eventHandler.SetShape(umlClass)
        eventHandler.SetPreviousHandler(umlClass.GetEventHandler())

        umlClass.SetEventHandler(eventHandler)

    def _displayUmlClass(self, umlClass: UmlClass, umlPosition: UmlPosition):

        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        umlClass.position = umlPosition
        umlClass.umlFrame = self._diagramFrame

        diagram.AddShape(umlClass)
        umlClass.Show(show=True)

        self._diagramFrame.refresh()
