
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.Interface import Interface
from umlmodel.Interface import Interfaces
from umlmodel.ModelTypes import ClassName
from wx import MouseEvent
from wx import Window

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.dialogs.DlgDisplayLollipopPlacementMsg import DlgDisplayLollipopPlacementMsg
from umlshapes.dialogs.DlgDisplayLollipopPlacementMsg import LOLLIPOP_PLACEMENT_MESSAGE
from umlshapes.frames.UmlClassCtxMenuHandler import UmlClassCtxMenuHandler
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.utils.CoordinateUtils import CoordinateUtils
from umlshapes.utils.ProximityUtils import ProximityUtils

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlPosition import UmlPoint
from umlshapes.types.UmlPosition import UmlPosition

NO_CLASS: UmlClass = cast(UmlClass, None)       # noqa


class ClassDiagramFrame(UmlFrame):

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
        """

        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)

        self.ucdLogger: Logger = getLogger(__name__)

        self._requestingLollipopLocation: bool     = False
        self._requestingUmlClass:         UmlClass = NO_CLASS

        self._menuHandler: UmlClassCtxMenuHandler = UmlClassCtxMenuHandler(self)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.REQUEST_LOLLIPOP_LOCATION,
                                        frameId=self.id,
                                        listener=self._onRequestLollipopLocation)

    def getDefinedInterfaces(self) -> Interfaces:
        """
        This will not only look for lollipop interfaces but will find UmlInterfaces.
        It will convert those Link's to Interfaces

        Exposed for the event handler

        Returns:  The interfaces that are on the board
        """
        from umlshapes.ShapeTypes import UmlShapes
        from umlshapes.links.UmlInterface import UmlInterface
        from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface

        umlShapes:  UmlShapes  = self.umlShapes
        interfaces: Interfaces = Interfaces([])

        for umlShape in umlShapes:

            if isinstance(umlShape, UmlLollipopInterface):
                lollipopInterface: UmlLollipopInterface = umlShape
                interface:         Interface            = lollipopInterface.modelInterface

                if interface.name != '' or len(interface.name) > 0:
                    if interface not in interfaces:
                        interfaces.append(interface)
            elif isinstance(umlShape, UmlInterface):
                umlInterface:   UmlInterface = umlShape
                interfaceClass: UmlClass     = umlInterface.interfaceClass
                implementor:    UmlClass     = umlInterface.implementingClass
                #
                # Convert to mode interface
                #
                interface = Interface(name=interfaceClass.modelClass.name)
                interface.addImplementor(ClassName(implementor.modelClass.name))

                interfaces.append(interface)

        return interfaces

    def OnMouseEvent(self, mouseEvent: MouseEvent):
        """
        Overrides UmlFrame.OnMouseEvent to intercept left-click placement when
        requesting a lollipop interface location, creating the lollipop only if
        the click lands inside or on the border of the requesting UmlClass.

        Args:
            mouseEvent: The incoming mouse event.
        """
        if self._requestingLollipopLocation:
            if mouseEvent.LeftDown():
                return
            if mouseEvent.LeftUp():
                x: int
                y: int
                x, y = self._convertEventCoordinates(mouseEvent)
                assert self._requestingUmlClass is not None, 'I need something to attach to'
                clickPoint: UmlPoint = UmlPoint(x=x, y=y)
                if CoordinateUtils.isPointInsideRectangle(
                    point=clickPoint,
                    rectangle=self._requestingUmlClass.rectangle
                ) is True:
                    self.ufLogger.debug(f'Request location: x,y=({x},{y}) {self._requestingUmlClass=}')
                    nearestPoint: UmlPosition = ProximityUtils.getNearestPointOnRectangle(
                        x=x,
                        y=y,
                        rectangle=self._requestingUmlClass.rectangle
                    )
                    self.ucdLogger.debug(f'Nearest point: {nearestPoint}')

                    self._requestCreationOfLollipopInterface(
                        requestingUmlClass=self._requestingUmlClass,
                        perimeterPoint=nearestPoint
                    )
                    self.umlPubSubEngine.sendMessage(
                        UmlMessageType.UPDATE_APPLICATION_STATUS,
                        frameId=self.id,
                        message=''
                    )
                return

        super().OnMouseEvent(mouseEvent)

    def OnRightClick(self, x: int, y: int, keys: int = 0):
        self.ucdLogger.debug('Ouch, you right-clicked me !!')

        if not self._areWeOverAShape(x=x, y=y):
            self.ucdLogger.info('You missed the shape')
            self._menuHandler.popupMenu(x=x, y=y)

    def _onRequestLollipopLocation(self, requestingUmlClass: UmlClass):

        self.ufLogger.debug(f'{requestingUmlClass=}')
        self._requestingLollipopLocation = True
        self._requestingUmlClass         = requestingUmlClass

        self.umlPubSubEngine.sendMessage(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                         frameId=self.id,
                                         message=LOLLIPOP_PLACEMENT_MESSAGE)

        if self._preferences.showLollipopPlacementDialog is True:
            self._showLollipopPlacementDialog()

    def _showLollipopPlacementDialog(self):
        """
        Displays instructions on placing the lollipop interface.
        If the user unchecks 'Show this dialog next time', updates the preference to False.
        """
        placementDialog: DlgDisplayLollipopPlacementMsg = DlgDisplayLollipopPlacementMsg(
            parent=self,
            preferences=self._preferences
        )
        with placementDialog:
            placementDialog.ShowModal()

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
                                           interfaces=self.getDefinedInterfaces(),
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
        # Do not pop up over a shape
        if shape is None:
            answer = False

        return answer

    def __repr__(self) -> str:
        return f'ClassDiagramFrame - `{self.id}`'

    def __str__(self) -> str:
        return self.__repr__()
