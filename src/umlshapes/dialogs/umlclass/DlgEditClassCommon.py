
from typing import List
from typing import cast
from typing import Union

from logging import Logger
from logging import getLogger

from copy import deepcopy

from umlmodel.Class import Class
from umlmodel.Interface import Interface
from umlmodel.Method import Method
from umlmodel.enumerations.Stereotype import Stereotype
from wx import OK
from wx import CommandEvent

from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog
from umlshapes.dialogs.BaseEditDialog import CustomDialogButton
from umlshapes.dialogs.BaseEditDialog import CustomDialogButtons

from umlshapes.dialogs.umlclass.DlgEditDescription import DlgEditDescription
from umlshapes.dialogs.umlclass.DlgEditMethod import DlgEditMethod
from umlshapes.dialogs.umlclass.DlgEditStereotype import DlgEditStereotype
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.enhancedlistbox.EnhancedListBox import EnhancedListBoxItems
from umlshapes.enhancedlistbox.EnhancedListBox import EnhancedListBox
from umlshapes.enhancedlistbox.AdvancedListCallbacks import AdvancedListCallbacks
from umlshapes.enhancedlistbox.CallbackAnswer import CallbackAnswer
from umlshapes.enhancedlistbox.DownCallbackData import DownCallbackData
from umlshapes.enhancedlistbox.UpCallbackData import UpCallbackData

CommonClassType = Union[Class, Interface]


