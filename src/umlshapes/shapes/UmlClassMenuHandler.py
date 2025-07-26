from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import Bitmap

from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import EVT_MENU

from wx import CommandEvent
from wx import Menu
from wx import MenuItem

from wx import NewIdRef as wxNewIdRef

from pyutmodelv2.PyutClass import PyutClass

from pyutmodelv2.enumerations.PyutDisplayParameters import PyutDisplayParameters
from pyutmodelv2.enumerations.PyutDisplayMethods import PyutDisplayMethods

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

        pyutClass: PyutClass = self._umlClass.pyutClass

        self._setMenuItemValues(pyutClass)

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
        pyutClass: PyutClass = self._umlClass.pyutClass
        eventId:   int       = event.GetId()
        frameId:   FrameId   = self._getFrameId()

        if eventId == ID_TOGGLE_STEREOTYPE:
            pyutClass.displayStereoType = not pyutClass.displayStereoType
            self._umlClass.autoSize()
        elif eventId == ID_TOGGLE_METHODS:
            pyutClass.showMethods = not pyutClass.showMethods     # flip it!!  too cute
            self._umlClass.autoSize()
        elif eventId == ID_TOGGLE_FIELDS:
            pyutClass.showFields = not pyutClass.showFields       # flip it!! too cute
            self._umlClass.autoSize()
        elif eventId == ID_AUTO_SIZE:
            self._umlClass.autoSize()
        elif eventId == ID_IMPLEMENT_INTERFACE:
            self._umlPubSubEngine.sendMessage(UmlMessageType.REQUEST_LOLLIPOP_LOCATION,
                                              frameId=frameId,
                                              requestingUmlClass=self._umlClass)
        elif eventId == ID_CUT_SHAPE:
            self._umlPubSubEngine.sendMessage(UmlMessageType.CUT_UML_CLASS,
                                              frameId=frameId,
                                              frameshapeToCut=self._umlClass)
        else:
            event.Skip()

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.DIAGRAM_MODIFIED, frameId=frameId, modifiedFrameId=frameId)

    # noinspection PyUnusedLocal
    def _onDisplayParametersClick(self, event: CommandEvent):
        """
        This menu item has its own handler because this option is tri-state

        Unspecified --> Display --> Do Not Display ---|
            ^------------------------------------------|

        Args:
            event:
        """
        pyutClass:         PyutClass             = self._umlClass.pyutClass
        displayParameters: PyutDisplayParameters = pyutClass.displayParameters
        self.logger.debug(f'{displayParameters=}')

        # noinspection PyUnreachableCode
        match displayParameters:
            case PyutDisplayParameters.UNSPECIFIED:
                pyutClass.displayParameters = PyutDisplayParameters.WITH_PARAMETERS
            case PyutDisplayParameters.WITH_PARAMETERS:
                pyutClass.displayParameters = PyutDisplayParameters.WITHOUT_PARAMETERS
            case PyutDisplayParameters.WITHOUT_PARAMETERS:
                pyutClass.displayParameters = PyutDisplayParameters.UNSPECIFIED
            case _:
                assert False, 'Unknown display type'

        self._umlClass.autoSize()
        self.logger.debug(f'{pyutClass.displayParameters=}')

    # noinspection PyUnusedLocal
    def _onDisplayConstructorClick(self, event: CommandEvent):
        """

        Args:
            event:
        """
        pyutClass:          PyutClass          = self._umlClass.pyutClass
        displayConstructor: PyutDisplayMethods = pyutClass.displayConstructor

        pyutClass.displayConstructor = self._nextDisplayValue(pyutDisplayValue=displayConstructor)
        self._umlClass.autoSize()

    # noinspection PyUnusedLocal
    def _onDisplayDunderMethodsClick(self, event: CommandEvent):
        """

        Args:
            event:
        """
        pyutClass:            PyutClass          = self._umlClass.pyutClass
        displayDunderMethods: PyutDisplayMethods = pyutClass.displayDunderMethods

        pyutClass.displayDunderMethods = self._nextDisplayValue(pyutDisplayValue=displayDunderMethods)
        self._umlClass.autoSize()
        self.logger.debug(f'{displayDunderMethods=}')

    def _setMenuItemValues(self, pyutClass: PyutClass):

        self._toggleStereotype.Check(pyutClass.displayStereoType)
        self._toggleFields.Check(pyutClass.showFields)
        self._toggleMethods.Check(pyutClass.showMethods)

        self._setTheTriStateDisplayParametersMenuItem(pyutClass=pyutClass)
        self._setTheTriStateDisplayConstructorMenuItem(pyutClass=pyutClass)
        self._setTheTriStateDisplayDunderMethodsMenuItem(pyutClass=pyutClass)

    def _setTheTriStateDisplayParametersMenuItem(self, pyutClass: PyutClass):

        displayParameters:    PyutDisplayParameters = pyutClass.displayParameters
        itemToggleParameters: MenuItem              = self._toggleParameters

        # noinspection PyUnreachableCode
        match displayParameters:
            case PyutDisplayParameters.UNSPECIFIED:
                triStateData: TriStateData = TriStateData(bitMap=UmlUtils.unspecifiedDisplayIcon(), menuText='Unspecified Parameter Display')
            case PyutDisplayParameters.WITH_PARAMETERS:
                triStateData = TriStateData(bitMap=UmlUtils.displayIcon(), menuText='Display Parameters')
            case PyutDisplayParameters.WITHOUT_PARAMETERS:
                triStateData = TriStateData(bitMap=UmlUtils.doNotDisplayIcon(), menuText='Do Not Display Parameters')
            case _:
                self.logger.warning(f'Unknown Parameter Display type: {displayParameters}')
                assert False, 'Developer error'

        # noinspection PyTypeChecker
        itemToggleParameters.SetBitmap(triStateData.bitMap)
        itemToggleParameters.SetItemLabel(triStateData.menuText)

    def _setTheTriStateDisplayConstructorMenuItem(self, pyutClass: PyutClass):

        displayConstructor:    PyutDisplayMethods = pyutClass.displayConstructor
        itemToggleConstructor: MenuItem           = self._toggleConstructor

        triStateData: TriStateData = self._getTriStateData(pyutDisplayValue=displayConstructor, displayName='Constructor')

        # noinspection PyTypeChecker
        itemToggleConstructor.SetBitmap(triStateData.bitMap)
        itemToggleConstructor.SetItemLabel(triStateData.menuText)

    def _setTheTriStateDisplayDunderMethodsMenuItem(self, pyutClass: PyutClass):

        displayDunderMethods:  PyutDisplayMethods = pyutClass.displayDunderMethods
        itemToggleConstructor: MenuItem           = self._toggleDunderMethods

        triStateData: TriStateData = self._getTriStateData(pyutDisplayValue=displayDunderMethods, displayName='Dunder Methods')

        # noinspection PyTypeChecker
        itemToggleConstructor.SetBitmap(triStateData.bitMap)
        itemToggleConstructor.SetItemLabel(triStateData.menuText)

    def _getTriStateData(self, pyutDisplayValue: PyutDisplayMethods, displayName: str) -> TriStateData:

        # noinspection PyUnreachableCode
        match pyutDisplayValue:

            case PyutDisplayMethods.UNSPECIFIED:
                return TriStateData(bitMap=UmlUtils.unspecifiedDisplayIcon(), menuText=f'Unspecified {displayName} Display')
            case PyutDisplayMethods.DISPLAY:
                return TriStateData(bitMap=UmlUtils.displayIcon(), menuText=f'Display {displayName}')
            case PyutDisplayMethods.DO_NOT_DISPLAY:
                return TriStateData(bitMap=UmlUtils.doNotDisplayIcon(), menuText=f'Do Not Display {displayName}')
            case _:
                self.logger.warning(f'Unknown Method Display type: {pyutDisplayValue}')
                assert False, 'Developer error'

    def _nextDisplayValue(self, pyutDisplayValue: PyutDisplayMethods) -> PyutDisplayMethods:

        # noinspection PyUnreachableCode
        match pyutDisplayValue:
            case PyutDisplayMethods.UNSPECIFIED:
                return PyutDisplayMethods.DISPLAY
            case PyutDisplayMethods.DISPLAY:
                return PyutDisplayMethods.DO_NOT_DISPLAY
            case PyutDisplayMethods.DO_NOT_DISPLAY:
                return PyutDisplayMethods.UNSPECIFIED
            case _:
                assert False, "Unknown method display type"

    def _getFrameId(self) -> FrameId:
        return self._getFrame().id

    def _getFrame(self) -> UmlFrame:
        umlFrame: UmlFrame = self._umlClass.umlFrame
        return umlFrame
