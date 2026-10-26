
from typing import cast

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import Bitmap
from wx import ClientDC
from wx import MemoryDC

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.sd.SDFragmentBounds import SDFragmentBounds
from umlshapes.sd.SDFragmentOperator import SDFragmentOperator
from umlshapes.sd.SDInteractionOperand import SDInteractionOperand
from umlshapes.sd.SDInteractionOperand import SDInteractionOperands
from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.UmlSDCombinedFragment import DEFAULT_FRAGMENT_HEIGHT
from umlshapes.sd.UmlSDCombinedFragment import DEFAULT_FRAGMENT_WIDTH
from umlshapes.sd.UmlSDCombinedFragment import UmlSDCombinedFragment
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

from umlshapes.sd.eventhandlers.UmlSDCombinedFragmentEventHandler import HANDLE_BOTTOM_MIDDLE
from umlshapes.sd.eventhandlers.UmlSDCombinedFragmentEventHandler import HANDLE_MIDDLE_RIGHT
from umlshapes.sd.eventhandlers.UmlSDCombinedFragmentEventHandler import HANDLE_TOP_MIDDLE
from umlshapes.sd.eventhandlers.UmlSDCombinedFragmentEventHandler import MIN_FRAGMENT_WIDTH
from umlshapes.sd.eventhandlers.UmlSDCombinedFragmentEventHandler import UmlSDCombinedFragmentEventHandler

INSTANCE_1_X:       int = 100
INSTANCE_2_X:       int = 320
INSTANCE_DEFAULT_Y: int = 50

FRAGMENT_START_Y:   int = 100
FRAGMENT_END_Y:     int = 220
BITMAP_WIDTH:       int = 800
BITMAP_HEIGHT:      int = 600

CUSTOM_FRAGMENT_X:      float = 200.0
CUSTOM_FRAGMENT_Y:      float = 150.0
CUSTOM_FRAGMENT_WIDTH:  int = 300
CUSTOM_FRAGMENT_HEIGHT: int = 180

BOUNDS_CENTER_X: int = 200
BOUNDS_CENTER_Y: int = 150
BOUNDS_WIDTH:    int = 120
BOUNDS_HEIGHT:   int = 80

EXPECTED_BOUNDS_LEFT:   int = 140
EXPECTED_BOUNDS_RIGHT:  int = 260
EXPECTED_BOUNDS_TOP:    int = 110
EXPECTED_BOUNDS_BOTTOM: int = 190

HIT_TEST_FRAGMENT_X:      float = 100.0
HIT_TEST_FRAGMENT_Y:      float = 100.0
HIT_TEST_FRAGMENT_WIDTH:  int = 100
HIT_TEST_FRAGMENT_HEIGHT: int = 100

HIT_TEST_INSIDE_LEFT_X:   float = 50.0
HIT_TEST_INSIDE_RIGHT_X:  float = 150.0
HIT_TEST_INSIDE_TOP_Y:    float = 50.0
HIT_TEST_INSIDE_BOTTOM_Y: float = 150.0

HIT_TEST_OUTSIDE_LEFT_X:   float = 49.0
HIT_TEST_OUTSIDE_RIGHT_X:  float = 151.0
HIT_TEST_OUTSIDE_TOP_Y:    float = 49.0
HIT_TEST_OUTSIDE_BOTTOM_Y: float = 151.0

DRAG_FRAGMENT_X:      float = 200.0
DRAG_FRAGMENT_Y:      float = 150.0
DRAG_FRAGMENT_WIDTH:  int = 200
DRAG_FRAGMENT_HEIGHT: int = 120

DRAG_START_X: int = 200
DRAG_START_Y: int = 150

DRAG_TARGET_X: int = 250
DRAG_TARGET_Y: int = 190
DRAG_DELTA_Y:  int = 40

EXPECTED_DRAG_X: float = 250.0

SIZING_CLAMP_FRAGMENT_X:      float = 200.0
SIZING_CLAMP_FRAGMENT_Y:      float = 150.0
SIZING_CLAMP_FRAGMENT_WIDTH:  int = 200
SIZING_CLAMP_FRAGMENT_HEIGHT: int = 120

