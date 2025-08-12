
from typing import cast

from logging import Logger
from logging import getLogger

import platform

from wx import App

from tests.demo.Versions import Versions
from umlshapes.lib.ogl import OGLInitialize

from codeallybasic.UnitTestBase import UnitTestBase

from umlshapes.preferences.UmlPreferences import UmlPreferences

from tests.demo.DemoAppFrame import DemoAppFrame


class DemoUmlShapes(App):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._preferences:     UmlPreferences = cast(UmlPreferences, None)
        self._wxFrame:         DemoAppFrame   = cast(DemoAppFrame, None)

        # self._demoEventEngine = DemoEventEngine(listeningWindow=self._frame)    # Our app event engine

        super().__init__(redirect=False)    # This calls OnInit()

    def OnInit(self):
        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()
        self._preferences = UmlPreferences()
        self._wxFrame     = DemoAppFrame()

        self.SetTopWindow(self._wxFrame)

        return True


if __name__ == '__main__':

    UnitTestBase.setUpLogging()

    version: Versions = Versions()
    print("Versions: ")
    print(f'Platform: {version.platform}')

    print(f'    System:       {platform.system()}')
    print(f'    Version:      {platform.version()}')
    print(f'    Release:      {platform.release()}')

    print(f'WxPython: {version.wxPythonVersion}')
    print(f'')
    print(f'UML Diagrammer Packages')
    print(f'    Uml Shapes:      {version.umlShapesVersion}')

    print(f'')
    print(f'Python:   {version.pythonVersion}')

    testApp: DemoUmlShapes = DemoUmlShapes()

    testApp.MainLoop()
