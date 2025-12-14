
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlmodel.Class import Class
from umlmodel.enumerations.DisplayMethods import DisplayMethods
from umlmodel.enumerations.DisplayParameters import DisplayParameters
from wx import Bitmap

from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import EVT_MENU

from wx import CommandEvent
from wx import Menu
from wx import MenuItem

from wx import NewIdRef as wxNewIdRef

from umlshapes.UmlUtils import UmlUtils

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.frames.DiagramFrame import FrameId

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass

# Menu IDs
[
    ID_TOGGLE_STEREOTYPE,
    ID_TOGGLE_FIELDS,
    ID_TOGGLE_METHODS,
    ID_TOGGLE_METHOD_PARAMETERS,
    ID_TOGGLE_CONSTRUCTOR,
    ID_TOGGLE_DUNDER_METHODS,
    ID_AUTO_SIZE,
    ID_CUT_SHAPE,
    ID_IMPLEMENT_INTERFACE
]  = wxNewIdRef(9)

HELP_STEREOTYPE:     str = 'Set stereotype display on or off'
HELP_FIELDS:         str = 'Set fields display on or off'
HELP_METHODS:        str = 'Set methods display on or off'
HELP_PARAMETERS:     str = 'Set parameter display Unspecified, On or Off'
HELP_CONSTRUCTOR:    str = 'Set constructor display Unspecified, On or Off'
HELP_DUNDER_METHODS: str = 'Set dunder method display Unspecified, On or Off'


@dataclass
class TriStateData:
    bitMap:   Bitmap
    menuText: str


