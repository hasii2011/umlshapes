from copy import deepcopy
from typing import List
from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Button
from wx import Choice
from wx import CommandEvent
from wx import EVT_BUTTON
from wx import EVT_CHOICE
from wx import EVT_LISTBOX
from wx import EVT_TEXT
from wx import ID_ANY
from wx import ID_OK
from wx import LB_SINGLE
from wx import ListBox
from wx import Size
from wx import StaticText
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog
from umlshapes.sd.SDFragmentOperator import SDFragmentOperator
from umlshapes.sd.SDInteractionOperand import SDInteractionOperand
from umlshapes.sd.SDInteractionOperand import SDInteractionOperands

MIN_DIALOG_WIDTH:  int = 380
MIN_DIALOG_HEIGHT: int = 340
LIST_BOX_MIN_WIDTH: int = 240
LIST_BOX_MIN_HEIGHT: int = 120


class DlgEditCombinedFragment(BaseEditDialog):
    """
    Modal dialog to edit sequence diagram combined fragment operators and interaction operands.
    """

    def __init__(
        self,
        parent: Window,
        operator: SDFragmentOperator,
        operands: SDInteractionOperands
    ):
        """
        Initialize the combined fragment edit dialog.

        Args:
            parent:   Parent window.
            operator: Current combined fragment operator.
            operands: List of interaction operands with guard conditions.
        """
        super().__init__(parent=parent, title='Edit Combined Fragment')

        self.logger: Logger = getLogger(__name__)

        self._operands: SDInteractionOperands = deepcopy(operands)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')

        self._layoutOperatorRow(parent=sizedPanel, initialOperator=operator)
        self._layoutOperandsGroup(parent=sizedPanel)

        self._bindEventHandlers()

        self._populateOperandListBox(selectedIndex=0)

        self._layoutStandardOkCancelButtonSizer()
        okBtn: Optional[Window] = self.FindWindow(ID_OK)
        if okBtn is not None:
            cast(Button, okBtn).SetDefault()

        self.Fit()
        currentSize: Size = self.GetSize()
        dialogWidth: int = max(currentSize.GetWidth(), MIN_DIALOG_WIDTH)
        dialogHeight: int = max(currentSize.GetHeight(), MIN_DIALOG_HEIGHT)
        self.SetSize(Size(dialogWidth, dialogHeight))
        self.SetMinSize(Size(MIN_DIALOG_WIDTH, MIN_DIALOG_HEIGHT))
        self.Centre()

    @property
    def operator(self) -> SDFragmentOperator:
        """
        The dialog invoker accesses this property to retrieve the updated operator.

        Returns:
            The selected SDFragmentOperator enum value.
        """
        selectedOperatorString: str = self._operatorChoice.GetStringSelection()
        return SDFragmentOperator(selectedOperatorString)

    @property
    def operands(self) -> SDInteractionOperands:
        """
        The dialog invoker accesses this property to retrieve the updated operands.

        Returns:
            Deep copy of the updated interaction operands.
        """
        return deepcopy(self._operands)

    def _layoutOperatorRow(self, parent: SizedPanel, initialOperator: SDFragmentOperator):
        operatorRow: SizedPanel = SizedPanel(parent=parent)
        operatorRow.SetSizerType('horizontal')
        operatorRow.SetSizerProps(expand=True)

        operatorLabel: StaticText = StaticText(parent=operatorRow, label='Operator:')
        operatorLabel.SetSizerProps(valign='center')

        operatorChoices: List[str] = [op.value for op in SDFragmentOperator]
        self._operatorChoice: Choice = Choice(
            parent=operatorRow,
            id=ID_ANY,
            choices=operatorChoices
        )
        self._operatorChoice.SetStringSelection(initialOperator.value)
        self._operatorChoice.SetSizerProps(expand=False, proportion=1, valign='center')

    def _layoutOperandsGroup(self, parent: SizedPanel):
        operandsBox: SizedStaticBox = SizedStaticBox(parent=parent, label='Interaction Operands')
        operandsBox.SetSizerType('vertical')
        operandsBox.SetSizerProps(expand=True, proportion=1)

        listAndButtonsRow: SizedPanel = SizedPanel(parent=operandsBox)
        listAndButtonsRow.SetSizerType('horizontal')
        listAndButtonsRow.SetSizerProps(expand=True, proportion=1)

        self._operandListBox: ListBox = ListBox(
            parent=listAndButtonsRow,
            id=ID_ANY,
            choices=[],
            style=LB_SINGLE
        )
        self._operandListBox.SetMinSize(Size(LIST_BOX_MIN_WIDTH, LIST_BOX_MIN_HEIGHT))
        self._operandListBox.SetSizerProps(expand=True, proportion=1)

        btnPanel: SizedPanel = SizedPanel(parent=listAndButtonsRow)
        btnPanel.SetSizerType('vertical')
        btnPanel.SetSizerProps(expand=False)

        self._btnAdd: Button = Button(parent=btnPanel, id=ID_ANY, label='&Add')
        self._btnAdd.SetSizerProps(expand=True)

        self._btnRemove: Button = Button(parent=btnPanel, id=ID_ANY, label='&Remove')
        self._btnRemove.SetSizerProps(expand=True)

        self._btnUp: Button = Button(parent=btnPanel, id=ID_ANY, label='&Up')
        self._btnUp.SetSizerProps(expand=True)

        self._btnDown: Button = Button(parent=btnPanel, id=ID_ANY, label='&Down')
        self._btnDown.SetSizerProps(expand=True)

        guardRow: SizedPanel = SizedPanel(parent=operandsBox)
        guardRow.SetSizerType('horizontal')
        guardRow.SetSizerProps(expand=True)

        guardLabel: StaticText = StaticText(parent=guardRow, label='Guard:')
        guardLabel.SetSizerProps(valign='center')

        self._guardTextCtrl: TextCtrl = TextCtrl(parent=guardRow, id=ID_ANY)
        self._guardTextCtrl.SetSizerProps(expand=True, proportion=1, valign='center')

    def _bindEventHandlers(self):

        self.Bind(EVT_CHOICE, self._onOperatorChanged, self._operatorChoice)
        self.Bind(EVT_LISTBOX, self._onOperandSelected, self._operandListBox)
        self.Bind(EVT_TEXT, self._onGuardTextChanged, self._guardTextCtrl)
        self.Bind(EVT_BUTTON, self._onAddOperand, self._btnAdd)
        self.Bind(EVT_BUTTON, self._onRemoveOperand, self._btnRemove)
        self.Bind(EVT_BUTTON, self._onUpOperand, self._btnUp)
        self.Bind(EVT_BUTTON, self._onDownOperand, self._btnDown)

    def _formatOperandLabel(self, index: int, operand: SDInteractionOperand) -> str:
        guardText: str = operand.guard.strip()
        if guardText == '':
            return f'[{index}]'
        if guardText.startswith('[') and guardText.endswith(']'):
            return f'[{index}] {guardText}'
        return f'[{index}] [{guardText}]'

    def _populateOperandListBox(self, selectedIndex: int = 0):
        self._operandListBox.Clear()
        for idx, op in enumerate(self._operands):
            self._operandListBox.Append(self._formatOperandLabel(idx, op))

        if len(self._operands) > 0:
            validIndex: int = max(0, min(selectedIndex, len(self._operands) - 1))
            self._operandListBox.SetSelection(validIndex)
            self._guardTextCtrl.ChangeValue(self._operands[validIndex].guard)
        else:
            self._guardTextCtrl.ChangeValue('')

        self._updateButtonStates()

    def _updateButtonStates(self):

        selectedIndex: int = self._operandListBox.GetSelection()
        hasValidSelection: bool = False
        if selectedIndex != -1:
            if len(self._operands) > 0:
                hasValidSelection = True

        if hasValidSelection:
            self._btnRemove.Enable(True)
            self._guardTextCtrl.Enable(True)
            if selectedIndex > 0:
                self._btnUp.Enable(True)
            else:
                self._btnUp.Enable(False)

            if selectedIndex < len(self._operands) - 1:
                self._btnDown.Enable(True)
            else:
                self._btnDown.Enable(False)
        else:
            self._btnRemove.Enable(False)
            self._btnUp.Enable(False)
            self._btnDown.Enable(False)
            self._guardTextCtrl.Enable(False)

    def _onOperatorChanged(self, event: CommandEvent):
        operatorString: str = event.GetString()
        self.logger.debug(f'Operator changed to: {operatorString}')
        event.Skip()

    def _onOperandSelected(self, event: CommandEvent):
        selectedIndex: int = self._operandListBox.GetSelection()
        if 0 <= selectedIndex < len(self._operands):
            self._guardTextCtrl.ChangeValue(self._operands[selectedIndex].guard)
        self._updateButtonStates()
        event.Skip()

    def _onGuardTextChanged(self, event: CommandEvent):
        selectedIndex: int = self._operandListBox.GetSelection()
        if 0 <= selectedIndex < len(self._operands):
            newGuard: str = self._guardTextCtrl.GetValue()
            self._operands[selectedIndex].guard = newGuard
            self._operandListBox.SetString(
                selectedIndex,
                self._formatOperandLabel(selectedIndex, self._operands[selectedIndex])
            )
        event.Skip()

    def _onAddOperand(self, _event: CommandEvent):

        newOperand: SDInteractionOperand = SDInteractionOperand(guard='')
        self._operands.append(newOperand)
        newIndex: int = len(self._operands) - 1
        self._populateOperandListBox(selectedIndex=newIndex)
        self._guardTextCtrl.SetFocus()

    def _onRemoveOperand(self, _event: CommandEvent):

        selectedIndex: int = self._operandListBox.GetSelection()
        if 0 <= selectedIndex < len(self._operands):
            del self._operands[selectedIndex]
            newIndex: int = min(selectedIndex, len(self._operands) - 1)
            self._populateOperandListBox(selectedIndex=newIndex)

    def _onUpOperand(self, _event: CommandEvent):

        selectedIndex: int = self._operandListBox.GetSelection()
        if selectedIndex > 0:
            operandToMove: SDInteractionOperand = self._operands.pop(selectedIndex)
            self._operands.insert(selectedIndex - 1, operandToMove)
            self._populateOperandListBox(selectedIndex=selectedIndex - 1)

    def _onDownOperand(self, _event: CommandEvent):

        selectedIndex: int = self._operandListBox.GetSelection()
        if 0 <= selectedIndex < len(self._operands) - 1:
            operandToMove: SDInteractionOperand = self._operands.pop(selectedIndex)
            self._operands.insert(selectedIndex + 1, operandToMove)
            self._populateOperandListBox(selectedIndex=selectedIndex + 1)