class DlgEditClassCommon(BaseEditDialog):
    """
    This parent class is responsible for the comment attributes that Classes and Interfaces share.

    These are
        * Description
        * Methods
    This class creates deep copies of the input model class

    Subclasses need to override the `onOk` and `onCancel` handlers

    `onOk` the subclasses should retrieve the common attributes from _modelCopy
    `onCancel` the subclasses should restore the common attributes from _Model

    A big ask here is that the parent class that is provided for the UI is the actual
    frame on which we are editing.
    """
    def __init__(self, parent: ClassDiagramFrame, umlPubSubEngine: IUmlPubSubEngine, dlgTitle: str, commonClassType: CommonClassType, editInterface: bool = False):
        """

        Args:
            parent:
            umlPubSubEngine:
            dlgTitle:
            commonClassType:
            editInterface:
        """

        super().__init__(parent, dlgTitle)

        self._parent = parent   #

        self._umlFrame: ClassDiagramFrame = parent  # another moniker

        assert isinstance(self._umlFrame, ClassDiagramFrame), 'Developer error,  must be a class diagram frame'

        self.ccLogger:         Logger           = getLogger(__name__)
        self._editInterface:   bool             = editInterface
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self._model:             CommonClassType = commonClassType
        self._modeInterfaceCopy: CommonClassType = deepcopy(commonClassType)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')

        self._methods: EnhancedListBox = cast(EnhancedListBox, None)

        self._customDialogButtons: CustomDialogButtons = CustomDialogButtons([])

    def _defineAdditionalDialogButtons(self, parent: SizedPanel):
        """
        Create Ok, Cancel, stereotype and description buttons;
        since we want to use a custom button layout, we won't use the
        CreateStdDialogBtnSizer here, we'll just create our own panel with
        a horizontal layout and add the buttons to that;
        """

        self._defineStereoTypeButton()
        self._defineDescriptionButton()
        self._layoutCustomDialogButtonContainer(parent=parent, customButtons=self._customDialogButtons)

    def _defineStereoTypeButton(self):

        stereotypeDialogButton: CustomDialogButton = CustomDialogButton()
        stereotypeDialogButton.label    = '&Stereotype...'
        stereotypeDialogButton.callback = self._onStereotype

        self._customDialogButtons.append(stereotypeDialogButton)

    def _defineDescriptionButton(self):

        descriptionDialogButton: CustomDialogButton = CustomDialogButton()
        descriptionDialogButton.label    = '&Description...'
        descriptionDialogButton.callback = self._onDescription

        self._customDialogButtons.append(descriptionDialogButton)

    def _layoutMethodControls(self, parent: SizedPanel):

        callbacks: AdvancedListCallbacks = AdvancedListCallbacks()
        callbacks.addCallback    = self._methodAddCallback
        callbacks.editCallback   = self._methodEditCallback
        callbacks.removeCallback = self._methodRemoveCallback
        callbacks.upCallback     = self._methodUpCallback
        callbacks.downCallback   = self._methodDownCallback

        self._methods = EnhancedListBox(parent=parent, title='Methods:', callbacks=callbacks)

    def _fillMethodList(self):

        methodItems: EnhancedListBoxItems = EnhancedListBoxItems([])

        for method in self._modeInterfaceCopy.methods:
            methodItems.append(str(method))

        self._methods.setItems(methodItems)

    def _onNameChange(self, event):
        self._modeInterfaceCopy.name = event.GetString()

    # noinspection PyUnusedLocal
    def _onDescription(self, event: CommandEvent):
        """
        Called when the class description button is pressed.
        Args:
            event:
        """
        with DlgEditDescription(self, model=self._modeInterfaceCopy) as dlg:
            if dlg.ShowModal() == OK:
                # self._eventEngine.sendEvent(EventType.UMLDiagramModified)
                self._modeInterfaceCopy.description = dlg.description
            else:
                self._modeInterfaceCopy.description = self._model.description

    def _methodEditCallback(self, selection: int):
        """
        Edit a method.
        """
        method: Method = self._modeInterfaceCopy.methods[selection]

        return self._editMethod(method=method)

    def _methodAddCallback(self) -> CallbackAnswer:
        """
        """
        method: Method     = Method(name=UmlPreferences().defaultNameMethod)
        answer: CallbackAnswer = self._editMethod(method=method)
        if answer.valid is True:
            self._modeInterfaceCopy.methods.append(method)

        return answer

    def _editMethod(self, method: Method) -> CallbackAnswer:
        """
        Common method to edit either new or old method
        Args:
            method:
        """
        self.ccLogger.info(f'method to edit: {method}')

        answer: CallbackAnswer = CallbackAnswer()

        with DlgEditMethod(parent=self, method=method, editInterface=self._editInterface) as dlg:
            if dlg.ShowModal() == OK:
                answer.item = str(method)
                answer.valid = True
            else:
                answer.valid = False

        return answer

    def _methodRemoveCallback(self, selection: int):

        # Remove from _modelCopy
        methods: List[Method] = self._modeInterfaceCopy.methods
        methods.pop(selection)

    def _methodUpCallback(self, selection: int) -> UpCallbackData:
        """
        Move up a method in the list.
        """
        methods: List[Method] = self._modeInterfaceCopy.methods
        method:  Method       = methods[selection]
        methods.pop(selection)
        methods.insert(selection-1, method)

        upCallbackData: UpCallbackData = UpCallbackData()

        upCallbackData.previousItem = str(methods[selection-1])
        upCallbackData.currentItem  = str(methods[selection])

        return upCallbackData

    def _methodDownCallback(self, selection: int) -> DownCallbackData:
        """
        Move down a method in the list.
        """
        methods: List[Method] = self._modeInterfaceCopy.methods
        method:  Method       = methods[selection]

        methods.pop(selection)
        methods.insert(selection+1, method)

        downCallbackData: DownCallbackData = DownCallbackData()
        downCallbackData.currentItem = str(methods[selection])
        downCallbackData.nextItem    = str(methods[selection+1])

        return downCallbackData

    # noinspection PyUnusedLocal
    def _onStereotype(self, event: CommandEvent):
        """
        Args:
            event:
        """
        stereotype: Stereotype = cast(Class, self._modeInterfaceCopy).stereotype

        with DlgEditStereotype(parent=self._parent, stereotype=stereotype) as dlg:
            if dlg.ShowModal() == OK:
                cast(Class, self._modeInterfaceCopy).stereotype = dlg.value

    def _indicateFrameModified(self):
        """
        """
        self._umlFrame.frameModified = True
        self._umlPubSubEngine.sendMessage(UmlMessageType.FRAME_MODIFIED, frameId=self._umlFrame.id, modifiedFrameId=self._umlFrame.id)
