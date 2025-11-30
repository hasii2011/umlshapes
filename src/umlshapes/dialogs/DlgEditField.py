
from wx import CommandEvent
from wx import Window

from umlmodel.Field import Field
from umlmodel.FieldType import FieldType
from umlmodel.enumerations.Visibility import Visibility
from umlshapes.dialogs.BaseEditParamFieldDialog import BaseEditParamFieldDialog

from codeallybasic.SecureConversions import SecureConversions


class DlgEditField(BaseEditParamFieldDialog):

    def __init__(self, parent: Window, fieldToEdit: Field):
        super().__init__(parent, title='Edit Field', layoutField=True)
        """
        The Dialog to edit model fields
        Args:
            parent:
            fieldToEdit:  The parameter that is being edited
        """
        self._fieldToEdit: Field = fieldToEdit

        self._name.SetValue(self._fieldToEdit.name)
        self._type.SetValue(str(self._fieldToEdit.type))

        self._defaultValue.SetValue(SecureConversions.secureString(self._fieldToEdit.defaultValue))
        self._rdbVisibility.SetStringSelection(str(self._fieldToEdit.visibility))

        self._name.SetFocus()
        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

    # noinspection PyUnusedLocal
    def _onOk (self, event: CommandEvent):
        """
        Add additional behavior to super class method
        Args:
            event:  Associated event
        """
        nameValue: str = self._name.GetValue().strip()
        if nameValue == '':
            self._indicateEmptyTextCtrl(self._name)
            return  # will not end modal dialog

        self._fieldToEdit.name = nameValue

        self._fieldToEdit.type = FieldType(self._type.GetValue().strip())
        visStr: str            = self._rdbVisibility.GetStringSelection()
        vis:    Visibility     = Visibility.toEnum(visStr)
        self._fieldToEdit.visibility = vis

        if self._defaultValue.GetValue().strip() != "":
            self._fieldToEdit.defaultValue = self._defaultValue.GetValue().strip()
        else:
            self._fieldToEdit.defaultValue = ''

        super()._onOk(event)
