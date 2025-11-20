
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from copy import deepcopy

from wx import ID_ANY

from wx import CommandEvent
from wx import Point
from wx import Size

from wx.adv import EL_ALLOW_DELETE
from wx.adv import EL_ALLOW_EDIT
from wx.adv import EL_ALLOW_NEW
from wx.adv import EL_DEFAULT_STYLE
from wx.adv import EditableListBox

from wx.lib.sized_controls import SizedPanel

from umlmodel.Method import Modifiers
from umlmodel.Modifier import Modifier

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog


class DlgEditMethodModifiers(BaseEditDialog):

    def __init__(self, parent, pyutModifiers: Modifiers):

        super().__init__(parent, title='Edit Method Modifiers')

        self.logger:             Logger     = getLogger(__name__)
        self._modelModifiers:     Modifiers = pyutModifiers
        self._modelModifiersCopy: Modifiers = deepcopy(pyutModifiers)

        self._elb: EditableListBox = cast(EditableListBox, None)
        sizedPanel: SizedPanel = self.GetContentsPane()

        self._layoutEditableListBox(sizedPanel)
        self._layoutStandardOkCancelButtonSizer()

    @property
    def modifiers(self) -> Modifiers:
        return self._stringToPyutModifiers()

    def _layoutEditableListBox(self, parent: SizedPanel):
        style: int = EL_DEFAULT_STYLE | EL_ALLOW_NEW | EL_ALLOW_EDIT | EL_ALLOW_DELETE
        self._elb = EditableListBox(parent, ID_ANY, "Modifiers", Point(-1, -1), Size(-1, -1), style=style)

        self._elb.SetStrings(self._pyutModifiersToStrings())

    def _onOk(self, event: CommandEvent):
        """
        """

        super()._onOk(event)

    def _pyutModifiersToStrings(self) -> List[str]:
        """
        Converts the copy of the modifiers to a list of string
        Returns:
        """

        stringList: List[str] = []
        for pyutModifier in self._modelModifiersCopy:
            stringList.append(pyutModifier.name)

        return stringList

    def _stringToPyutModifiers(self) -> Modifiers:

        pyutModifiers: Modifiers = Modifiers([])
        strList:       List[str]     = self._elb.GetStrings()
        for modifierString in strList:
            pyutModifier: Modifier = Modifier(name=modifierString)
            pyutModifiers.append(pyutModifier)

        return pyutModifiers
