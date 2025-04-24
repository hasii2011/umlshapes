
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_MENU

from wx import Menu
from wx import CommandEvent

from wx import NewIdRef as wxNewIdRef

from umlshapes.types.Common import UmlShapes

if TYPE_CHECKING:
    from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame
from umlshapes.shapes.UmlClass import UmlClass


class UmlClassDiagramFrameMenuHandler:
    def __init__(self, frame: 'UmlClassDiagramFrame'):

        from umlshapes.frames.UmlClassDiagramFrame import UmlClassDiagramFrame

        self.logger: Logger = getLogger(__name__)

        self._frame:       UmlClassDiagramFrame = frame
        self._contextMenu: Menu                 = cast(Menu, None)

        self._autoSizeID:    int = wxNewIdRef()
        self.arrangeLinksID: int = wxNewIdRef()

        self._createContextMenu()

    def popupMenu(self, x: int, y: int):

        self.logger.debug(f'UmlClassDiagramFrameMenuHandler - x,y: {x},{y}')

        self._frame.PopupMenu(self._contextMenu, x, y)

    def _createContextMenu(self):

        menu: Menu = Menu()

        menu.Append(self._autoSizeID, 'Auto Size Classes', 'Auto size all class objects on diagram')
        menu.Append(self.arrangeLinksID, 'Arrange Links', 'Auto arrange links')

        # Callbacks
        menu.Bind(EVT_MENU, self._onMenuClick, id=self._autoSizeID)
        menu.Bind(EVT_MENU, self._onMenuClick, id=self.arrangeLinksID)

        self._contextMenu = menu

    def _onMenuClick(self, event: CommandEvent):
        """
        Callback for the popup menu on the class

        Args:
            event:
        """
        eventId: int = event.GetId()

        match eventId:
            case self._autoSizeID:
                self._autoSize()
            case self.arrangeLinksID:
                # self._arrangeLinks()
                pass
            case _:
                self.logger.error('Unhandled Menu ID')

    def _autoSize(self):

        umlFrame:  UmlClassDiagramFrame = self._frame
        umlShapes: UmlShapes            = umlFrame.umlShapes

        for umlObject in umlShapes:
            if isinstance(umlObject, UmlClass):
                oglClass: UmlClass = cast(UmlClass, umlObject)

                oglClass.autoSize()

    # def _arrangeLinks(self):
    #
    #     umlFrame:   UmlFrame = cast(UmlFrame, self._frame)
    #     umlObjects: UmlObjects = umlFrame.umlObjects
    #
    #     for oglObject in umlObjects:
    #         if isinstance(oglObject, OglLink):
    #             oglLink: OglLink = cast(OglLink, oglObject)
    #             self.logger.info(f"Optimizing: {oglLink}")
    #             oglLink.optimizeLine()
    #         else:
    #             self.logger.debug(f"No line optimizing for: {oglObject}")
