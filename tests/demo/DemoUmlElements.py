
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

from pyutmodelv2.PyutText import PyutText

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlTextEventHandler import UmlTextEventHandler

FRAME_WIDTH:  int = 800
FRAME_HEIGHT: int = 600

INITIAL_X:   int = 50
INITIAL_Y:   int = 50

INCREMENT_X: int = INITIAL_X + 10
INCREMENT_Y: int = INITIAL_Y + 10


class DemoUmlElements(App):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        super().__init__(redirect=False)

        self._currentPosition: UmlPosition = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()
        self._ID_DISPLAY_UML_TEXT:  int = wxNewIdRef()
        self._textCounter:          int = 0

        self._preferences: UmlPreferences = UmlPreferences()
        self._frame:       SizedFrame     = SizedFrame(parent=None, title="Test UML Elements", size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        # self._demoEventEngine = DemoEventEngine(listeningWindow=self._frame)    # Our app event engine

        sizedPanel: SizedPanel = self._frame.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)
        # self._diagramFrame = DemoUmlFrame(parent=sizedPanel, demoEventEngine=self._demoEventEngine)
        self._diagramFrame = UmlFrame(parent=sizedPanel)
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()
        self.SetTopWindow(self._frame)

        self._frame.CreateStatusBar()  # should always do this when there's a resize border
        self._frame.SetAutoLayout(True)
        self._frame.Show(True)

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

        # viewMenu.Append(id=self._ID_DISPLAY_SEQUENCE_DIAGRAM,    item='Sequence Diagram', helpString='Display Sequence Diagram')
        # viewMenu.Append(id=self._ID_DISPLAY_OGL_CLASS,           item='Ogl Class',        helpString='Display an Ogl Class')
        viewMenu.Append(id=self._ID_DISPLAY_UML_TEXT, item='Uml Text', helpString='Display Uml Text')
        # viewMenu.Append(id=self._ID_DISPLAY_OGL_COMPOSITION,     item='Ogl Composition',  helpString='Display an Composition Link')
        # viewMenu.Append(id=self._ID_DISPLAY_OGL_INTERFACE,       item='Ogl Interface',    helpString='Display Lollipop Interface')
        # viewMenu.Append(id=self._ID_DISPLAY_OGL_USE_CASE,        item='Ogl Use Case',     helpString='Display Ogl Use Case')
        # viewMenu.Append(id=self._ID_DISPLAY_OGL_ACTOR,           item='Ogl Actor',        helpString='Display Ogl Actor')

        viewMenu.AppendSeparator()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(viewMenu, 'View')

        self._frame.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)

        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_SEQUENCE_DIAGRAM)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_OGL_CLASS)
        self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_UML_TEXT)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_OGL_COMPOSITION)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_OGL_INTERFACE)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_OGL_USE_CASE)
        # self.Bind(EVT_MENU, self._onDisplayElement, id=self._ID_DISPLAY_OGL_ACTOR)

    def _onDisplayElement(self, event: CommandEvent):
        menuId: int = event.GetId()
        match menuId:
            # case self._ID_DISPLAY_SEQUENCE_DIAGRAM:
            #     self._displaySequenceDiagram()
            # case self._ID_DISPLAY_OGL_CLASS:
            #     self._displayOglClass()
            case self._ID_DISPLAY_UML_TEXT:
                self._displayOglText()
            # case self._ID_DISPLAY_OGL_COMPOSITION:
            #     self._displayOglComposition()
            # case self._ID_DISPLAY_OGL_INTERFACE:
            #     self._displayOglInterface()
            # case self._ID_DISPLAY_OGL_USE_CASE:
            #     self._displayOglUseCase()
            # case self._ID_DISPLAY_OGL_ACTOR:
            #     self._displayOglActor()
            case _:
                self.logger.error(f'WTH!  I am not handling that menu item')

    def _displayOglText(self):

        content:        str           = f'{self._preferences.textValue} {self._textCounter}'
        self._textCounter += 1
        pyutText:       PyutText      = PyutText(content=content)
        textDimensions: UmlDimensions = self._preferences.textDimensions
        umlPosition:    UmlPosition   = self._computePosition()

        umlText:  UmlText  = UmlText(pyutText=pyutText, width=textDimensions.width, height=textDimensions.height)

        umlText.SetCanvas(self._diagramFrame)
        umlText.SetX(x=umlPosition.x)
        umlText.SetY(y=umlPosition.y)

        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        diagram.AddShape(umlText)
        umlText.Show(show=True)

        eventHandler: UmlTextEventHandler = UmlTextEventHandler(moveColor=umlText.moveColor)
        eventHandler.SetShape(umlText)
        eventHandler.SetPreviousHandler(umlText.GetEventHandler())

        umlText.SetEventHandler(eventHandler)

        self._diagramFrame.refresh()

    def _computePosition(self) -> UmlPosition:

        self._currentPosition.x += INCREMENT_X
        self._currentPosition.y += INCREMENT_Y

        return UmlPosition(
            x=self._currentPosition.x,
            y=self._currentPosition.y
        )


if __name__ == '__main__':

    UnitTestBase.setUpLogging()

    testApp: DemoUmlElements = DemoUmlElements()

    testApp.MainLoop()
