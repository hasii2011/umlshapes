
from logging import Logger
from logging import getLogger

from wx import DEFAULT_FRAME_STYLE
from wx import EVT_MENU
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_EXIT

from wx import Menu
from wx import MenuBar
from wx import CommandEvent
from wx import OK

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces
from pyutmodelv2.PyutModelTypes import ClassName

from umlshapes.IApplicationAdapter import IApplicationAdapter
from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.UmlUtils import UmlUtils
from umlshapes.dialogs.DlgEditInterface import DlgEditInterface
from umlshapes.eventengine.UmlEventEngine import UmlEventEngine
from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
from umlshapes.links.eventhandlers.UmlLollipopInterfaceEventHandler import UmlLollipopInterfaceEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.Common import AttachmentSide
from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import Identifiers
from tests.demo.RelationshipCreator import RelationshipCreator
from tests.demo.ShapeCreator import ShapeCreator
from tests.demo.DemoApplicationAdapter import DemoApplicationAdapter

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720


class DemoAppFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=None, title='Test UML Shapes', size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        self._applicationAdapter: IApplicationAdapter = DemoApplicationAdapter(frame=self)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        self._diagramFrame = UmlClassDiagramFrame(
            parent=sizedPanel,
            applicationAdapter=self._applicationAdapter,
            createLollipopCallback=self._createLollipopInterface
        )
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()

        self.CreateStatusBar()  # should always do this when there's a resize border
        self.SetAutoLayout(True)
        self.Show(True)

        self._shapeCreator:        ShapeCreator        = ShapeCreator(diagramFrame=self._diagramFrame)
        self._relationshipCreator: RelationshipCreator = RelationshipCreator(diagramFrame=self._diagramFrame)
        self._preferences:         UmlPreferences      = UmlPreferences()

        self._pyutInterfaceCount: int = 0

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = Menu()
        viewMenu: Menu    = Menu()

        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")
        fileMenu.AppendSeparator()
        # fileMenu.Append(ID_PREFERENCES, "P&references", "Uml preferences")

        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_INTERFACE,   item='UML Interface',   helpString='Display Normal Interface')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_AGGREGATION, item='UML Aggregation', helpString='Display a aggregation Link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_COMPOSITION, item='UML Composition', helpString='Display a composition Link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_INHERITANCE, item='UML Inheritance', helpString='Display an Inheritance Link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_ASSOCIATION, item='Uml Association', helpString='Display Bare Association')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_CLASS,       item='Uml Class',          helpString='Display an Uml Class')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_TEXT,        item='Uml Text',           helpString='Display Uml Text')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_NOTE,        item='Uml Note',           helpString='Display Uml Note')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_USE_CASE,    item='Uml Use Case',       helpString='Display Uml Use Case')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_ACTOR,       item='Uml Actor',          helpString='Display Uml Actor')
        # viewMenu.Append(id=self._ID_DISPLAY_SEQUENCE_DIAGRAM,    item='Sequence Diagram', helpString='Display Sequence Diagram')
        viewMenu.AppendSeparator()

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(viewMenu, 'View')

        self.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)

        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_TEXT)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_NOTE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_USE_CASE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_ACTOR)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_CLASS)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_ASSOCIATION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_INHERITANCE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_COMPOSITION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_AGGREGATION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_INTERFACE)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_SEQUENCE_DIAGRAM)

    def _onDisplayElement(self, event: CommandEvent):

        menuId:              int                 = event.GetId()
        shapeCreator:        ShapeCreator        = self._shapeCreator
        relationshipCreator: RelationshipCreator = self._relationshipCreator

        # noinspection PyUnreachableCode
        match menuId:
            case Identifiers.ID_DISPLAY_UML_CLASS:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_CLASS)
                self.SetStatusText('See the shape !!')
            case Identifiers.ID_DISPLAY_UML_TEXT:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_TEXT)
            case Identifiers.ID_DISPLAY_UML_NOTE:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_NOTE)
            case Identifiers.ID_DISPLAY_UML_USE_CASE:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_USE_CASE)
            case Identifiers.ID_DISPLAY_UML_ACTOR:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_ACTOR)

            case Identifiers.ID_DISPLAY_UML_ASSOCIATION:
                relationshipCreator.displayRelationship(idReference=Identifiers.ID_DISPLAY_UML_ASSOCIATION)
            case Identifiers.ID_DISPLAY_UML_COMPOSITION:
                relationshipCreator.displayRelationship(idReference=Identifiers.ID_DISPLAY_UML_COMPOSITION)
            case Identifiers.ID_DISPLAY_UML_AGGREGATION:
                relationshipCreator.displayRelationship(idReference=Identifiers.ID_DISPLAY_UML_AGGREGATION)

            case Identifiers.ID_DISPLAY_UML_INHERITANCE:
                relationshipCreator.displayRelationship(idReference=Identifiers.ID_DISPLAY_UML_INHERITANCE)
            case Identifiers.ID_DISPLAY_UML_INTERFACE:
                relationshipCreator.displayRelationship(idReference=Identifiers.ID_DISPLAY_UML_INTERFACE)
            # case self._ID_DISPLAY_SEQUENCE_DIAGRAM:
            #     self._displaySequenceDiagram()
            case _:
                self.logger.error(f'WTH!  I am not handling that menu item')

    def _createLollipopInterface(self, requestingUmlClass: UmlClass, perimeterPoint: UmlPosition):
        """

        Args:
            requestingUmlClass:
            perimeterPoint:
        """

        interfaceName: str = f'{self._preferences.defaultNameInterface}{self._pyutInterfaceCount}'
        self._pyutInterfaceCount += 1

        pyutInterface:        PyutInterface        = PyutInterface(interfaceName)
        pyutInterface.addImplementor(ClassName(requestingUmlClass.pyutClass.name))

        umlLollipopInterface: UmlLollipopInterface = UmlLollipopInterface(pyutInterface=pyutInterface)
        umlLollipopInterface.attachedTo            = requestingUmlClass

        attachmentSide: AttachmentSide      = UmlUtils.attachmentSide(x=perimeterPoint.x, y=perimeterPoint.y, rectangle=requestingUmlClass.rectangle)
        umlLollipopInterface.attachmentSide = attachmentSide
        umlLollipopInterface.lineCentum     = UmlUtils.computeLineCentum(attachmentSide=attachmentSide, umlPosition=perimeterPoint, rectangle=requestingUmlClass.rectangle)

        self.logger.debug(f'{umlLollipopInterface.attachmentSide=} {umlLollipopInterface.lineCentum=}')

        umlLollipopInterface.SetCanvas(self)
        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        diagram.AddShape(umlLollipopInterface)
        umlLollipopInterface.Show(show=True)
        self.logger.info(f'UmlInterface added: {umlLollipopInterface}')

        eventHandler: UmlLollipopInterfaceEventHandler = UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)
        eventHandler.SetPreviousHandler(umlLollipopInterface.GetEventHandler())
        umlLollipopInterface.SetEventHandler(eventHandler)

        umlFrame:       UmlClassDiagramFrame = self._diagramFrame
        eventEngine:    UmlEventEngine       = umlFrame.eventEngine
        pyutInterfaces: PyutInterfaces       = eventHandler.getLollipopInterfaces()

        with DlgEditInterface(parent=umlFrame, oglInterface2=umlLollipopInterface, eventEngine=eventEngine, pyutInterfaces=pyutInterfaces) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()
