
from typing import cast

from logging import Logger
from logging import getLogger

from collections.abc import Iterable

from wx import ClientDC
from wx import MouseEvent
from wx import Window

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas

from umlshapes.UmlUtils import UmlUtils
from umlshapes.eventengine.IUmlEventEngine import IUmlEventEngine

from umlshapes.frames.DiagramFrame import DiagramFrame

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import UmlShapeList


DEFAULT_WIDTH: int   = 3000
A4_FACTOR:     float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20


class UmlFrame(DiagramFrame):

    def __init__(self, parent: Window, umlEventEngine: IUmlEventEngine):

        self.ufLogger:     Logger          = getLogger(__name__)
        self._preferences: UmlPreferences  = UmlPreferences()
        self._eventEngine: IUmlEventEngine = umlEventEngine

        super().__init__(parent=parent)

        self.maxWidth:  int  = DEFAULT_WIDTH
        self.maxHeight: int = int(self.maxWidth / A4_FACTOR)  # 1.41 is for A4 support

        nbrUnitsX: int = int(self.maxWidth / PIXELS_PER_UNIT_X)
        nbrUnitsY: int = int(self.maxHeight / PIXELS_PER_UNIT_Y)
        initPosX:  int = 0
        initPosY:  int = 0
        self.SetScrollbars(PIXELS_PER_UNIT_X, PIXELS_PER_UNIT_Y, nbrUnitsX, nbrUnitsY, initPosX, initPosY, False)

        self.setInfinite(True)
        self._currentReportInterval: int = self._preferences.trackMouseInterval

        self._id: str = UmlUtils.getID()

    @property
    def eventEngine(self) -> IUmlEventEngine:
        return self._eventEngine

    @property
    def umlShapes(self) -> UmlShapeList:

        diagram: UmlDiagram = self.GetDiagram()
        return diagram.GetShapeList()

    @property
    def id(self) -> str:
        """
        UmlFrame ID

        Returns:  The UML generated ID
        """
        return self._id

    def OnLeftClick(self, x, y, keys=0):
        """
        Maybe this belongs in DiagramFrame

        Args:
            x:
            y:
            keys:
        """
        diagram: UmlDiagram = self.umlDiagram
        shapes:  Iterable = diagram.GetShapeList()

        for shape in shapes:
            umlShape: Shape     = cast(Shape, shape)
            canvas: ShapeCanvas = umlShape.GetCanvas()
            dc:     ClientDC    = ClientDC(canvas)
            canvas.PrepareDC(dc)

            umlShape.Select(select=False, dc=dc)

        self.refresh()

    def OnMouseEvent(self, mouseEvent: MouseEvent):
        """
        Debug hook
        TODO:  Update the UI via an event
        Args:
            mouseEvent:

        """
        super().OnMouseEvent(mouseEvent)

        if self._preferences.trackMouse is True:
            if self._currentReportInterval == 0:
                x, y = self.CalcUnscrolledPosition(mouseEvent.GetPosition())
                self.ufLogger.info(f'({x},{y})')
                self._currentReportInterval = self._preferences.trackMouseInterval
            else:
                self._currentReportInterval -= 1
