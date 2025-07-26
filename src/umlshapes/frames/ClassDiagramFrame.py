
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Window

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.UmlClassCtxMenuHandler import UmlClassCtxMenuHandler
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.UmlUtils import UmlUtils

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPosition

NO_CLASS: UmlClass = cast(UmlClass, None)

CreateLollipopCallback = Callable[[UmlClass, UmlPosition], None]


class ClassDiagramFrame(UmlFrame):

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine, createLollipopCallback: CreateLollipopCallback):
        """

        Args:
            parent:
            createLollipopCallback:
        """

        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)

        self._createLollipopCallback: CreateLollipopCallback = createLollipopCallback

        self.ucdLogger: Logger = getLogger(__name__)

        self._menuHandler:  UmlClassCtxMenuHandler = cast(UmlClassCtxMenuHandler, None)

        self._requestingLollipopLocation: bool     = False
        self._requestingUmlClass:         UmlClass = NO_CLASS

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.REQUEST_LOLLIPOP_LOCATION,
                                        frameId=self.id,
                                        callback=self._onRequestLollipopLocation)
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

        if self._requestingLollipopLocation:
            self.ufLogger.debug(f'Request location: x,y=({x},{y}) {self._requestingUmlClass=}')
            nearestPoint: UmlPosition = UmlUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=self._requestingUmlClass.rectangle)
            self.ucdLogger.debug(f'Nearest point: {nearestPoint}')

            assert self._requestingUmlClass is not None, 'I need something to attach to'
            self._createLollipopInterface(
                requestingUmlClass=self._requestingUmlClass,
                perimeterPoint=nearestPoint
            )
            self.umlPubSubEngine.sendMessage(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                             frameId=self.id,
                                             message='')
        else:
            super().OnLeftClick(x=x, y=y, keys=keys)

    def OnRightClick(self, x: int, y: int, keys: int = 0):
        self.ucdLogger.debug('Ouch, you right-clicked me !!')

        if not self._areWeOverAShape(x=x, y=y):
            self.ucdLogger.info('You missed the shape')
            if self._menuHandler is None:
                self._menuHandler = UmlClassCtxMenuHandler(self)

            self._menuHandler.popupMenu(x=x, y=y)

    def _onRequestLollipopLocation(self, requestingUmlClass: UmlClass):

        self.ufLogger.debug(f'{requestingUmlClass=}')
        self._requestingLollipopLocation = True
        self._requestingUmlClass         = requestingUmlClass

        self.umlPubSubEngine.sendMessage(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                         frameId=self.id,
                                         message='Click on the UML Class edge where you want to place the interface')

    def _createLollipopInterface(self, requestingUmlClass: UmlClass, perimeterPoint: UmlPosition):
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
        self._umlPubSubEngine.sendMessage(UmlMessageType.DIAGRAM_MODIFIED,
                                          frameId=self.id,
                                          modifiedFrameId=self.id
                                          )

    def _areWeOverAShape(self, x: int, y: int) -> bool:
        answer:         bool  = True
        shape, n = self.FindShape(x=x, y=y)
        # Don't popup over a shape
        if shape is None:
            answer = False

        return answer

    def __repr__(self) -> str:
        return f'ClassDiagramFrame - `{self.id}`'

    def __str__(self) -> str:
        return self.__repr__()
