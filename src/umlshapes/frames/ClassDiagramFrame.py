
from typing import Callable
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Window

from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces
from pyutmodelv2.PyutModelTypes import ClassName

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

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
        """

        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)

        self.ucdLogger: Logger = getLogger(__name__)

        self._menuHandler:  UmlClassCtxMenuHandler = cast(UmlClassCtxMenuHandler, None)

        self._requestingLollipopLocation: bool     = False
        self._requestingUmlClass:         UmlClass = NO_CLASS

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.REQUEST_LOLLIPOP_LOCATION,
                                        frameId=self.id,
                                        listener=self._onRequestLollipopLocation)
        self._pyutInterfaceCount: int = 0

    @property
    def requestingLollipopLocation(self) -> bool:
        """
        Cheater property for the class event handler

        Returns: the mode we are in
        """
        return self._requestingLollipopLocation
    def getDefinedInterfaces(self) -> PyutInterfaces:
        """
        This will not only look for lollipop interfaces but will find UmlInterfaces.
        It will convert those PyutLink's to PyutInterfaces

        Exposed for the event handler

        Returns:  The interfaces that are on the board
        """
        from umlshapes.types.Common import UmlShapeList
        from umlshapes.links.UmlInterface import UmlInterface
        from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

        # umlLollipopInterface: UmlLollipopInterface = self.GetShape()
        # umlFrame:             ClassDiagramFrame = umlLollipopInterface.GetCanvas()

        umlShapes:      UmlShapeList   = self.umlShapes
        pyutInterfaces: PyutInterfaces = PyutInterfaces([])

        for umlShape in umlShapes:

            if isinstance(umlShape, UmlLollipopInterface):
                lollipopInterface: UmlLollipopInterface = umlShape
                pyutInterface:     PyutInterface = lollipopInterface.pyutInterface

                if pyutInterface.name != '' or len(pyutInterface.name) > 0:
                    if pyutInterface not in pyutInterfaces:
                        pyutInterfaces.append(pyutInterface)
            elif isinstance(umlShape, UmlInterface):
                umlInterface: UmlInterface = umlShape
                interface:    UmlClass     = umlInterface.interfaceClass
                implementor:  UmlClass     = umlInterface.implementingClass
                #
                # Convert to PyutInterface
                #
                pyutInterface = PyutInterface(name=interface.pyutClass.name)
                pyutInterface.addImplementor(ClassName(implementor.pyutClass.name))

                pyutInterfaces.append(pyutInterface)

        return pyutInterfaces


    def OnLeftClick(self, x, y, keys=0):

        if self._requestingLollipopLocation:
            self.ufLogger.debug(f'Request location: x,y=({x},{y}) {self._requestingUmlClass=}')
            nearestPoint: UmlPosition = UmlUtils.getNearestPointOnRectangle(x=x, y=y, rectangle=self._requestingUmlClass.rectangle)
            self.ucdLogger.debug(f'Nearest point: {nearestPoint}')

            assert self._requestingUmlClass is not None, 'I need something to attach to'
            self._requestCreationOfLollipopInterface(
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

    def _requestCreationOfLollipopInterface(self, requestingUmlClass: UmlClass, perimeterPoint: UmlPosition):
        """
        Args:
            requestingUmlClass:
            perimeterPoint:
        """
        self._umlPubSubEngine.sendMessage(UmlMessageType.CREATE_LOLLIPOP,
                                          frameId=self.id,
                                          requestingFrame=self,
                                          requestingUmlClass=requestingUmlClass,
                                          pyutInterfaces=self.getDefinedInterfaces(),
                                          perimeterPoint=perimeterPoint,
                                          )
        #
        # cleanup
        #
        self._requestingLollipopLocation = False
        self._requestingUmlClass         = NO_CLASS

        self.refresh()
        self._umlPubSubEngine.sendMessage(UmlMessageType.FRAME_MODIFIED,
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
