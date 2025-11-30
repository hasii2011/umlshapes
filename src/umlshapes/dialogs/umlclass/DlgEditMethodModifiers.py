
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

    def __init__(self, parent, modifiers: Modifiers):

        super().__init__(parent, title='Edit Method Modifiers')

        self.logger:             Logger     = getLogger(__name__)
        self._modelModifiers:     Modifiers = modifiers
        self._modelModifiersCopy: Modifiers = deepcopy(modifiers)

        self._elb: EditableListBox = cast(EditableListBox, None)
        sizedPanel: SizedPanel = self.GetContentsPane()

        self._layoutEditableListBox(sizedPanel)
        self._layoutStandardOkCancelButtonSizer()

    @property
    def modifiers(self) -> Modifiers:
        return self._stringToModifiers()

    def _layoutEditableListBox(self, parent: SizedPanel):
        style: int = EL_DEFAULT_STYLE | EL_ALLOW_NEW | EL_ALLOW_EDIT | EL_ALLOW_DELETE
        self._elb = EditableListBox(parent, ID_ANY, "Modifiers", Point(-1, -1), Size(-1, -1), style=style)

        self._elb.SetStrings(self._modifiersToStrings())

    def _onOk(self, event: CommandEvent):
        """
        """

        super()._onOk(event)

    def _modifiersToStrings(self) -> List[str]:
        """
        Converts the copy of the modifiers to a list of string
        Returns:
        """

        stringList: List[str] = []
        for modifier in self._modelModifiersCopy:
            stringList.append(modifier.name)

        return stringList

    def _stringToModifiers(self) -> Modifiers:

        modifiers: Modifiers = Modifiers([])
        strList:       List[str]     = self._elb.GetStrings()
        for modifierString in strList:
            modifier: Modifier = Modifier(name=modifierString)
            modifiers.append(modifier)

        return modifiers
