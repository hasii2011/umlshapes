
from typing import cast
from typing import List

from logging import Logger
from logging import getLogger

from copy import deepcopy

from umlmodel.Interface import Interface
from umlmodel.Interface import Interfaces
from umlmodel.Interface import InterfacesDict
from umlmodel.ModelTypes import ClassName
from wx import OK
from wx import CANCEL
from wx import CB_DROPDOWN
from wx import CB_SORT
from wx import EVT_COMBOBOX
from wx import EVT_TEXT_ENTER
from wx import ID_ANY
from wx import TE_PROCESS_ENTER
from wx import EVT_TEXT

from wx import CommandEvent
from wx import Size
from wx import ComboBox

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlshapes.dialogs.umlclass.DlgEditClassCommon import DlgEditClassCommon

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface


class DlgEditInterface(DlgEditClassCommon):
    """
    Handles lollipop interfaces
    """

    clsLogger: Logger = getLogger(__name__)

    def __init__(self, parent, umlPubSubEngine: IUmlPubSubEngine, lollipopInterface: UmlLollipopInterface, interfaces: Interfaces, editMode: bool = False):
        """

        Args:
            parent:             parent window
            umlPubSubEngine:    the pub/sub engine
            lollipopInterface:  The created UmlLollipop interface
            interfaces:         The list of interfaces on the board
            editMode:           Set to true when we are editing, Not on initial creation
        """

        self._lollipopInterface:  UmlLollipopInterface = lollipopInterface
        self._modelInterface:     Interface        = lollipopInterface.modelInterface
        self._modelInterfaceCopy: Interface        = deepcopy(lollipopInterface.modelInterface)

        self._interfaces:     Interfaces     = interfaces
        self._interfacesDict: InterfacesDict = self._toDictionary(interfaces)

        self.editMode:     bool      = editMode
        self._implementor: ClassName = self._modelInterface.implementors[0]

        super().__init__(parent, umlPubSubEngine=umlPubSubEngine, dlgTitle='Edit Interface', commonClassType=self._modelInterfaceCopy, editInterface=True)

        self.logger: Logger = DlgEditInterface.clsLogger

        self._interfaceNameControl: ComboBox = cast(ComboBox, None)

        sizedPanel: SizedPanel = self.GetContentsPane()

        self._layoutInterfaceNameSelectionControl(parent=sizedPanel)
        self._layoutMethodControls(parent=sizedPanel)
        self._defineAdditionalDialogButtons(sizedPanel)

        self._fillMethodList()
        self.SetSize(Size(width=-1, height=300))

        self._modeInterfaceCopy: Interface = cast(Interface, None)

    @property
    def interface(self) -> Interface:
        return self._modelInterface

    def _layoutInterfaceNameSelectionControl(self, parent: SizedPanel):

        interfaceNameBox: SizedStaticBox = SizedStaticBox(parent=parent, label='Interface Name')
        interfaceNameBox.SetSizerProps(proportion=1)

        interfaceNames: List[str] = self._toInterfaceNames(self._interfaces)

        cb: ComboBox = ComboBox(parent=interfaceNameBox,
                                id=ID_ANY,
                                size=Size(200, -1),
                                choices=interfaceNames,
                                style=CB_DROPDOWN | TE_PROCESS_ENTER | CB_SORT
                                )
        if self.editMode is True:
            if len(self._modelInterfaceCopy.name) > 0:
                cb.SetValue(self._modelInterfaceCopy.name)
        else:
            cb.SetValue('')

        self._interfaceNameControl = cb

        self.Bind(EVT_COMBOBOX,   self._onInterfaceNameChanged,        cb)
        self.Bind(EVT_TEXT_ENTER, self._interfaceNameEnterKeyPressed,  cb)
        self.Bind(EVT_TEXT,       self._interfaceNameCharacterEntered, cb)

    def _defineAdditionalDialogButtons(self, parent: SizedPanel):
        """
        Override base class
        """
        self._defineDescriptionButton()
        self._layoutCustomDialogButtonContainer(parent=parent, customButtons=self._customDialogButtons)

    def _onInterfaceNameChanged(self, event: CommandEvent):
        """
        Selection has changed

        Args:
            event:
        """
        selectedInterfaceName: str = event.GetString()

        assert selectedInterfaceName in self._interfacesDict.keys(), 'Must be an existing interface'

        selectedInterface: Interface = self._interfacesDict[selectedInterfaceName]
        self.logger.debug(f'Selection Changed {selectedInterface.name=} {selectedInterface.id=}')

        self._modeInterfaceCopy = selectedInterface
        self._fillMethodList()

        event.Skip(True)

    def _interfaceNameEnterKeyPressed(self, event: CommandEvent):

        newInterfaceName: str = event.GetString()
        self.logger.info(f'_interfaceNameEnterKeyPressed: {newInterfaceName=}')
        self._modeInterfaceCopy.name = newInterfaceName
        event.Skip(False)

    # Capture events every time a user hits a key in the text entry field.
    def _interfaceNameCharacterEntered(self, event: CommandEvent):

        updatedInterfaceName: str = event.GetString()
        self.logger.debug(f'_interfaceNameCharacterEntered: {updatedInterfaceName=}')
        self._modeInterfaceCopy.name = updatedInterfaceName
        event.Skip()

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        Called when the Ok button is pressed;  Implement
        Args:
            event:
        """
        selectedInterfaceName: str            = self._modeInterfaceCopy.name
        interfacesDict:        InterfacesDict = self._interfacesDict
        if selectedInterfaceName in interfacesDict.keys():

            existingInterface: Interface = interfacesDict[selectedInterfaceName]
            self._modelInterface = existingInterface
            self._modelInterface.addImplementor(self._implementor)
            self.logger.debug(f'Using existing interface. {self._modelInterface.name=} {self._modelInterface.id=} {self._modelInterface.implementors}')
        else:
            # Get common stuff from base class
            #
            self._modelInterface.name        = self._modeInterfaceCopy.name
            self._modelInterface.methods     = self._modeInterfaceCopy.methods
            self._modelInterface.description = self._modeInterfaceCopy.description
            self.logger.debug(f'Using new interface. {self._modelInterface.name=} {self._modelInterface.id=}')

        self._lollipopInterface.modelInterface = self._modelInterface
        self.SetReturnCode(OK)
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onCancel(self, event: CommandEvent):
        self.SetReturnCode(CANCEL)
        self.EndModal(CANCEL)

    def _toInterfaceNames(self, interfaces: Interfaces) -> List[str]:

        interfacesNames: List[str] = []
        for interface in interfaces:
            interfacesNames.append(interface.name)
        return interfacesNames

    def _toDictionary(self, interfaces: Interfaces) -> InterfacesDict:

        interfacesDict: InterfacesDict = InterfacesDict({})

        for interface in interfaces:
            interfacesDict[interface.name] = interface

        return interfacesDict
