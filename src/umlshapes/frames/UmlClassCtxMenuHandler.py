
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_MENU

from wx import Menu
from wx import CommandEvent

from wx import NewIdRef as wxNewIdRef

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.Common import UmlShapeList

if TYPE_CHECKING:
    from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.shapes.UmlClass import UmlClass


class UmlClassCtxMenuHandler:
    def __init__(self, frame: 'ClassDiagramFrame'):

        from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

        self.logger: Logger = getLogger(__name__)

        self._frame:       ClassDiagramFrame = frame
        self._contextMenu: Menu                 = cast(Menu, None)

        self._autoSizeID:     int = wxNewIdRef()
        self._arrangeLinksID: int = wxNewIdRef()
        self._createClassID:  int = wxNewIdRef()

        self._createContextMenu()

    def popupMenu(self, x: int, y: int):

        self.logger.debug(f'UmlClassCtxMenuHandler - x,y: {x},{y}')

        autoSizeMenuItem     = self._contextMenu.FindItemById(id=self._autoSizeID)
        arrangeLinksMenuItem = self._contextMenu.FindItemById(id=self._arrangeLinksID)
        if len(self._frame.umlShapes) == 0:
            autoSizeMenuItem.Enable(False)
            arrangeLinksMenuItem.Enable(False)
        else:
            autoSizeMenuItem.Enable(True)
            arrangeLinksMenuItem.Enable(True)

        self._frame.PopupMenu(self._contextMenu, x, y)

    def _createContextMenu(self):

        menu: Menu = Menu()

        menu.Append(self._autoSizeID,     'Auto Size Classes', 'Auto size all class objects on diagram')
        menu.Append(self._arrangeLinksID, 'Arrange Links',      'Auto arrange links')
        if UmlPreferences().classDiagramFromCtxMenu is True:
            menu.Append(self._createClassID, 'Create Class', 'Create New Class')
            menu.Bind(EVT_MENU, self._onMenuClick, id=self._createClassID)

        # Callbacks
        menu.Bind(EVT_MENU, self._onMenuClick, id=self._autoSizeID)
        menu.Bind(EVT_MENU, self._onMenuClick, id=self._arrangeLinksID)

        self._contextMenu = menu

    def _onMenuClick(self, event: CommandEvent):
        """
        Callback for the popup menu on the class

        Args:
            event:
        """
        eventId: int = event.GetId()

        # noinspection PyUnreachableCode
        match eventId:
            case self._autoSizeID:
                self._autoSize()
            case self._arrangeLinksID:
                # self._arrangeLinks()
                pass
            case _:
                self.logger.error('Unhandled Menu ID')

    def _autoSize(self):

        umlFrame:  ClassDiagramFrame = self._frame
        umlShapes: UmlShapeList        = umlFrame.umlShapes

        for umlShape in umlShapes:
            if isinstance(umlShape, UmlClass):
                umlShape.autoSize()

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
