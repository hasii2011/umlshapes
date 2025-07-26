
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

from wx.lib.sized_controls import SizedPanel

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutParameter import PyutParameter

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.types.Common import UmlShapeList

if TYPE_CHECKING:
    from umlshapes.shapes.UmlClass import UmlClass

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

# noinspection SpellCheckingInspection
"""
from pyut.ui.eventengine.EventType import EventType
from pyut.ui.eventengine.IEventEngine import IEventEngine
"""


class DlgEditClass(DlgEditClassCommon):
    """
    Dialog for the class edits.

    Creating a DlgEditClass object will automatically open a dialog for class
    editing. The PyutClass given in the constructor parameters is used to fill the
    fields with the dialog, and is updated when the OK button is clicked.

    Dialogs for methods and fields editing are implemented in different dialog classes and
    created when invoking the _callDlgEditMethod and _callDlgEditField methods.

    Because the dialog works on a copy of the PyutClass object, if you cancel the
    dialog, any modifications are lost.

    """
    def __init__(self, parent: ClassDiagramFrame, eventEngine: IUmlPubSubEngine, pyutClass: PyutClass):
        """

        Args:
            parent:         dialog parent
            pyutClass:      Class modified by dialog
        """

        assert isinstance(parent, ClassDiagramFrame), 'Developer error.  Must be a Uml Diagram Frame'
        self._umlFrame:    ClassDiagramFrame = parent
        self.logger:       Logger               = getLogger(__name__)
        self._pyutClass:   PyutClass            = pyutClass

        super().__init__(parent=parent, eventEngine=eventEngine, dlgTitle="Edit Class", pyutModel=self._pyutClass, editInterface=False)
        self._oldClassName: str = pyutClass.name

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._pyutFields: EnhancedListBox = cast(EnhancedListBox, None)

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

        self._pyutFields = EnhancedListBox(parent=parent, title='Fields:', callbacks=callbacks)

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
            duplicate: PyutParameter = PyutParameter(name=parameter.name, type=parameter.type, defaultValue=parameter.defaultValue)
            dupParams.append(duplicate)
        return dupParams

    def _fillAllControls(self):
        """
        Fill all controls with _pyutModelCopy data.

        """
        # Fill Class name
        self._className.SetValue(self._pyutModelCopy.name)

        fieldItems: EnhancedListBoxItems = EnhancedListBoxItems([])
        for field in self._pyutModelCopy.fields:
            fieldItems.append(str(field))     # Depends on a reasonable __str__ implementation
        self._pyutFields.setItems(fieldItems)

        self._fillMethodList()

        # Fill display properties
        self._chkShowFields.SetValue(self._pyutModelCopy.showFields)
        self._chkShowMethods.SetValue(self._pyutModelCopy.showMethods)
        self._chkShowStereotype.SetValue(cast(PyutClass, self._pyutModelCopy).displayStereoType)

    def _fieldAddCallback(self) -> CallbackAnswer:
        # TODO Use default field name when available
        field:  PyutField      = PyutField(name='FieldName')
        answer: CallbackAnswer = CallbackAnswer()
        with DlgEditField(parent=self, fieldToEdit=field) as dlg:
            if dlg.ShowModal() == OK:
                answer.item  = str(field)
                answer.valid = True
                self._pyutModelCopy.fields.append(field)
            else:
                answer.valid = False
        return answer

    def _fieldEditCallback(self, selection: int) -> CallbackAnswer:

        field:  PyutField      = self._pyutModelCopy.fields[selection]
        answer: CallbackAnswer = CallbackAnswer()
        with DlgEditField(parent=self, fieldToEdit=field) as dlg:
            if dlg.ShowModal() == OK:
                answer.item  = str(field)
                answer.valid = True
            else:
                answer.valid = False
        return answer

    def _fieldRemoveCallback(self, selection: int):

        fields: List[PyutField] = self._pyutModelCopy.fields
        fields.pop(selection)

    def _fieldUpCallback(self, selection: int) -> UpCallbackData:

        fields: List[PyutField] = self._pyutModelCopy.fields
        field:   PyutField      = fields[selection]

        fields.pop(selection)
        fields.insert(selection - 1, field)

        upCallbackData: UpCallbackData = UpCallbackData()

        upCallbackData.previousItem = str(fields[selection-1])
        upCallbackData.currentItem  = str(fields[selection])

        return upCallbackData

    def _fieldDownCallback(self, selection: int) -> DownCallbackData:

        fields: List[PyutField] = self._pyutModelCopy.fields
        field:  PyutField       = fields[selection]
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
        self._pyutClass.stereotype = cast(PyutClass, self._pyutModelCopy).stereotype
        # Adds all fields in a list
        self._pyutClass.fields = self._pyutModelCopy.fields

        # Update display properties
        self._pyutClass.showFields        = self._chkShowFields.GetValue()
        self._pyutClass.showMethods       = self._chkShowMethods.GetValue()
        self._pyutClass.displayStereoType = self._chkShowStereotype.GetValue()

        #
        # Get common stuff from base class
        #
        self._pyutClass.name        = self._pyutModelCopy.name
        self._pyutClass.methods     = self._pyutModelCopy.methods
        self._pyutClass.fields      = self._pyutModelCopy.fields
        self._pyutClass.description = self._pyutModelCopy.description

        prefs: UmlPreferences = UmlPreferences()

        if prefs.autoResizeShapesOnEdit is True:
            umlClass: 'UmlClass' = self._getAssociatedOglClass(self._pyutClass)

            umlClass.autoSize()

        self._setProjectModified()

        # TODO:
        # if self._oldClassName != self._pyutClass.name:
        #     self._eventEngine.sendEvent(EventType.ClassNameChanged, oldClassName=self._oldClassName, newClassName=self._pyutClass.name)

        self.SetReturnCode(OK)
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onCancel(self, event: CommandEvent):
        self.SetReturnCode(CANCEL)
        self.EndModal(CANCEL)

    def _getAssociatedOglClass(self, pyutClass: PyutClass) -> 'UmlClass':
        """
        Return the OglClass that represents pyutClass

        Args:
            pyutClass:  Model class

        Returns:    The appropriate graphical class
        """
        from umlshapes.shapes.UmlClass import UmlClass

        oglClasses: List[UmlClass] = [po for po in self._getUmlShapes() if isinstance(po, UmlClass) and po.pyutClass is pyutClass]

        # This will pop in the TestADialog application since it has no frame
        assert len(oglClasses) == 1, 'Cannot have more then one ogl class per pyut class'
        return oglClasses.pop(0)

    def _getUmlShapes(self) -> UmlShapeList:
        """
        The frame may contain no UML shapes.

        Returns: Return the list of UmlShapes in the diagram.
        """
        return self._umlFrame.umlShapes
