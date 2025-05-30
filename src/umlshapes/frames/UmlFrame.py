
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from collections.abc import Iterable

from wx import ClientDC
from wx import MessageBox
from wx import MouseEvent
from wx import OK
from wx import Point
from wx import Window

from wx import Yield as wxYield

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.eventengine.UmlEventEngine import UmlEventEngine
from umlshapes.eventengine.UmlEvents import CreateLollipopInterfaceEvent
from umlshapes.eventengine.UmlEvents import EVT_REQUEST_LOLLIPOP_LOCATION
from umlshapes.eventengine.UmlEvents import RequestLollipopLocationEvent

from umlshapes.frames.DiagramFrame import DiagramFrame

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.Common import UmlShapeList


DEFAULT_WIDTH: int   = 3000
A4_FACTOR:     float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20


class UmlFrame(DiagramFrame):
    def __init__(self, parent: Window):

        self.ufLogger:     Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        self._eventEngine: UmlEventEngine = UmlEventEngine(listeningWindow=self)

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

        self._requestingLollipopLocation: bool = False
        self._eventEngine.registerListener(event=EVT_REQUEST_LOLLIPOP_LOCATION, callback=self._onRequestLollipopLocation)
        # self._oglEventEngine.registerListener(event=EVT_CREATE_LOLLIPOP_INTERFACE, callback=self._onCreateLollipopInterface)
        # self._oglEventEngine.registerListener(event=EVT_DIAGRAM_FRAME_MODIFIED,    callback=self._onDiagramModified)
        # self._oglEventEngine.registerListener(event=EVT_CUT_OGL_CLASS,             callback=self._onCutClass)

    @property
    def eventEngine(self) -> UmlEventEngine:
        return self._eventEngine

    @property
    def umlShapes(self) -> UmlShapeList:

        diagram: UmlDiagram = self.GetDiagram()
        return diagram.GetShapeList()

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

        if self._requestingLollipopLocation is False:
            for shape in shapes:
                umlShape: Shape     = cast(Shape, shape)
                canvas: ShapeCanvas = umlShape.GetCanvas()
                dc:     ClientDC    = ClientDC(canvas)
                canvas.PrepareDC(dc)

                umlShape.Select(select=False, dc=dc)
        else:
            self.ufLogger.info(f'Did I get a location?')
            self._requestingLollipopLocation = False

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

    def _onRequestLollipopLocation(self, event: RequestLollipopLocationEvent):

        self.ufLogger.info(f'{event.requestShape=}')
        self._requestingLollipopLocation = True
        shape = event.requestShape
        self._requestLollipopLocation(shape)

    def _onCreateLollipopInterface(self, event: CreateLollipopInterfaceEvent):

        from umlshapes.shapes.UmlClass import UmlClass

        attachmentPoint: Point    = event.attachmentPoint
        implementor:     UmlClass = event.implementor
        self.ufLogger.info(f'{attachmentPoint=} {implementor=}')

        # self._createLollipopInterface(self, implementor=implementor, attachmentAnchor=attachmentPoint)

    def _requestLollipopLocation(self, destinationClass: 'UmlClass'):

        self.ufLogger.info(f'{destinationClass=}')
        # self._createPotentialAttachmentPoints(destinationClass=destinationClass)
        # self._demoEventEngine.sendEvent(DemoEventType.SET_STATUS_TEXT, statusMessage='Select attachment point')
        MessageBox(
            message='Click on the edge where you want to place the lollipop',
            caption='Touch me',
            style=OK,
            parent=self
                   )
        self.Refresh()
        wxYield()
