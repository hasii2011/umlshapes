
from typing import List
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CANCEL
from wx import EVT_TEXT
from wx import OK

from wx import CommandEvent
from wx import Size
from wx import StaticText
from wx import TextCtrl
from wx import CheckBox

from umlmodel.Class import Class
from umlmodel.Field import Field
from umlmodel.Parameter import Parameter

from wx.lib.sized_controls import SizedPanel

from umlshapes.ShapeTypes import UmlShapes

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.dialogs.umlclass.DlgEditClassCommon import DlgEditClassCommon
from umlshapes.dialogs.DlgEditField import DlgEditField

from umlshapes.enhancedlistbox.AdvancedListCallbacks import AdvancedListCallbacks
from umlshapes.enhancedlistbox.CallbackAnswer import CallbackAnswer
from umlshapes.enhancedlistbox.DownCallbackData import DownCallbackData
from umlshapes.enhancedlistbox.EnhancedListBox import EnhancedListBox
from umlshapes.enhancedlistbox.EnhancedListBoxItems import EnhancedListBoxItems
from umlshapes.enhancedlistbox.UpCallbackData import UpCallbackData

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.preferences.UmlPreferences import UmlPreferences

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass


class DlgEditClass(DlgEditClassCommon):
    """
    Dialog for the class edits.

    Creating a DlgEditClass object will automatically open a dialog for class
    editing. The Class given in the constructor parameters is used to fill the
    fields with the dialog, and is updated when the OK button is clicked.

    Dialogs for methods and fields editing are implemented in different dialog classes and
    created when invoking the _callDlgEditMethod and _callDlgEditField methods.

    Because the dialog works on a copy of the Class object, if you cancel the
    dialog, any modifications are lost.

    """
    def __init__(self, parent: ClassDiagramFrame, umlPubSubEngine: IUmlPubSubEngine, modelClass: Class):
        """

        Args:
            parent:         dialog parent
            modelClass:      Class modified by dialog
        """

        assert isinstance(parent, ClassDiagramFrame), 'Developer error.  Must be a Uml Diagram Frame'

        self.logger:      Logger = getLogger(__name__)
        self._modelClass: Class  = modelClass

        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine, dlgTitle="Edit Class", commonClassType=self._modelClass, editInterface=False)
        self._oldClassName: str = modelClass.name

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._enhancedListBox: EnhancedListBox = cast(EnhancedListBox, None)

        self._layoutNameControls(parent=sizedPanel)

        self._layoutFieldControls(parent=sizedPanel)
        self._layoutMethodControls(parent=sizedPanel)
        self._layoutMethodDisplayOptions(parent=sizedPanel)

        self._fillAllControls()

        self._className.SetFocus()
        self._className.SetSelection(0, len(self._className.GetValue()))
        self._defineAdditionalDialogButtons(sizedPanel)
        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

    def _layoutNameControls(self, parent: SizedPanel):

        lbl: str = 'Class Name:'

        namePanel: SizedPanel = SizedPanel(parent)
        namePanel.SetSizerType('horizontal')

        StaticText(namePanel, label=lbl)
        self._className: TextCtrl = TextCtrl(namePanel, value='', size=Size(250, -1))  #

        self.Bind(EVT_TEXT, self._onNameChange, self._className)

    def _layoutFieldControls(self, parent: SizedPanel):

        callbacks: AdvancedListCallbacks = AdvancedListCallbacks()
        callbacks.addCallback    = self._fieldAddCallback
        callbacks.editCallback   = self._fieldEditCallback
        callbacks.removeCallback = self._fieldRemoveCallback
        callbacks.upCallback     = self._fieldUpCallback
        callbacks.downCallback   = self._fieldDownCallback

        self._enhancedListBox = EnhancedListBox(parent=parent, title='Fields:', callbacks=callbacks)

    def _layoutMethodDisplayOptions(self, parent: SizedPanel):

        buttonPanel: SizedPanel = SizedPanel(parent)
        buttonPanel.SetSizerType('horizontal')

        self._chkShowStereotype: CheckBox = CheckBox(buttonPanel, label='Show stereotype')
        self._chkShowFields:     CheckBox = CheckBox(buttonPanel, label='Show fields')
        self._chkShowMethods:    CheckBox = CheckBox(buttonPanel, label='Show methods')

    def _duplicateParameters(self, parameters):
        """
        Duplicate the list of param
        """
        dupParams = []
        for parameter in parameters:
            duplicate: Parameter = Parameter(name=parameter.name, type=parameter.type, defaultValue=parameter.defaultValue)
            dupParams.append(duplicate)
        return dupParams

    def _fillAllControls(self):
        """
        Fill all controls with _modelCopy data.

        """
        # Fill Class name
        self._className.SetValue(self._modeInterfaceCopy.name)

        fieldItems: EnhancedListBoxItems = EnhancedListBoxItems([])
        for field in self._modeInterfaceCopy.fields:
            fieldItems.append(str(field))     # Depends on a reasonable __str__ implementation
        self._enhancedListBox.setItems(fieldItems)

        self._fillMethodList()

        # Fill display properties
        self._chkShowFields.SetValue(self._modeInterfaceCopy.showFields)
        self._chkShowMethods.SetValue(self._modeInterfaceCopy.showMethods)
        self._chkShowStereotype.SetValue(cast(Class, self._modeInterfaceCopy).displayStereoType)

    def _fieldAddCallback(self) -> CallbackAnswer:
        # TODO Use default field name when available
        field:  Field          = Field(name='FieldName')
        answer: CallbackAnswer = CallbackAnswer()
        with DlgEditField(parent=self, fieldToEdit=field) as dlg:
            if dlg.ShowModal() == OK:
                answer.item  = str(field)
                answer.valid = True
                self._modeInterfaceCopy.fields.append(field)
            else:
                answer.valid = False
        return answer

    def _fieldEditCallback(self, selection: int) -> CallbackAnswer:

        field:  Field          = self._modeInterfaceCopy.fields[selection]
        answer: CallbackAnswer = CallbackAnswer()
        with DlgEditField(parent=self, fieldToEdit=field) as dlg:
            if dlg.ShowModal() == OK:
                answer.item  = str(field)
                answer.valid = True
            else:
                answer.valid = False
        return answer

    def _fieldRemoveCallback(self, selection: int):

        fields: List[Field] = self._modeInterfaceCopy.fields
        fields.pop(selection)

    def _fieldUpCallback(self, selection: int) -> UpCallbackData:

        fields: List[Field] = self._modeInterfaceCopy.fields
        field:  Field       = fields[selection]

        fields.pop(selection)
        fields.insert(selection - 1, field)

        upCallbackData: UpCallbackData = UpCallbackData()

        upCallbackData.previousItem = str(fields[selection-1])
        upCallbackData.currentItem  = str(fields[selection])

        return upCallbackData

    def _fieldDownCallback(self, selection: int) -> DownCallbackData:

        fields: List[Field] = self._modeInterfaceCopy.fields
        field:  Field       = fields[selection]
        fields.pop(selection)
        fields.insert(selection + 1, field)

        downCallbackData: DownCallbackData = DownCallbackData()
        downCallbackData.nextItem    = str(fields[selection+1])
        downCallbackData.currentItem = str(fields[selection])

        return downCallbackData

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        Activated when button OK is clicked.
        """
        self._modelClass.stereotype = cast(Class, self._modeInterfaceCopy).stereotype
        # Adds all fields in a list
        self._modelClass.fields = self._modeInterfaceCopy.fields

        # Update display properties
        self._modelClass.showFields        = self._chkShowFields.GetValue()
        self._modelClass.showMethods       = self._chkShowMethods.GetValue()
        self._modelClass.displayStereoType = self._chkShowStereotype.GetValue()

        #
        # Get common stuff from base class
        #
        self._modelClass.name        = self._modeInterfaceCopy.name
        self._modelClass.methods     = self._modeInterfaceCopy.methods
        self._modelClass.fields      = self._modeInterfaceCopy.fields
        self._modelClass.description = self._modeInterfaceCopy.description

        prefs: UmlPreferences = UmlPreferences()

        if prefs.autoResizeShapesOnEdit is True:
            umlClass: 'UmlClass' = self._getAssociatedUmlClass(self._modelClass)

            umlClass.autoSize()

        self._indicateFrameModified()

        # TODO:
        # if self._oldClassName != self._class.name:
        #     self._eventEngine.sendEvent(EventType.ClassNameChanged, oldClassName=self._oldClassName, newClassName=self._class.name)

        self.SetReturnCode(OK)
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onCancel(self, event: CommandEvent):
        self.SetReturnCode(CANCEL)
        self.EndModal(CANCEL)

    def _getAssociatedUmlClass(self, modelClass: Class) -> 'UmlClass':
        """
        Return the UmlClass that represents model Class

        Args:
            modelClass:  Model class

        Returns:    The appropriate graphical class
        """
        from umlshapes.shapes.UmlClass import UmlClass

        umlClasses: List[UmlClass] = [po for po in self._getUmlShapes() if isinstance(po, UmlClass) and po.modelClass is modelClass]

        # This will pop in the TestADialog application since it has no frame
        assert len(umlClasses) == 1, 'Cannot have more then one UML Class per model class'

        return umlClasses.pop(0)

    def _getUmlShapes(self) -> UmlShapes:
        """
        The frame may contain no UML shapes.

        Returns: Return the list of UmlShapes in the diagram.
        """
        return self._umlFrame.umlShapes
