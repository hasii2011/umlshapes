from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallybasic.UnitTestBase import UnitTestBase

from umlshapes.sd.SDLayoutParameters import DEFAULT_COLUMN_SPACING
from umlshapes.sd.SDLayoutParameters import SDLayoutParameters
from umlshapes.sd.SDLayoutEngine import SDLayoutEngine

COLUMN_0_INDEX: int = 0
COLUMN_1_INDEX: int = 1
COLUMN_2_INDEX: int = 2

EXPECTED_COL_0_X: int = 100
EXPECTED_COL_1_X: int = 320
EXPECTED_COL_2_X: int = 540

HEADER_BOTTOM_Y: int = 90

SLOT_0_INDEX: int = 0
SLOT_1_INDEX: int = 1
SLOT_2_INDEX: int = 2

EXPECTED_SLOT_0_Y: int = 110
EXPECTED_SLOT_1_Y: int = 150
EXPECTED_SLOT_2_Y: int = 190

TARGET_Y_ABOVE_SLOTS: int = 80
TARGET_Y_NEAR_SLOT_0: int = 115
TARGET_Y_NEAR_SLOT_1: int = 145
TARGET_Y_NEAR_SLOT_2: int = 195

TOTAL_SLOTS_FEW:  int = 2
TOTAL_SLOTS_MANY: int = 10

EXPECTED_FEW_SLOTS_HEIGHT:  int = 360
EXPECTED_MANY_SLOTS_HEIGHT: int = 500

CUSTOM_COLUMN_SPACING: int = 300
CUSTOM_SLOT_HEIGHT:    int = 50
CUSTOM_TOP_PADDING:    int = 30
CUSTOM_BOTTOM_PADDING: int = 50
CUSTOM_START_X:        int = 150
CUSTOM_START_Y:        int = 80

EXPECTED_CUSTOM_COL_0_X:  int = 150
EXPECTED_CUSTOM_COL_1_X:  int = 450
EXPECTED_CUSTOM_SLOT_1_Y: int = 170

EXTERNAL_MUTATION_VALUE: int = 999
NEW_COLUMN_SPACING:      int = 400
EXPECTED_NEW_COL_1_X:    int = 500


class TestSDLayoutEngine(UnitTestBase):
    """
    Unit tests for SDLayoutEngine column and slot calculations.
    """

    def setUp(self):
        super().setUp()
        self._layoutEngine: SDLayoutEngine = SDLayoutEngine()

    def testComputeColumnX(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine
        col0: int = layoutEngine.computeColumnX(columnIndex=COLUMN_0_INDEX)
        col1: int = layoutEngine.computeColumnX(columnIndex=COLUMN_1_INDEX)
        col2: int = layoutEngine.computeColumnX(columnIndex=COLUMN_2_INDEX)

        self.assertEqual(EXPECTED_COL_0_X, col0)
        self.assertEqual(EXPECTED_COL_1_X, col1)
        self.assertEqual(EXPECTED_COL_2_X, col2)

    def testComputeSlotY(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        slot0: int = layoutEngine.computeSlotY(headerBottomY=HEADER_BOTTOM_Y, slotIndex=SLOT_0_INDEX)
        slot1: int = layoutEngine.computeSlotY(headerBottomY=HEADER_BOTTOM_Y, slotIndex=SLOT_1_INDEX)
        slot2: int = layoutEngine.computeSlotY(headerBottomY=HEADER_BOTTOM_Y, slotIndex=SLOT_2_INDEX)

        self.assertEqual(EXPECTED_SLOT_0_Y, slot0)
        self.assertEqual(EXPECTED_SLOT_1_Y, slot1)
        self.assertEqual(EXPECTED_SLOT_2_Y, slot2)

    def testComputeNearestSlotIndex(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        idxAbove: int = layoutEngine.computeNearestSlotIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_ABOVE_SLOTS)
        idx0:     int = layoutEngine.computeNearestSlotIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_SLOT_0)
        idx1:     int = layoutEngine.computeNearestSlotIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_SLOT_1)
        idx2:     int = layoutEngine.computeNearestSlotIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_SLOT_2)

        self.assertEqual(SLOT_0_INDEX, idxAbove)
        self.assertEqual(SLOT_0_INDEX, idx0)
        self.assertEqual(SLOT_1_INDEX, idx1)
        self.assertEqual(SLOT_2_INDEX, idx2)

    def testComputeNearestSlotY(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        snappedY: int = layoutEngine.computeNearestSlotY(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_SLOT_1)
        self.assertEqual(EXPECTED_SLOT_1_Y, snappedY)

    def testComputeLifelineHeight(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        heightFewSlots: int = layoutEngine.computeLifelineHeight(totalSlots=TOTAL_SLOTS_FEW)
        self.assertEqual(EXPECTED_FEW_SLOTS_HEIGHT, heightFewSlots)

        heightManySlots: int = layoutEngine.computeLifelineHeight(totalSlots=TOTAL_SLOTS_MANY)
        self.assertEqual(EXPECTED_MANY_SLOTS_HEIGHT, heightManySlots)

    def testCustomParameters(self):
        customParams: SDLayoutParameters = SDLayoutParameters(
            columnSpacing=CUSTOM_COLUMN_SPACING,
            slotHeight=CUSTOM_SLOT_HEIGHT,
            topPadding=CUSTOM_TOP_PADDING,
            bottomPadding=CUSTOM_BOTTOM_PADDING,
            startX=CUSTOM_START_X,
            startY=CUSTOM_START_Y
        )
        customEngine: SDLayoutEngine = SDLayoutEngine(parameters=customParams)

        self.assertEqual(EXPECTED_CUSTOM_COL_0_X, customEngine.computeColumnX(columnIndex=COLUMN_0_INDEX))
        self.assertEqual(EXPECTED_CUSTOM_COL_1_X, customEngine.computeColumnX(columnIndex=COLUMN_1_INDEX))
        self.assertEqual(EXPECTED_CUSTOM_SLOT_1_Y, customEngine.computeSlotY(headerBottomY=HEADER_BOTTOM_Y, slotIndex=SLOT_1_INDEX))

    def testParametersImmutabilityViaCopy(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine
        paramsCopy: SDLayoutParameters = layoutEngine.parameters
        paramsCopy.columnSpacing = EXTERNAL_MUTATION_VALUE

        self.assertEqual(DEFAULT_COLUMN_SPACING, layoutEngine.parameters.columnSpacing)

    def testParametersSetter(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine
        newParams: SDLayoutParameters = SDLayoutParameters(columnSpacing=NEW_COLUMN_SPACING)
        layoutEngine.parameters = newParams

        self.assertEqual(NEW_COLUMN_SPACING, layoutEngine.parameters.columnSpacing)
        self.assertEqual(EXPECTED_NEW_COL_1_X, layoutEngine.computeColumnX(columnIndex=COLUMN_1_INDEX))


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestSDLayoutEngine))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