class UmlClassMenuHandler:
    def __init__(self, umlClass: 'UmlClass', umlPubSubEngine: IUmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._umlClass:       'UmlClass'        = umlClass
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self._contextMenu:         Menu     = cast(Menu, None)
        self._toggleStereotype:    MenuItem = cast(MenuItem, None)
        self._toggleFields:        MenuItem = cast(MenuItem, None)
        self._toggleMethods:       MenuItem = cast(MenuItem, None)
        self._toggleParameters:    MenuItem = cast(MenuItem, None)
        self._toggleConstructor:   MenuItem = cast(MenuItem, None)
        self._toggleDunderMethods: MenuItem = cast(MenuItem, None)

        self._createContextMenu()

    def popupMenu(self, x: int, y: int):

        modelClass: Class = self._umlClass.modelClass

        self._setMenuItemValues(modelClass)

        self.logger.debug(f'UmlClassMenuHandler - x,y: {x},{y}')

        frame: UmlFrame = self._umlClass.umlFrame
        frame.PopupMenu(self._contextMenu, x, y)

    def _createContextMenu(self):

        menu: Menu = Menu()

        self._toggleStereotype    = menu.Append(id=ID_TOGGLE_STEREOTYPE,        item="Toggle stereotype display", helpString=HELP_STEREOTYPE,     kind=ITEM_CHECK)
        self._toggleFields        = menu.Append(id=ID_TOGGLE_FIELDS,            item="Toggle fields display",     helpString=HELP_FIELDS,         kind=ITEM_CHECK)
        self._toggleMethods       = menu.Append(id=ID_TOGGLE_METHODS,           item="Toggle methods display",    helpString=HELP_METHODS,        kind=ITEM_CHECK)
        self._toggleParameters    = menu.Append(id=ID_TOGGLE_METHOD_PARAMETERS, item=" ",                         helpString=HELP_PARAMETERS,     kind=ITEM_NORMAL)
        self._toggleConstructor   = menu.Append(id=ID_TOGGLE_CONSTRUCTOR,       item=" ",                         helpString=HELP_CONSTRUCTOR,    kind=ITEM_NORMAL)
        self._toggleDunderMethods = menu.Append(id=ID_TOGGLE_DUNDER_METHODS,    item=" ",                         helpString=HELP_DUNDER_METHODS, kind=ITEM_NORMAL)

        menu.Append(ID_AUTO_SIZE, 'Auto Size', 'Resize to see the entire class')
        menu.Append(ID_CUT_SHAPE, 'Cut shape', 'Cut this shape')
        menu.Append(ID_IMPLEMENT_INTERFACE, 'Implement Interface', 'Use Existing interface or create new one')

        # Callbacks
        menu.Bind(EVT_MENU, self._onMenuClick, id=ID_TOGGLE_STEREOTYPE)
        menu.Bind(EVT_MENU, self._onMenuClick, id=ID_TOGGLE_FIELDS)
        menu.Bind(EVT_MENU, self._onMenuClick, id=ID_TOGGLE_METHODS)
        menu.Bind(EVT_MENU, self._onMenuClick, id=ID_AUTO_SIZE)
        menu.Bind(EVT_MENU, self._onMenuClick, id=ID_CUT_SHAPE)
        menu.Bind(EVT_MENU, self._onMenuClick, id=ID_IMPLEMENT_INTERFACE)
        menu.Bind(EVT_MENU, self._onDisplayParametersClick,    id=ID_TOGGLE_METHOD_PARAMETERS)
        menu.Bind(EVT_MENU, self._onDisplayConstructorClick,   id=ID_TOGGLE_CONSTRUCTOR)
        menu.Bind(EVT_MENU, self._onDisplayDunderMethodsClick, id=ID_TOGGLE_DUNDER_METHODS)

        self._contextMenu = menu

    def _onMenuClick(self, event: CommandEvent):
        """
        Callback for the popup menu on the class

        Args:
            event:
        """
        modelClass: Class = self._umlClass.modelClass
        eventId:   int       = event.GetId()
        frameId:   FrameId   = self._getFrameId()

        if eventId == ID_TOGGLE_STEREOTYPE:
            modelClass.displayStereoType = not modelClass.displayStereoType
            self._umlClass.autoSize()
        elif eventId == ID_TOGGLE_METHODS:
            modelClass.showMethods = not modelClass.showMethods     # flip it!!  too cute
            self._umlClass.autoSize()
        elif eventId == ID_TOGGLE_FIELDS:
            modelClass.showFields = not modelClass.showFields       # flip it!! too cute
            self._umlClass.autoSize()
        elif eventId == ID_AUTO_SIZE:
            self._umlClass.autoSize()
        elif eventId == ID_IMPLEMENT_INTERFACE:
            self._umlPubSubEngine.sendMessage(UmlMessageType.REQUEST_LOLLIPOP_LOCATION,
                                              frameId=frameId,
                                              requestingUmlClass=self._umlClass)
        elif eventId == ID_CUT_SHAPE:
            # Cheater way to cut but eliminates a message
            self._umlClass.selected = True
            # self._umlClass.umlFrame.refresh()     # No clue to the end-user
            self._umlPubSubEngine.sendMessage(UmlMessageType.CUT_SHAPES,
                                              frameId=frameId
                                              )
        else:
            event.Skip()

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=frameId, modifiedFrameId=frameId)

    # noinspection PyUnusedLocal
    def _onDisplayParametersClick(self, event: CommandEvent):
        """
        This menu item has its own handler because this option is tri-state

        Unspecified --> Display --> Do Not Display ---|
            ^------------------------------------------|

        Args:
            event:
        """
        modelClass:        Class             = self._umlClass.modelClass
        displayParameters: DisplayParameters = modelClass.displayParameters
        self.logger.debug(f'{displayParameters=}')

        # noinspection PyUnreachableCode
        match displayParameters:
            case DisplayParameters.UNSPECIFIED:
                modelClass.displayParameters = DisplayParameters.DISPLAY_PARAMETERS
            case DisplayParameters.DISPLAY_PARAMETERS:
                modelClass.displayParameters = DisplayParameters.DO_NOT_DISPLAY_PARAMETERS
            case DisplayParameters.DO_NOT_DISPLAY_PARAMETERS:
                modelClass.displayParameters = DisplayParameters.UNSPECIFIED
            case _:
                assert False, 'Unknown display type'

        self._umlClass.autoSize()
        self.logger.debug(f'{modelClass.displayParameters=}')

    # noinspection PyUnusedLocal
    def _onDisplayConstructorClick(self, event: CommandEvent):
        """

        Args:
            event:
        """
        modelClass:         Class          = self._umlClass.modelClass
        displayConstructor: DisplayMethods = modelClass.displayConstructor

        modelClass.displayConstructor = self._nextDisplayValue(displayValue=displayConstructor)
        self._umlClass.autoSize()

    # noinspection PyUnusedLocal
    def _onDisplayDunderMethodsClick(self, event: CommandEvent):
        """

        Args:
            event:
        """
        modelClass:           Class          = self._umlClass.modelClass
        displayDunderMethods: DisplayMethods = modelClass.displayDunderMethods

        modelClass.displayDunderMethods = self._nextDisplayValue(displayValue=displayDunderMethods)
        self._umlClass.autoSize()
        self.logger.debug(f'{displayDunderMethods=}')

    def _setMenuItemValues(self, modelClass: Class):

        self._toggleStereotype.Check(modelClass.displayStereoType)
        self._toggleFields.Check(modelClass.showFields)
        self._toggleMethods.Check(modelClass.showMethods)

        self._setTheTriStateDisplayParametersMenuItem(modelClass=modelClass)
        self._setTheTriStateDisplayConstructorMenuItem(modelClass=modelClass)
        self._setTheTriStateDisplayDunderMethodsMenuItem(modelClass=modelClass)

    def _setTheTriStateDisplayParametersMenuItem(self, modelClass: Class):

        displayParameters:    DisplayParameters = modelClass.displayParameters
        itemToggleParameters: MenuItem          = self._toggleParameters

        # noinspection PyUnreachableCode
        match displayParameters:
            case DisplayParameters.UNSPECIFIED:
                triStateData: TriStateData = TriStateData(bitMap=UmlUtils.unspecifiedDisplayIcon(), menuText='Unspecified Parameter Display')
            case DisplayParameters.DISPLAY_PARAMETERS:
                triStateData = TriStateData(bitMap=UmlUtils.displayIcon(), menuText='Display Parameters')
            case DisplayParameters.DO_NOT_DISPLAY_PARAMETERS:
                triStateData = TriStateData(bitMap=UmlUtils.doNotDisplayIcon(), menuText='Do Not Display Parameters')
            case _:
                self.logger.warning(f'Unknown Parameter Display type: {displayParameters}')
                assert False, 'Developer error'

        itemToggleParameters.SetBitmap(triStateData.bitMap)     # noqa
        itemToggleParameters.SetItemLabel(triStateData.menuText)

    def _setTheTriStateDisplayConstructorMenuItem(self, modelClass: Class):

        displayConstructor:    DisplayMethods = modelClass.displayConstructor
        itemToggleConstructor: MenuItem       = self._toggleConstructor

        triStateData: TriStateData = self._getTriStateData(displayValue=displayConstructor, displayName='Constructor')

        # noinspection PyTypeChecker
        itemToggleConstructor.SetBitmap(triStateData.bitMap)
        itemToggleConstructor.SetItemLabel(triStateData.menuText)

    def _setTheTriStateDisplayDunderMethodsMenuItem(self, modelClass: Class):

        displayDunderMethods:  DisplayMethods = modelClass.displayDunderMethods
        itemToggleConstructor: MenuItem       = self._toggleDunderMethods

        triStateData: TriStateData = self._getTriStateData(displayValue=displayDunderMethods, displayName='Dunder Methods')

        # noinspection PyTypeChecker
        itemToggleConstructor.SetBitmap(triStateData.bitMap)
        itemToggleConstructor.SetItemLabel(triStateData.menuText)

    def _getTriStateData(self, displayValue: DisplayMethods, displayName: str) -> TriStateData:

        # noinspection PyUnreachableCode
        match displayValue:

            case DisplayMethods.UNSPECIFIED:
                return TriStateData(bitMap=UmlUtils.unspecifiedDisplayIcon(), menuText=f'Unspecified {displayName} Display')
            case DisplayMethods.DISPLAY:
                return TriStateData(bitMap=UmlUtils.displayIcon(), menuText=f'Display {displayName}')
            case DisplayMethods.DO_NOT_DISPLAY:
                return TriStateData(bitMap=UmlUtils.doNotDisplayIcon(), menuText=f'Do Not Display {displayName}')
            case _:
                self.logger.warning(f'Unknown Method Display type: {displayValue}')
                assert False, 'Developer error'

    def _nextDisplayValue(self, displayValue: DisplayMethods) -> DisplayMethods:

        # noinspection PyUnreachableCode
        match displayValue:
            case DisplayMethods.UNSPECIFIED:
                return DisplayMethods.DISPLAY
            case DisplayMethods.DISPLAY:
                return DisplayMethods.DO_NOT_DISPLAY
            case DisplayMethods.DO_NOT_DISPLAY:
                return DisplayMethods.UNSPECIFIED
            case _:
                assert False, "Unknown method display type"

    def _getFrameId(self) -> FrameId:
        return self._getFrame().id

    def _getFrame(self) -> UmlFrame:
        umlFrame: UmlFrame = self._umlClass.umlFrame
        return umlFrame
