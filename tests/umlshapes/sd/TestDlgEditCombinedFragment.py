
from typing import Optional

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import CommandEvent
from wx import ID_CANCEL
from wx import ID_OK
from wx import Window

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlshapes.dialogs.DlgEditCombinedFragment import DlgEditCombinedFragment
from umlshapes.sd.SDFragmentOperator import SDFragmentOperator
from umlshapes.sd.SDInteractionOperand import SDInteractionOperand
from umlshapes.sd.SDInteractionOperand import SDInteractionOperands

SAMPLE_GUARD_1: str = 'x > 0'
SAMPLE_GUARD_2: str = 'else'
SAMPLE_GUARD_3: str = 'x > 100'


class TestDlgEditCombinedFragment(UnitTestBaseW):
    """
    Unit tests for DlgEditCombinedFragment dialog.
    """

    def setUp(self):
        super().setUp()
        self._operands: SDInteractionOperands = SDInteractionOperands([
            SDInteractionOperand(guard=SAMPLE_GUARD_1, startTimeStep=1, endTimeStep=2),
            SDInteractionOperand(guard=SAMPLE_GUARD_2, startTimeStep=2, endTimeStep=3)
        ])

    def testDlgEditCombinedFragmentInitialization(self):
        """
        Verify that DlgEditCombinedFragment initializes with the correct operator, operands, and title.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.ALT,
            operands=self._operands
        ) as dlg:
            self.assertEqual(dlg.GetTitle(), 'Edit Combined Fragment')
            self.assertEqual(dlg.operator, SDFragmentOperator.ALT)
            self.assertEqual(len(dlg.operands), 2)
            self.assertEqual(dlg.operands[0].guard, SAMPLE_GUARD_1)
            self.assertEqual(dlg.operands[1].guard, SAMPLE_GUARD_2)
            self.assertIsNot(dlg.operands, self._operands)
            self.assertEqual(dlg._operandListBox.GetCount(), 2)
            self.assertEqual(dlg._operandListBox.GetString(0), f'[0] [{SAMPLE_GUARD_1}]')
            self.assertEqual(dlg._operandListBox.GetString(1), f'[1] [{SAMPLE_GUARD_2}]')
            self.assertEqual(dlg._operandListBox.GetSelection(), 0)
            self.assertEqual(dlg._guardTextCtrl.GetValue(), SAMPLE_GUARD_1)
            self.assertFalse(dlg._btnUp.IsEnabled())
            self.assertTrue(dlg._btnDown.IsEnabled())
            self.assertTrue(dlg._btnRemove.IsEnabled())

    def testDlgEditCombinedFragmentEscapeIdAndDefaultButton(self):
        """
        Verify that DlgEditCombinedFragment configures EscapeId to ID_CANCEL and OK as default button.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.LOOP,
            operands=self._operands
        ) as dlg:
            self.assertEqual(dlg.GetEscapeId(), ID_CANCEL)
            okBtn: Optional[Window] = dlg.FindWindow(ID_OK)
            self.assertIsNotNone(okBtn)
            self.assertIs(dlg.GetDefaultItem(), okBtn)

    def testDlgEditCombinedFragmentOperatorSelection(self):
        """
        Verify that selecting a different operator updates the operator property.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.OPT,
            operands=self._operands
        ) as dlg:
            self.assertEqual(dlg.operator, SDFragmentOperator.OPT)

            dlg._operatorChoice.SetStringSelection(SDFragmentOperator.PAR.value)
            dummyEvent: CommandEvent = CommandEvent()
            dummyEvent.SetString(SDFragmentOperator.PAR.value)
            dlg._onOperatorChanged(dummyEvent)

            self.assertEqual(dlg.operator, SDFragmentOperator.PAR)

    def testDlgEditCombinedFragmentOperandSelectionUpdatesGuard(self):
        """
        Verify that selecting an operand updates the guard text control and button states.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.ALT,
            operands=self._operands
        ) as dlg:
            dlg._operandListBox.SetSelection(1)
            dummyEvent: CommandEvent = CommandEvent()
            dlg._onOperandSelected(dummyEvent)

            self.assertEqual(dlg._guardTextCtrl.GetValue(), SAMPLE_GUARD_2)
            self.assertTrue(dlg._btnUp.IsEnabled())
            self.assertFalse(dlg._btnDown.IsEnabled())

    def testDlgEditCombinedFragmentGuardTextEditing(self):
        """
        Verify that editing the guard text field updates the operand model and list display.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.ALT,
            operands=self._operands
        ) as dlg:
            dlg._guardTextCtrl.SetValue(SAMPLE_GUARD_3)
            dummyEvent: CommandEvent = CommandEvent()
            dlg._onGuardTextChanged(dummyEvent)

            self.assertEqual(dlg.operands[0].guard, SAMPLE_GUARD_3)
            self.assertEqual(dlg._operandListBox.GetString(0), f'[0] [{SAMPLE_GUARD_3}]')

    def testDlgEditCombinedFragmentAddOperand(self):
        """
        Verify that adding an operand appends a new operand and selects it for editing.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.ALT,
            operands=self._operands
        ) as dlg:
            dummyEvent: CommandEvent = CommandEvent()
            dlg._onAddOperand(dummyEvent)

            self.assertEqual(len(dlg.operands), 3)
            self.assertEqual(dlg._operandListBox.GetCount(), 3)
            self.assertEqual(dlg._operandListBox.GetSelection(), 2)
            self.assertEqual(dlg._guardTextCtrl.GetValue(), '')
            self.assertEqual(dlg._operandListBox.GetString(2), '[2]')
            self.assertTrue(dlg._btnUp.IsEnabled())
            self.assertFalse(dlg._btnDown.IsEnabled())

    def testDlgEditCombinedFragmentRemoveOperand(self):
        """
        Verify that removing an operand deletes it from operands and updates selection.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.ALT,
            operands=self._operands
        ) as dlg:
            dlg._operandListBox.SetSelection(0)
            dummyEvent: CommandEvent = CommandEvent()
            dlg._onRemoveOperand(dummyEvent)

            self.assertEqual(len(dlg.operands), 1)
            self.assertEqual(dlg._operandListBox.GetCount(), 1)
            self.assertEqual(dlg.operands[0].guard, SAMPLE_GUARD_2)
            self.assertEqual(dlg._guardTextCtrl.GetValue(), SAMPLE_GUARD_2)
            self.assertFalse(dlg._btnUp.IsEnabled())
            self.assertFalse(dlg._btnDown.IsEnabled())

    def testDlgEditCombinedFragmentMoveUpAndDown(self):
        """
        Verify that moving operands up and down reorders the operand list and updates list display.
        """
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.ALT,
            operands=self._operands
        ) as dlg:
            dlg._operandListBox.SetSelection(1)
            dummyEvent: CommandEvent = CommandEvent()
            dlg._onUpOperand(dummyEvent)

            self.assertEqual(dlg.operands[0].guard, SAMPLE_GUARD_2)
            self.assertEqual(dlg.operands[1].guard, SAMPLE_GUARD_1)
            self.assertEqual(dlg._operandListBox.GetSelection(), 0)

            dummyEvent = CommandEvent()
            dlg._onDownOperand(dummyEvent)

            self.assertEqual(dlg.operands[0].guard, SAMPLE_GUARD_1)
            self.assertEqual(dlg.operands[1].guard, SAMPLE_GUARD_2)
            self.assertEqual(dlg._operandListBox.GetSelection(), 1)

    def testDlgEditCombinedFragmentEmptyOperandsHandling(self):
        """
        Verify that dialog handles empty operand list by disabling controls until an operand is added.
        """
        emptyOperands: SDInteractionOperands = SDInteractionOperands([])
        with DlgEditCombinedFragment(
            parent=self._listeningWindow,
            operator=SDFragmentOperator.LOOP,
            operands=emptyOperands
        ) as dlg:
            self.assertEqual(len(dlg.operands), 0)
            self.assertEqual(dlg._operandListBox.GetCount(), 0)
            self.assertFalse(dlg._guardTextCtrl.IsEnabled())
            self.assertFalse(dlg._btnRemove.IsEnabled())
            self.assertFalse(dlg._btnUp.IsEnabled())
            self.assertFalse(dlg._btnDown.IsEnabled())

            dummyEvent: CommandEvent = CommandEvent()
            dlg._onAddOperand(dummyEvent)

            self.assertEqual(len(dlg.operands), 1)
            self.assertTrue(dlg._guardTextCtrl.IsEnabled())
            self.assertTrue(dlg._btnRemove.IsEnabled())


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestDlgEditCombinedFragment))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