SIZING_CLAMP_START_X: int = 300
SIZING_CLAMP_START_Y: int = 150

SIZING_CLAMP_TARGET_X: int = 120
SIZING_CLAMP_TARGET_Y: int = 150


class TestSDCombinedFragment(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Combined Fragments (UmlSDCombinedFragment).
    Tests creation, operators, operand management, geometry calculations,
    hit testing, drawing, and interactive event handling (selection, dragging, sizing).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._preferences:     UmlPreferences       = UmlPreferences()
        self._layoutEngine:    SDLayoutEngine       = SDLayoutEngine()
        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        self._diagramFrame.Destroy()
        super().tearDown()

    def testFragmentCreationAndDefaults(self):
        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment()

        self.assertEqual(SDFragmentOperator.ALT, fragment.operator)
        self.assertEqual(0, len(fragment.operands))
        self.assertEqual(DEFAULT_FRAGMENT_WIDTH, fragment.GetWidth())
        self.assertEqual(DEFAULT_FRAGMENT_HEIGHT, fragment.GetHeight())
        self.assertEqual(0.0, fragment.GetX())
        self.assertEqual(0.0, fragment.GetY())

        expectedStr: str = f'UmlSDCombinedFragment(id={fragment.id}, operator=alt, operands=0)'
        self.assertEqual(expectedStr, str(fragment))
        self.assertEqual(expectedStr, repr(fragment))

    def testFragmentCustomOperatorAndOperands(self):
        initialOperands: SDInteractionOperands = SDInteractionOperands([
            SDInteractionOperand(guard='x > 0', startTimeStep=0, endTimeStep=1)
        ])
        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.LOOP,
            operands=initialOperands,
            x=CUSTOM_FRAGMENT_X,
            y=CUSTOM_FRAGMENT_Y,
            width=CUSTOM_FRAGMENT_WIDTH,
            height=CUSTOM_FRAGMENT_HEIGHT
        )

        self.assertEqual(SDFragmentOperator.LOOP, fragment.operator)
        self.assertEqual(1, len(fragment.operands))
        self.assertEqual(CUSTOM_FRAGMENT_WIDTH, fragment.GetWidth())
        self.assertEqual(CUSTOM_FRAGMENT_HEIGHT, fragment.GetHeight())
        self.assertEqual(CUSTOM_FRAGMENT_X, fragment.GetX())
        self.assertEqual(CUSTOM_FRAGMENT_Y, fragment.GetY())

        # Test setter for operator
        fragment.operator = SDFragmentOperator.PAR
        self.assertEqual(SDFragmentOperator.PAR, fragment.operator)

        # Test adding operand
        newOperand: SDInteractionOperand = fragment.addOperand(guard='else', startTimeStep=1, endTimeStep=2)
        self.assertEqual(2, len(fragment.operands))
        self.assertEqual('else', newOperand.guard)
        self.assertEqual(1, newOperand.startTimeStep)
        self.assertEqual(2, newOperand.endTimeStep)

        # Test removing operand
        fragment.removeOperand(0)
        self.assertEqual(1, len(fragment.operands))
        self.assertEqual('else', fragment.operands[0].guard)

        # Test removing out of range operand does not fail
        fragment.removeOperand(99)
        self.assertEqual(1, len(fragment.operands))

    def testFragmentHitTest(self):
        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            x=HIT_TEST_FRAGMENT_X,
            y=HIT_TEST_FRAGMENT_Y,
            width=HIT_TEST_FRAGMENT_WIDTH,
            height=HIT_TEST_FRAGMENT_HEIGHT
        )

        # Inside center
        insideHitResult: object = fragment.HitTest(x=HIT_TEST_FRAGMENT_X, y=HIT_TEST_FRAGMENT_Y)
        self.assertNotEqual(False, insideHitResult)

        # Inside corners
        self.assertNotEqual(False, fragment.HitTest(x=HIT_TEST_INSIDE_LEFT_X, y=HIT_TEST_INSIDE_TOP_Y))
        self.assertNotEqual(False, fragment.HitTest(x=HIT_TEST_INSIDE_RIGHT_X, y=HIT_TEST_INSIDE_BOTTOM_Y))

        # Outside bounds
        self.assertEqual(False, fragment.HitTest(x=HIT_TEST_OUTSIDE_LEFT_X, y=HIT_TEST_FRAGMENT_Y))
        self.assertEqual(False, fragment.HitTest(x=HIT_TEST_OUTSIDE_RIGHT_X, y=HIT_TEST_FRAGMENT_Y))
        self.assertEqual(False, fragment.HitTest(x=HIT_TEST_FRAGMENT_X, y=HIT_TEST_OUTSIDE_TOP_Y))
        self.assertEqual(False, fragment.HitTest(x=HIT_TEST_FRAGMENT_X, y=HIT_TEST_OUTSIDE_BOTTOM_Y))

    def testFragmentBoundsDataclass(self):
        bounds: SDFragmentBounds = SDFragmentBounds(
            centerX=BOUNDS_CENTER_X,
            centerY=BOUNDS_CENTER_Y,
            width=BOUNDS_WIDTH,
            height=BOUNDS_HEIGHT
        )

        self.assertEqual(BOUNDS_CENTER_X, bounds.centerX)
        self.assertEqual(BOUNDS_CENTER_Y, bounds.centerY)
        self.assertEqual(BOUNDS_WIDTH, bounds.width)
        self.assertEqual(BOUNDS_HEIGHT, bounds.height)

        self.assertEqual(EXPECTED_BOUNDS_LEFT, bounds.left)
        self.assertEqual(EXPECTED_BOUNDS_RIGHT, bounds.right)
        self.assertEqual(EXPECTED_BOUNDS_TOP, bounds.top)
        self.assertEqual(EXPECTED_BOUNDS_BOTTOM, bounds.bottom)

    def testFragmentLayoutEngineIntegration(self):

        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        lifeLines: list[UmlSDLifeLine] = [inst1.umlSDLifeLine, inst2.umlSDLifeLine]
        bounds: SDFragmentBounds = self._layoutEngine.computeFragmentBounds(
            lifeLines=lifeLines,
            startY=FRAGMENT_START_Y,
            endY=FRAGMENT_END_Y
        )

        expectedPadding: int = self._layoutEngine.parameters.fragmentPadding
        expectedMinX:    int = round(inst1.umlSDLifeLine.GetX()) - expectedPadding
        expectedMaxX:    int = round(inst2.umlSDLifeLine.GetX()) + expectedPadding
        expectedWidth:   int = expectedMaxX - expectedMinX
        expectedCenterX: int = (expectedMinX + expectedMaxX) // 2

        self.assertEqual(expectedWidth, bounds.width)
        self.assertEqual(expectedCenterX, bounds.centerX)
        self.assertEqual(FRAGMENT_END_Y - FRAGMENT_START_Y, bounds.height)
        self.assertEqual((FRAGMENT_START_Y + FRAGMENT_END_Y) // 2, bounds.centerY)

        # Empty lifelines fallback
        emptyBounds: SDFragmentBounds = self._layoutEngine.computeFragmentBounds(
            lifeLines=[],
            startY=FRAGMENT_START_Y,
            endY=FRAGMENT_END_Y
        )
        self.assertEqual(0, emptyBounds.width)
        self.assertEqual(0, emptyBounds.centerX)

        # Snap fragment to time steps
        headerBottomY: int = round(inst1.umlSDLifeLine.rectangle.top)
        snappedStartY: int
        snappedEndY: int
        snappedStartY, snappedEndY = self._layoutEngine.snapFragmentToTimeSteps(
            headerBottomY=headerBottomY,
            startY=118,
            endY=222
        )
        self.assertLess(snappedStartY, snappedEndY)
        self.assertGreaterEqual(snappedEndY - snappedStartY, self._layoutEngine.parameters.timeStepHeight)

        # Enforce minimum height when end <= start
        invertedStartY: int
        invertedEndY: int
        invertedStartY, invertedEndY = self._layoutEngine.snapFragmentToTimeSteps(
            headerBottomY=headerBottomY,
            startY=150,
            endY=140
        )
        self.assertEqual(invertedStartY + self._layoutEngine.parameters.timeStepHeight, invertedEndY)

    def testFragmentDrawing(self):

        bitmap: Bitmap   = Bitmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        dc:     MemoryDC = MemoryDC(bitmap)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.ALT,
            x=200.0,
            y=200.0,
            width=250,
            height=150
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        fragment.addOperand(guard='balance >= total', startTimeStep=0, endTimeStep=1)
        fragment.addOperand(guard='[else]', startTimeStep=1, endTimeStep=2)

        # Draw unselected
        fragment.Select(False)
        fragment.OnDraw(dc=dc)

        # Draw selected
        fragment.Select(True)
        fragment.OnDraw(dc=dc)

        dc.SelectObject(Bitmap())

    def testFragmentEventHandlerSelection(self):
        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            x=200.0,
            y=200.0,
            width=200,
            height=120
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        eventHandler: UmlSDCombinedFragmentEventHandler = cast(
            UmlSDCombinedFragmentEventHandler,
            fragment.GetEventHandler()
        )
        self.assertIsInstance(eventHandler, UmlSDCombinedFragmentEventHandler)

        selectedShapes: list[object] = []

        def selectionListener(umlShape: object, **kwargs):
            selectedShapes.append(umlShape)

        self._umlPubSubEngine.subscribe(
            messageType=UmlMessageType.UML_SHAPE_SELECTED,
            frameId=self._diagramFrame.id,
            listener=selectionListener
        )

        self.assertFalse(fragment.Selected())

        # Click to select
        eventHandler.OnLeftClick(x=200, y=200)

        self.assertTrue(fragment.Selected())
        self.assertEqual(1, len(selectedShapes))
        self.assertIs(fragment, selectedShapes[0])

        # Click again to deselect
        eventHandler.OnLeftClick(x=200, y=200)
        self.assertFalse(fragment.Selected())

    def testFragmentEventHandlerDragging(self):

        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            x=DRAG_FRAGMENT_X,
            y=DRAG_FRAGMENT_Y,
            width=DRAG_FRAGMENT_WIDTH,
            height=DRAG_FRAGMENT_HEIGHT
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        eventHandler: UmlSDCombinedFragmentEventHandler = cast(
            UmlSDCombinedFragmentEventHandler,
            fragment.GetEventHandler()
        )

        eventHandler.OnBeginDragLeft(x=DRAG_START_X, y=DRAG_START_Y)
        self.assertTrue(fragment.Selected())

        # Drag right and down
        eventHandler.OnDragLeft(draw=False, x=DRAG_TARGET_X, y=DRAG_TARGET_Y)
        self.assertEqual(EXPECTED_DRAG_X, fragment.GetX())

        headerBottomY: int   = round(inst1.umlSDLifeLine.rectangle.top)
        halfHeight:    float = fragment.GetHeight() / 2.0
        expectedTopY:  int   = self._layoutEngine.computeNearestTimeStepY(
            headerBottomY=headerBottomY,
            targetY=round((DRAG_FRAGMENT_Y + DRAG_DELTA_Y) - halfHeight)
        )
        self.assertEqual(expectedTopY + halfHeight, fragment.GetY())

        eventHandler.OnEndDragLeft(x=DRAG_TARGET_X, y=DRAG_TARGET_Y)
        self.assertEqual(EXPECTED_DRAG_X, fragment.GetX())
        self.assertEqual(expectedTopY + halfHeight, fragment.GetY())

    def testFragmentEventHandlerSizingBottomHandle(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            x=200.0,
            y=150.0,
            width=200,
            height=120
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        # Initialize control points
        fragment.MakeControlPoints()
        controlPoints: list[ControlPoint] = fragment.getControlPoints()
        bottomHandle:  ControlPoint       = controlPoints[HANDLE_BOTTOM_MIDDLE]

        eventHandler: UmlSDCombinedFragmentEventHandler = cast(
            UmlSDCombinedFragmentEventHandler,
            fragment.GetEventHandler()
        )

        eventHandler.OnSizingBeginDragLeft(pt=bottomHandle, x=200, y=210)

        # Drag bottom handle downwards
        targetY: int = 265
        eventHandler.OnSizingDragLeft(pt=bottomHandle, draw=False, x=200, y=targetY)

        headerBottomY:         int = round(inst1.umlSDLifeLine.rectangle.top)
        expectedSnappedBottom: int = self._layoutEngine.computeNearestTimeStepY(
            headerBottomY=headerBottomY,
            targetY=targetY
        )
        expectedTop:     float = 150.0 - (120.0 / 2.0)
        expectedHeight:  float = expectedSnappedBottom - expectedTop
        expectedCenterY: float = (expectedTop + expectedSnappedBottom) / 2.0

        self.assertEqual(expectedHeight, fragment.GetHeight())
        self.assertEqual(expectedCenterY, fragment.GetY())

        eventHandler.OnSizingEndDragLeft(pt=bottomHandle, x=200, y=targetY)
        self.assertEqual(expectedHeight, fragment.GetHeight())

    def testFragmentEventHandlerSizingTopHandle(self):

        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            x=200.0,
            y=150.0,
            width=200,
            height=120
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        fragment.MakeControlPoints()

        controlPoints: list[ControlPoint] = fragment.getControlPoints()
        topHandle:     ControlPoint       = controlPoints[HANDLE_TOP_MIDDLE]

        eventHandler: UmlSDCombinedFragmentEventHandler = cast(
            UmlSDCombinedFragmentEventHandler,
            fragment.GetEventHandler()
        )

        eventHandler.OnSizingBeginDragLeft(pt=topHandle, x=200, y=90)

        # Drag top handle upwards
        targetY: int = 70
        eventHandler.OnSizingDragLeft(pt=topHandle, draw=False, x=200, y=targetY)

        headerBottomY:      int = round(inst1.umlSDLifeLine.rectangle.top)
        expectedSnappedTop: int = self._layoutEngine.computeNearestTimeStepY(
            headerBottomY=headerBottomY,
            targetY=targetY
        )
        expectedBottom:  float = 150.0 + (120.0 / 2.0)
        expectedHeight:  float = expectedBottom - expectedSnappedTop
        expectedCenterY: float = (expectedSnappedTop + expectedBottom) / 2.0

        self.assertEqual(expectedHeight, fragment.GetHeight())
        self.assertEqual(expectedCenterY, fragment.GetY())

        eventHandler.OnSizingEndDragLeft(pt=topHandle, x=200, y=targetY)
        self.assertEqual(expectedHeight, fragment.GetHeight())

    def testFragmentEventHandlerSizingWidthClamp(self):
        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            x=SIZING_CLAMP_FRAGMENT_X,
            y=SIZING_CLAMP_FRAGMENT_Y,
            width=SIZING_CLAMP_FRAGMENT_WIDTH,
            height=SIZING_CLAMP_FRAGMENT_HEIGHT
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        fragment.MakeControlPoints()
        controlPoints: list[ControlPoint] = fragment.getControlPoints()
        rightHandle:   ControlPoint       = controlPoints[HANDLE_MIDDLE_RIGHT]

        eventHandler: UmlSDCombinedFragmentEventHandler = cast(
            UmlSDCombinedFragmentEventHandler,
            fragment.GetEventHandler()
        )

        # Drag right handle leftwards towards minimum width
        eventHandler.OnSizingBeginDragLeft(pt=rightHandle, x=SIZING_CLAMP_START_X, y=SIZING_CLAMP_START_Y)
        eventHandler.OnSizingDragLeft(pt=rightHandle, draw=False, x=SIZING_CLAMP_TARGET_X, y=SIZING_CLAMP_TARGET_Y)
        eventHandler.OnSizingEndDragLeft(pt=rightHandle, x=SIZING_CLAMP_TARGET_X, y=SIZING_CLAMP_TARGET_Y)

        self.assertGreaterEqual(fragment.GetWidth(), MIN_FRAGMENT_WIDTH)

    def _createSDInstance(self, name: str, x: int, y: int = INSTANCE_DEFAULT_Y) -> UmlSDInstance:
        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = name

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        umlPosition: UmlPosition = UmlPosition(x=x, y=y)
        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        centerX: float
        centerY: float
        centerX, centerY = umlSDInstance.computeCenterXY(position=umlPosition)
        umlSDInstance.Move(dc, centerX, centerY)
        umlSDInstance.position = umlPosition

        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)
        return umlSDInstance


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestSDCombinedFragment))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
