
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.IApplicationAdapter import IApplicationAdapter

from umlshapes.eventengine.UmlEvents import EVT_REQUEST_LOLLIPOP_LOCATION
from umlshapes.eventengine.UmlEvents import RequestLollipopLocationEvent

from umlshapes.frames.UmlClassDiagramFrameMenuHandler import UmlClassDiagramFrameMenuHandler
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.UmlUtils import UmlUtils

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPosition

NO_CLASS: UmlClass = cast(UmlClass, None)

CreateLollipopCallback = Callable[[UmlClass, UmlPosition], None]


class UmlClassDiagramFrame(UmlFrame):

    def __init__(self, parent: Window, applicationAdapter: IApplicationAdapter, createLollipopCallback: CreateLollipopCallback):
        """

        Args:
            parent:
            applicationAdapter:
            createLollipopCallback:
        """

        super().__init__(parent=parent, applicationAdapter=applicationAdapter)

        self._createLollipopCallback: CreateLollipopCallback = createLollipopCallback

        self.ucdLogger: Logger = getLogger(__name__)

        self._menuHandler:  UmlClassDiagramFrameMenuHandler = cast(UmlClassDiagramFrameMenuHandler, None)

        self._requestingLollipopLocation: bool     = False
        self._requestingUmlClass:         UmlClass = NO_CLASS

        self._eventEngine.registerListener(event=EVT_REQUEST_LOLLIPOP_LOCATION, callback=self._onRequestLollipopLocation)
        # self._oglEventEngine.registerListener(event=EVT_DIAGRAM_FRAME_MODIFIED,    callback=self._onDiagramModified)
        # self._oglEventEngine.registerListener(event=EVT_CUT_OGL_CLASS,             callback=self._onCutClass)

        self._pyutInterfaceCount: int = 0

    @property
    def requestingLollipopLocation(self) -> bool:
        """
        Cheater property for the class event handler

        Returns: the mode we are in
        """
        return self._requestingLollipopLocation

    def OnLeftClick(self, x, y, keys=0):

        if self._requestingLollipopLocation is True:
            self.ufLogger.debug(f'Request location: x,y=({x},{y}) {self._requestingUmlClass=}')
            nearestPoint: UmlPosition = UmlUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=self._requestingUmlClass.rectangle)
            self.ucdLogger.debug(f'Nearest point: {nearestPoint}')

            assert self._requestingUmlClass is not None, 'I need something to attach to'
            self.createLollipopInterface(
                requestingUmlClass=self._requestingUmlClass,
                perimeterPoint=nearestPoint
            )
            self._applicationAdapter.updateApplicationStatus('')
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

        self.ufLogger.debug(f'{event.requestShape=}')
        self._requestingLollipopLocation = True
        self._requestingUmlClass            = event.requestShape

        self._applicationAdapter.updateApplicationStatus('Click on the UML Class edge where you want to place the interface')

    def createLollipopInterface(self, requestingUmlClass: UmlClass, perimeterPoint: UmlPosition):
        """
        Args:
            requestingUmlClass:
            perimeterPoint:
        """
        assert self._createLollipopCallback is not None, 'Impossible !!!'
        self._createLollipopCallback(requestingUmlClass, perimeterPoint)
        #
        # cleanup
        #
        self._requestingLollipopLocation = False
        self._requestingUmlClass         = NO_CLASS

        self.refresh()

    def _areWeOverAShape(self, x: int, y: int) -> bool:
        answer:         bool  = True
        shape, n = self.FindShape(x=x, y=y)
        # Don't popup over a shape
        if shape is None:
            answer = False

        return answer

    def __repr__(self) -> str:
        return f'UmlClassDiagramFrame - `{self.id}`'

    def __str__(self) -> str:
        return self.__repr__()
