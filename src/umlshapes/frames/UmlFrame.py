
from typing import cast

from logging import Logger
from logging import getLogger

from collections.abc import Iterable

from wx import Window
from wx.lib.ogl import Shape

from umlshapes.DiagramFrame import DiagramFrame
from umlshapes.UmlDiagram import UmlDiagram

DEFAULT_WIDTH: int   = 3000
A4_FACTOR:     float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20


class UmlFrame(DiagramFrame):
    # def __init__(self, parent: Window, demoEventEngine: DemoEventEngine):
    def __init__(self, parent: Window):

        self.logger: Logger          = getLogger(__name__)
        # self._demoEventEngine: DemoEventEngine = demoEventEngine

        super().__init__(parent=parent)

        self.maxWidth:  int  = DEFAULT_WIDTH
        self.maxHeight: int = int(self.maxWidth / A4_FACTOR)  # 1.41 is for A4 support

        nbrUnitsX: int = int(self.maxWidth / PIXELS_PER_UNIT_X)
        nbrUnitsY: int = int(self.maxHeight / PIXELS_PER_UNIT_Y)
        initPosX:  int = 0
        initPosY:  int = 0
        self.SetScrollbars(PIXELS_PER_UNIT_X, PIXELS_PER_UNIT_Y, nbrUnitsX, nbrUnitsY, initPosX, initPosY, False)

        self.setInfinite(True)

        # self._oglEventEngine.registerListener(event=EVT_REQUEST_LOLLIPOP_LOCATION, callback=self._onRequestLollipopLocation)
        # self._oglEventEngine.registerListener(event=EVT_CREATE_LOLLIPOP_INTERFACE, callback=self._onCreateLollipopInterface)
        # self._oglEventEngine.registerListener(event=EVT_DIAGRAM_FRAME_MODIFIED,    callback=self._onDiagramModified)
        # self._oglEventEngine.registerListener(event=EVT_CUT_OGL_CLASS,             callback=self._onCutClass)

    def OnLeftClick(self, x, y, keys=0):
        """
        Maybe this belongs in DiagramFrame
        Args:
            x:
            y:
            keys:

        Returns:

        """
        self.logger.info(f'You clicked on the Uml Frame')

        diagram: UmlDiagram = self.umlDiagram

        shapes: Iterable = diagram.GetShapeList()

        for shape in shapes:
            umlShape: Shape = cast(Shape, shape)
            umlShape.Select(select=False)

        self.refresh()