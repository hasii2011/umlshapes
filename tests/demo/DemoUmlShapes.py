
from typing import Tuple

from logging import Logger
from logging import getLogger

from wx import EVT_MENU
from wx import ID_EXIT
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT

from wx import App
from wx import Menu
from wx import MenuBar
from wx import CommandEvent

from wx import NewIdRef as wxNewIdRef

from wx.lib.ogl import OGLInitialize

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutLink import PyutLink

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from tests.demo.ShapeCreator import ShapeCreator
from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame
from umlshapes.links.UmlAggregation import UmlAggregation

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlComposition import UmlComposition
from umlshapes.links.UmlInheritance import UmlInheritance
from umlshapes.links.UmlInterface import UmlInterface

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler

from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler

from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.preferences.UmlPreferences import UmlPreferences


FRAME_WIDTH:  int = 800
FRAME_HEIGHT: int = 600

INITIAL_X:   int = 100
INITIAL_Y:   int = 100

INCREMENT_X: int = 25
INCREMENT_Y: int = 25


class DemoUmlShapes(App):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        super().__init__(redirect=False)

        self._currentPosition: UmlPosition = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()
        self._ID_DISPLAY_UML_TEXT:        int = wxNewIdRef()
        self._ID_DISPLAY_UML_NOTE:        int = wxNewIdRef()
        self._ID_DISPLAY_UML_USE_CASE:    int = wxNewIdRef()
        self._ID_DISPLAY_UML_ACTOR:       int = wxNewIdRef()
        self._ID_DISPLAY_UML_CLASS:       int = wxNewIdRef()
        self._ID_DISPLAY_UML_ASSOCIATION: int = wxNewIdRef()
        self._ID_DISPLAY_UML_INHERITANCE: int = wxNewIdRef()
        self._ID_DISPLAY_UML_COMPOSITION: int = wxNewIdRef()
        self._ID_DISPLAY_UML_AGGREGATION: int = wxNewIdRef()
        self._ID_DISPLAY_UML_INTERFACE:   int = wxNewIdRef()

        self._textCounter:        int = 0
        self._noteCounter:        int = 0
        self._useCaseCounter:     int = 0
        self._actorCounter:       int = 0
        self._classCounter:       int = 0
        self._associationCounter: int = 0
        self._inheritanceCounter: int = 0
        self._compositionCounter: int = 0
        self._interfaceCounter:   int = 0

        self._preferences: UmlPreferences = UmlPreferences()
        self._frame:       SizedFrame     = SizedFrame(
            parent=None,
            title="Test UML Shapes",
            size=(FRAME_WIDTH, FRAME_HEIGHT),
            style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        )

        # self._demoEventEngine = DemoEventEngine(listeningWindow=self._frame)    # Our app event engine

        sizedPanel: SizedPanel = self._frame.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        self._diagramFrame = UmlClassDiagramFrame(parent=sizedPanel)
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()
        self.SetTopWindow(self._frame)

        self._frame.CreateStatusBar()  # should always do this when there's a resize border
        self._frame.SetAutoLayout(True)
        self._frame.Show(True)

        self._shapeCreator: ShapeCreator = ShapeCreator(diagramFrame=self._diagramFrame)

    def OnInit(self):
        return True

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = Menu()
        viewMenu: Menu    = Menu()

        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")
        fileMenu.AppendSeparator()
        # fileMenu.Append(ID_PREFERENCES, "P&references", "Ogl preferences")

        viewMenu.Append(id=self._ID_DISPLAY_UML_INTERFACE,   item='UML Interface',   helpString='Display Normal Interface')
        viewMenu.Append(id=self._ID_DISPLAY_UML_AGGREGATION, item='UML Aggregation', helpString='Display a aggregation Link')
        viewMenu.Append(id=self._ID_DISPLAY_UML_COMPOSITION, item='UML Composition', helpString='Display a composition Link')
        viewMenu.Append(id=self._ID_DISPLAY_UML_INHERITANCE, item='UML Inheritance', helpString='Display an Inheritance Link')
        viewMenu.Append(id=self._ID_DISPLAY_UML_ASSOCIATION, item='Uml Association', helpString='Display Bare Association')
        viewMenu.Append(id=self._ID_DISPLAY_UML_CLASS,       item='Uml Class',          helpString='Display an Uml Class')
        viewMenu.Append(id=self._ID_DISPLAY_UML_TEXT,        item='Uml Text',           helpString='Display Uml Text')
        viewMenu.Append(id=self._ID_DISPLAY_UML_NOTE,        item='Uml Note',           helpString='Display Uml Note')
        viewMenu.Append(id=self._ID_DISPLAY_UML_USE_CASE,    item='Uml Use Case',       helpString='Display Uml Use Case')
        viewMenu.Append(id=self._ID_DISPLAY_UML_ACTOR,       item='Uml Actor',          helpString='Display Uml Actor')
        # viewMenu.Append(id=self._ID_DISPLAY_SEQUENCE_DIAGRAM,    item='Sequence Diagram', helpString='Display Sequence Diagram')
        viewMenu.AppendSeparator()

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(viewMenu, 'View')

        self._frame.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)

        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_TEXT)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_NOTE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_USE_CASE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_ACTOR)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_CLASS)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_ASSOCIATION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_INHERITANCE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_COMPOSITION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_AGGREGATION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_INTERFACE)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_SEQUENCE_DIAGRAM)

    def _onDisplayElement(self, event: CommandEvent):

        menuId:       int          = event.GetId()
        shapeCreator: ShapeCreator = self._shapeCreator

        # noinspection PyUnreachableCode
        match menuId:
            case self._ID_DISPLAY_UML_CLASS:
                shapeCreator.displayShape(self._shapeCreator.ID_DISPLAY_UML_CLASS)
            case self._ID_DISPLAY_UML_TEXT:
                shapeCreator.displayShape(self._shapeCreator.ID_DISPLAY_UML_TEXT)
            case self._ID_DISPLAY_UML_NOTE:
                shapeCreator.displayShape(self._shapeCreator.ID_DISPLAY_UML_NOTE)
            case self._ID_DISPLAY_UML_USE_CASE:
                shapeCreator.displayShape(self._shapeCreator.ID_DISPLAY_UML_USE_CASE)
            case self._ID_DISPLAY_UML_ACTOR:
                shapeCreator.displayShape(self._shapeCreator.ID_DISPLAY_UML_ACTOR)
            case self._ID_DISPLAY_UML_ASSOCIATION:
                self._displayBareAssociation()
            case self._ID_DISPLAY_UML_INHERITANCE:
                self._displayUmlInheritance()
            case self._ID_DISPLAY_UML_COMPOSITION:
                self._displayUmlComposition()
            case self._ID_DISPLAY_UML_AGGREGATION:
                self._displayUmlAggregation()
            case self._ID_DISPLAY_UML_INTERFACE:
                self._displayUmlInterface()
            # case self._ID_DISPLAY_SEQUENCE_DIAGRAM:
            #     self._displaySequenceDiagram()
            case _:
                self.logger.error(f'WTH!  I am not handling that menu item')

    def _displayBareAssociation(self):

        sourceUmlClass, destinationUmlClass = self._createClassPair()

        self.logger.info(f'{sourceUmlClass.id=} {destinationUmlClass.id=}')

        umlAssociation: UmlAssociation = UmlAssociation(pyutLink=self._createAssociationPyutLink())
        umlAssociation.SetCanvas(self._diagramFrame)
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceUmlClass.addLink(umlLink=umlAssociation, destinationClass=destinationUmlClass)
        self._diagramFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)

        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation)
        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

        self.logger.info(f'controlPoints: {umlAssociation.GetLineControlPoints()}')

    def _displayUmlComposition(self):

        composerUmlClass, composedUmlClass = self._createClassPair()

        composerUmlClass.pyutClass.name = 'Hospital'
        composedUmlClass.pyutClass.name = 'Department'

        self.logger.info(f'{composerUmlClass.id=} {composedUmlClass.id=}')

        pyutLink: PyutLink = self._createAssociationPyutLink()
        pyutLink.linkType               = PyutLinkType.COMPOSITION
        pyutLink.name                   = ''
        pyutLink.sourceCardinality      = '1'
        pyutLink.destinationCardinality = '1..*'

        umlComposition: UmlComposition = UmlComposition(pyutLink=pyutLink)
        umlComposition.SetCanvas(self._diagramFrame)
        umlComposition.MakeLineControlPoints(n=2)       # Make this configurable

        composerUmlClass.addLink(umlLink=umlComposition, destinationClass=composedUmlClass)
        self._diagramFrame.umlDiagram.AddShape(umlComposition)
        umlComposition.Show(True)

        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlComposition)
        eventHandler.SetPreviousHandler(umlComposition.GetEventHandler())
        umlComposition.SetEventHandler(eventHandler)

    def _displayUmlAggregation(self):

        aggregatorUmlClass, aggregatedUmlClass = self._createClassPair()

        aggregatorUmlClass.pyutClass.name = 'Triangle'
        aggregatedUmlClass.pyutClass.name = 'Segment'

        self.logger.info(f'{aggregatorUmlClass.id=} {aggregatedUmlClass.id=}')

        pyutLink: PyutLink = self._createAssociationPyutLink()
        pyutLink.linkType               = PyutLinkType.AGGREGATION
        pyutLink.name                   = '+sides'
        pyutLink.sourceCardinality      = '*'
        pyutLink.destinationCardinality = '3'

        umlAggregation: UmlAggregation = UmlAggregation(pyutLink=pyutLink)
        umlAggregation.SetCanvas(self._diagramFrame)
        umlAggregation.MakeLineControlPoints(n=2)       # Make this configurable

        aggregatorUmlClass.addLink(umlLink=umlAggregation, destinationClass=aggregatedUmlClass)

        self._diagramFrame.umlDiagram.AddShape(umlAggregation)
        umlAggregation.Show(True)

        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAggregation)
        eventHandler.SetPreviousHandler(umlAggregation.GetEventHandler())
        umlAggregation.SetEventHandler(eventHandler)

    def _displayUmlInheritance(self):

        baseUmlClass, subUmlClass = self._createClassPair()
        baseUmlClass.pyutClass.name = 'Base Class'
        subUmlClass.pyutClass.name  = 'SubClass'

        pyutInheritance: PyutLink = self._createInheritancePyutLink()

        pyutInheritance.destination  = baseUmlClass.pyutClass
        pyutInheritance.source       = subUmlClass.pyutClass

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

    def _displayUmlInterface(self):

        interfaceClass, implementingClass = self._createClassPair()

        interfaceClass.pyutClass.name     = 'Interface Class'
        implementingClass.pyutClass.name  = 'Implementing Class'

        pyutInterface: PyutLink = self._createInterfacePyutLink()

        pyutInterface.destination  = implementingClass.pyutClass
        pyutInterface.source       = interfaceClass.pyutClass

        umlInterface: UmlInterface = UmlInterface(pyutLink=pyutInterface, interfaceClass=interfaceClass, implementingClass=implementingClass)
        umlInterface.SetCanvas(self._diagramFrame)
        umlInterface.MakeLineControlPoints(n=2)

        implementingClass.addLink(umlLink=umlInterface, destinationClass=interfaceClass)

        self._diagramFrame.umlDiagram.AddShape(umlInterface)
        umlInterface.Show(True)

        eventHandler: UmlLinkEventHandler = UmlLinkEventHandler(umlLink=umlInterface)
        eventHandler.SetPreviousHandler(umlInterface.GetEventHandler())
        umlInterface.SetEventHandler(eventHandler)

    def _displayShape(self, umlShape: UmlShape, umlPosition: UmlPosition):

        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        umlShape.position = umlPosition
        umlShape.SetCanvas(self._diagramFrame)

        diagram.AddShape(umlShape)
        umlShape.Show(show=True)

        self._diagramFrame.refresh()

    def _computePosition(self) -> UmlPosition:

        currentPosition: UmlPosition = UmlPosition(x=self._currentPosition.x, y=self._currentPosition.y)

        self._currentPosition.x += INCREMENT_X
        self._currentPosition.y += INCREMENT_Y

        return currentPosition

    def _createAssociationPyutLink(self) -> PyutLink:

        name: str = f'{self._preferences.defaultAssociationName} {self._associationCounter}'
        self._associationCounter += 1

        pyutLink: PyutLink = PyutLink(name=name, linkType=PyutLinkType.ASSOCIATION)

        pyutLink.sourceCardinality      = 'src Card'
        pyutLink.destinationCardinality = 'dst Card'

        return pyutLink

    def _createInheritancePyutLink(self) -> PyutLink:

        name: str = f'Inheritance {self._inheritanceCounter}'
        self._inheritanceCounter += 1

        pyutInheritance: PyutLink = PyutLink(name=name, linkType=PyutLinkType.INHERITANCE)

        return pyutInheritance

    def _createInterfacePyutLink(self):

        name: str = f'implements'
        self._interfaceCounter += 1

        pyutInterface: PyutLink = PyutLink(name=name, linkType=PyutLinkType.INTERFACE)

        return pyutInterface

    def _createClassPair(self) -> Tuple[UmlClass, UmlClass]:

        sourcePosition:       UmlPosition = UmlPosition(x=100, y=100)
        destinationPosition:  UmlPosition = UmlPosition(x=200, y=300)

        sourcePyutClass:      PyutClass   = self._createSimplePyutClass()
        destinationPyutClass: PyutClass   = self._createSimplePyutClass()

        sourceUmlClass:      UmlClass = UmlClass(pyutClass=sourcePyutClass)
        destinationUmlClass: UmlClass = UmlClass(pyutClass=destinationPyutClass)

        self._displayShape(umlShape=sourceUmlClass, umlPosition=sourcePosition)
        self._displayShape(umlShape=destinationUmlClass, umlPosition=destinationPosition)

        self._associateClassEventHandler(umlClass=sourceUmlClass)
        self._associateClassEventHandler(umlClass=destinationUmlClass)

        return sourceUmlClass, destinationUmlClass

    def _createSimplePyutClass(self) -> PyutClass:

        className: str = f'{self._preferences.defaultClassName} {self._classCounter}'
        self._classCounter += 1
        pyutClass: PyutClass  = PyutClass(name=className)

        return pyutClass

    def _associateClassEventHandler(self, umlClass: UmlClass):

        eventHandler: UmlClassEventHandler = UmlClassEventHandler()
        eventHandler.SetShape(umlClass)
        eventHandler.SetPreviousHandler(umlClass.GetEventHandler())

        umlClass.SetEventHandler(eventHandler)


if __name__ == '__main__':

    UnitTestBase.setUpLogging()

    testApp: DemoUmlShapes = DemoUmlShapes()

    testApp.MainLoop()
