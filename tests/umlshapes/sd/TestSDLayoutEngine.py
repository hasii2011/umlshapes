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

TIME_STEP_0_INDEX: int = 0
TIME_STEP_1_INDEX: int = 1
TIME_STEP_2_INDEX: int = 2

EXPECTED_TIME_STEP_0_Y: int = 110
EXPECTED_TIME_STEP_1_Y: int = 150
EXPECTED_TIME_STEP_2_Y: int = 190

TARGET_Y_ABOVE_TIME_STEPS: int = 80
TARGET_Y_NEAR_TIME_STEP_0: int = 115
TARGET_Y_NEAR_TIME_STEP_1: int = 145
TARGET_Y_NEAR_TIME_STEP_2: int = 195

TOTAL_TIME_STEPS_FEW:  int = 2
TOTAL_TIME_STEPS_MANY: int = 10

EXPECTED_FEW_TIME_STEPS_HEIGHT:  int = 360
EXPECTED_MANY_TIME_STEPS_HEIGHT: int = 500

CUSTOM_COLUMN_SPACING:  int = 300
CUSTOM_TIME_STEP_HEIGHT: int = 50
CUSTOM_TOP_PADDING:     int = 30
CUSTOM_BOTTOM_PADDING:  int = 50
CUSTOM_START_X:         int = 150
CUSTOM_START_Y:         int = 80

EXPECTED_CUSTOM_COL_0_X:       int = 150
EXPECTED_CUSTOM_COL_1_X:       int = 450
EXPECTED_CUSTOM_TIME_STEP_1_Y: int = 170

EXTERNAL_MUTATION_VALUE: int = 999
NEW_COLUMN_SPACING:      int = 400
EXPECTED_NEW_COL_1_X:    int = 500

LIFELINE_X:                    int = 200
START_Y:                       int = 120
END_Y:                         int = 240
NESTING_LEVEL_0:               int = 0
NESTING_LEVEL_1:               int = 1
NESTING_LEVEL_2:               int = 2

EXPECTED_EXECUTION_X_LEVEL_0: int = 200
EXPECTED_EXECUTION_X_LEVEL_1: int = 207
EXPECTED_EXECUTION_X_LEVEL_2: int = 214

EXPECTED_EXECUTION_WIDTH:     int = 14
EXPECTED_EXECUTION_CENTER_Y:  int = 180
EXPECTED_EXECUTION_HEIGHT:    int = 120
EXPECTED_MIN_HEIGHT:           int = 40
TINY_END_Y:                    int = 130


