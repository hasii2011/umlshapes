
from logging import Logger
from logging import getLogger
from typing import cast

from wx import EVT_MENU
from wx import ID_EXIT
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT

from wx import App
from wx import Menu
from wx import MenuBar
from wx import CommandEvent

from wx.lib.ogl import OGLInitialize

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from tests.demo.DemoCommon import Identifiers

from tests.demo.ShapeCreator import ShapeCreator
from tests.demo.RelationshipCreator import RelationshipCreator

from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame

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

        self._currentPosition: UmlPosition    = cast(UmlPosition, None)
        self._preferences:     UmlPreferences = cast(UmlPreferences, None)
        self._wxFrame:         SizedFrame     = cast(SizedFrame, None)
        self._diagramFrame:    UmlClassDiagramFrame = cast(UmlClassDiagramFrame, None)

        # self._demoEventEngine = DemoEventEngine(listeningWindow=self._frame)    # Our app event engine

        self._shapeCreator:        ShapeCreator        = cast(ShapeCreator, None)
        self._relationshipCreator: RelationshipCreator = cast(RelationshipCreator, None)

        super().__init__(redirect=False)    # This calls OnInit()

    def OnInit(self):
        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()
        self._currentPosition = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        self._preferences = UmlPreferences()
        self._wxFrame     = SizedFrame(
            parent=None,
            title="Test UML Shapes",
            size=(FRAME_WIDTH, FRAME_HEIGHT),
            style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        )

        sizedPanel: SizedPanel = self._wxFrame.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        self._diagramFrame = UmlClassDiagramFrame(parent=sizedPanel)
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()
        self.SetTopWindow(self._wxFrame)

        self._wxFrame.CreateStatusBar()  # should always do this when there's a resize border
        self._wxFrame.SetAutoLayout(True)
        self._wxFrame.Show(True)

        self._shapeCreator        = ShapeCreator(diagramFrame=self._diagramFrame)
        self._relationshipCreator = RelationshipCreator(diagramFrame=self._diagramFrame)

        return True

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = Menu()
        viewMenu: Menu    = Menu()

        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")
        fileMenu.AppendSeparator()
        # fileMenu.Append(ID_PREFERENCES, "P&references", "Ogl preferences")

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

        self._wxFrame.SetMenuBar(menuBar)

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
                self._wxFrame.SetStatusText('See the shape !!')
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


if __name__ == '__main__':

    UnitTestBase.setUpLogging()

    testApp: DemoUmlShapes = DemoUmlShapes()

    testApp.MainLoop()
