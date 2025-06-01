
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Point
from wx import Window

from umlshapes.UmlUtils import UmlUtils
from umlshapes.IApplicationAdapter import IApplicationAdapter

from umlshapes.eventengine.UmlEvents import CreateLollipopInterfaceEvent
from umlshapes.eventengine.UmlEvents import EVT_REQUEST_LOLLIPOP_LOCATION
from umlshapes.eventengine.UmlEvents import RequestLollipopLocationEvent

from umlshapes.frames.UmlClassDiagramFrameMenuHandler import UmlClassDiagramFrameMenuHandler
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.UmlClass import UmlClass


class UmlClassDiagramFrame(UmlFrame):

    def __init__(self, parent: Window, applicationAdapter: IApplicationAdapter):

        super().__init__(parent=parent, applicationAdapter=applicationAdapter)

        self.ucdLogger: Logger = getLogger(__name__)

        self._menuHandler:  UmlClassDiagramFrameMenuHandler = cast(UmlClassDiagramFrameMenuHandler, None)

        self._requestingLollipopLocation: bool    = False
        self._requestingUmlClass:         UmlClass = cast(UmlClass, None)

        self._eventEngine.registerListener(event=EVT_REQUEST_LOLLIPOP_LOCATION, callback=self._onRequestLollipopLocation)
        # self._oglEventEngine.registerListener(event=EVT_CREATE_LOLLIPOP_INTERFACE, callback=self._onCreateLollipopInterface)
        # self._oglEventEngine.registerListener(event=EVT_DIAGRAM_FRAME_MODIFIED,    callback=self._onDiagramModified)
        # self._oglEventEngine.registerListener(event=EVT_CUT_OGL_CLASS,             callback=self._onCutClass)

    @property
    def requestingLollipopLocation(self) -> bool:
        """
        Cheater property for the class event handler

        Returns: the mode we are in
        """
        return self._requestingLollipopLocation

    def OnLeftClick(self, x, y, keys=0):

        if self._requestingLollipopLocation is True:
            self.ufLogger.info(f'Request location: x,y=({x},{y}) {self._requestingUmlClass=}')
            self._requestingLollipopLocation = False
            nPoint: Point = UmlUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=self._requestingUmlClass.rectangle)
            self.ucdLogger.info(f'Nearest point: {nPoint}')
        else:
            super().OnLeftClick(x=x, y=y, keys=keys)

    def OnRightClick(self, x: int, y: int, keys: int = 0):
        self.ucdLogger.debug('Ouch, you right-clicked me !!')

        if self._areWeOverAShape(x=x, y=y) is False:
            self.ucdLogger.info('You missed the shape')
            if self._menuHandler is None:
                self._menuHandler = UmlClassDiagramFrameMenuHandler(self)

            self._menuHandler.popupMenu(x=x, y=y)

    def _onRequestLollipopLocation(self, event: RequestLollipopLocationEvent):

        self.ufLogger.info(f'{event.requestShape=}')
        self._requestingLollipopLocation = True
        self._requestingUmlClass            = event.requestShape

        self._applicationAdapter.updateApplicationStatus('Click on the UML Class edge where you want to place the interface')

    def _onCreateLollipopInterface(self, event: CreateLollipopInterfaceEvent):

        from umlshapes.shapes.UmlClass import UmlClass

        attachmentPoint: Point    = event.attachmentPoint
        implementor:     UmlClass = event.implementor
        self.ufLogger.info(f'{attachmentPoint=} {implementor=}')

        # self._createLollipopInterface(self, implementor=implementor, attachmentAnchor=attachmentPoint)

    def _areWeOverAShape(self, x: int, y: int) -> bool:
        answer:         bool  = True
        shape, n = self.FindShape(x=x, y=y)
        # Don't popup over a shape
        if shape is None:
            answer = False

        return answer