class TestSDLayoutEngine(UnitTestBase):
    """
    Unit tests for SDLayoutEngine column and timeStep calculations.
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

    def testComputeTimeStepY(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        timeStep0: int = layoutEngine.computeTimeStepY(headerBottomY=HEADER_BOTTOM_Y, timeStepIndex=TIME_STEP_0_INDEX)
        timeStep1: int = layoutEngine.computeTimeStepY(headerBottomY=HEADER_BOTTOM_Y, timeStepIndex=TIME_STEP_1_INDEX)
        timeStep2: int = layoutEngine.computeTimeStepY(headerBottomY=HEADER_BOTTOM_Y, timeStepIndex=TIME_STEP_2_INDEX)

        self.assertEqual(EXPECTED_TIME_STEP_0_Y, timeStep0)
        self.assertEqual(EXPECTED_TIME_STEP_1_Y, timeStep1)
        self.assertEqual(EXPECTED_TIME_STEP_2_Y, timeStep2)

    def testComputeNearestTimeStepIndex(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        idxAbove: int = layoutEngine.computeNearestTimeStepIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_ABOVE_TIME_STEPS)
        idx0:     int = layoutEngine.computeNearestTimeStepIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_TIME_STEP_0)
        idx1:     int = layoutEngine.computeNearestTimeStepIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_TIME_STEP_1)
        idx2:     int = layoutEngine.computeNearestTimeStepIndex(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_TIME_STEP_2)

        self.assertEqual(TIME_STEP_0_INDEX, idxAbove)
        self.assertEqual(TIME_STEP_0_INDEX, idx0)
        self.assertEqual(TIME_STEP_1_INDEX, idx1)
        self.assertEqual(TIME_STEP_2_INDEX, idx2)

    def testComputeNearestTimeStepY(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        snappedY: int = layoutEngine.computeNearestTimeStepY(headerBottomY=HEADER_BOTTOM_Y, targetY=TARGET_Y_NEAR_TIME_STEP_1)
        self.assertEqual(EXPECTED_TIME_STEP_1_Y, snappedY)

    def testComputeLifelineHeight(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        heightFewTimeSteps: int = layoutEngine.computeLifelineHeight(totalTimeSteps=TOTAL_TIME_STEPS_FEW)
        self.assertEqual(EXPECTED_FEW_TIME_STEPS_HEIGHT, heightFewTimeSteps)

        heightManyTimeSteps: int = layoutEngine.computeLifelineHeight(totalTimeSteps=TOTAL_TIME_STEPS_MANY)
        self.assertEqual(EXPECTED_MANY_TIME_STEPS_HEIGHT, heightManyTimeSteps)

    def testCustomParameters(self):
        customParams: SDLayoutParameters = SDLayoutParameters(
            columnSpacing=CUSTOM_COLUMN_SPACING,
            timeStepHeight=CUSTOM_TIME_STEP_HEIGHT,
            topPadding=CUSTOM_TOP_PADDING,
            bottomPadding=CUSTOM_BOTTOM_PADDING,
            startX=CUSTOM_START_X,
            startY=CUSTOM_START_Y
        )
        customEngine: SDLayoutEngine = SDLayoutEngine()
        customEngine.parameters = customParams

        self.assertEqual(EXPECTED_CUSTOM_COL_0_X, customEngine.computeColumnX(columnIndex=COLUMN_0_INDEX))
        self.assertEqual(EXPECTED_CUSTOM_COL_1_X, customEngine.computeColumnX(columnIndex=COLUMN_1_INDEX))
        self.assertEqual(EXPECTED_CUSTOM_TIME_STEP_1_Y, customEngine.computeTimeStepY(headerBottomY=HEADER_BOTTOM_Y, timeStepIndex=TIME_STEP_1_INDEX))

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

    def testComputeExecutionX(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        x0: int = layoutEngine.computeExecutionX(lifeLineX=LIFELINE_X, nestingLevel=NESTING_LEVEL_0)
        x1: int = layoutEngine.computeExecutionX(lifeLineX=LIFELINE_X, nestingLevel=NESTING_LEVEL_1)
        x2: int = layoutEngine.computeExecutionX(lifeLineX=LIFELINE_X, nestingLevel=NESTING_LEVEL_2)

        self.assertEqual(EXPECTED_EXECUTION_X_LEVEL_0, x0)
        self.assertEqual(EXPECTED_EXECUTION_X_LEVEL_1, x1)
        self.assertEqual(EXPECTED_EXECUTION_X_LEVEL_2, x2)

    def testComputeExecutionBounds(self):
        layoutEngine: SDLayoutEngine = self._layoutEngine

        centerX, centerY, width, height = layoutEngine.computeExecutionBounds(
            lifeLineX=LIFELINE_X,
            startY=START_Y,
            endY=END_Y,
            nestingLevel=NESTING_LEVEL_1
        )

        self.assertEqual(EXPECTED_EXECUTION_X_LEVEL_1, centerX)
        self.assertEqual(EXPECTED_EXECUTION_CENTER_Y, centerY)
        self.assertEqual(EXPECTED_EXECUTION_WIDTH, width)
        self.assertEqual(EXPECTED_EXECUTION_HEIGHT, height)

        # Ensure minimum height is at least one timeStepHeight
        _, _, _, minHeight = layoutEngine.computeExecutionBounds(
            lifeLineX=LIFELINE_X,
            startY=START_Y,
            endY=TINY_END_Y,
            nestingLevel=NESTING_LEVEL_0
        )
        self.assertEqual(EXPECTED_MIN_HEIGHT, minHeight)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestSDLayoutEngine))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
