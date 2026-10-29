
from typing import cast
from typing import Optional

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import ClientDC

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.SDExecution import SDExecution
from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.SDMessageCreationHandler import SDMessageCreationHandler
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDExecution import EXECUTION_BOTTOM_HANDLE_INDEX
from umlshapes.sd.UmlSDExecution import EXECUTION_TOP_HANDLE_INDEX
from umlshapes.sd.UmlSDExecution import UmlSDExecution
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage

from umlshapes.sd.eventhandlers.UmlSDExecutionEventHandler import UmlSDExecutionEventHandler
from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import LifeLineClickDetails

INSTANCE_1_X:                     int = 100
INSTANCE_2_X:                     int = 320
INSTANCE_DEFAULT_Y:               int = 50

EXECUTION_START_Y_1:              int = 100
EXECUTION_END_Y_1:                int = 220
EXECUTION_START_Y_2:              int = 140
EXECUTION_END_Y_2:                int = 260
EXECUTION_START_Y_3:              int = 160
EXECUTION_END_Y_3:                int = 200
EXECUTION_START_Y_NON_OVERLAP:    int = 300
EXECUTION_END_Y_NON_OVERLAP:      int = 380

OUTSIDE_Y:                        int = 450
PROBE_Y_LEVEL_0_ONLY:             int = 120
PROBE_Y_LEVEL_1_OVERLAP:          int = 150
PROBE_Y_LEVEL_2_OVERLAP:          int = 175

RESIZE_DRAG_TOP_TARGET_Y:         int = 138
RESIZE_DRAG_BOTTOM_TARGET_Y:      int = 258

EXPECTED_TOP_SNAPPED_Y:           int = 150
EXPECTED_BOTTOM_SNAPPED_Y:        int = 270
EXPECTED_INITIAL_HEIGHT:          int = 120
EXPECTED_NESTING_LEVEL_0:         int = 0
EXPECTED_NESTING_LEVEL_1:         int = 1
EXPECTED_NESTING_LEVEL_2:         int = 2


class TestSDExecution(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Execution Specifications (UmlSDExecution).
    Tests creation, geometry calculation, nesting levels, message attachment snapping,
    and interactive sizing drag snapping.
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

    def testExecutionCreationAndGeometry(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1,
            nestingLevel=EXPECTED_NESTING_LEVEL_0
        )
        lifeLine.addExecution(execution=execution)

        self.assertEqual(EXECUTION_START_Y_1, execution.startY)
        self.assertEqual(EXECUTION_END_Y_1, execution.endY)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, execution.nestingLevel)
        self.assertEqual(self._preferences.executionWidth, execution.GetWidth())
        self.assertEqual(EXPECTED_INITIAL_HEIGHT, execution.GetHeight())
        self.assertEqual(round(lifeLine.GetX()), round(execution.GetX()))

        self.assertIsNotNone(execution.sdExecution)
        self.assertEqual(lifeLine.sdInstance, execution.sdExecution.instance)
        self.assertEqual(EXECUTION_START_Y_1, execution.sdExecution.startTime)
        self.assertEqual(EXECUTION_END_Y_1, execution.sdExecution.endTime)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, execution.sdExecution.nestingLevel)

    def testExplicitSDExecutionInjection(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        modelExecution: SDExecution = SDExecution(
            instance=lifeLine.sdInstance,
            startTime=EXECUTION_START_Y_1,
            endTime=EXECUTION_END_Y_1,
            nestingLevel=EXPECTED_NESTING_LEVEL_0
        )

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            sdExecution=modelExecution
        )
        lifeLine.addExecution(execution=execution)

        self.assertIs(modelExecution, execution.sdExecution)
        self.assertEqual(EXECUTION_START_Y_1, execution.startY)
        self.assertEqual(EXECUTION_END_Y_1, execution.endY)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, execution.nestingLevel)

    def testSDExecutionModelSynchronizationOnPropertyChange(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        lifeLine.addExecution(execution=execution)

        newStartY: int = EXECUTION_START_Y_1 + 20
        newEndY: int = EXECUTION_END_Y_1 + 40
        newNestingLevel: int = EXPECTED_NESTING_LEVEL_1

        execution.startY = newStartY
        self.assertEqual(newStartY, execution.sdExecution.startTime)

        execution.endY = newEndY
        self.assertEqual(newEndY, execution.sdExecution.endTime)

        execution.nestingLevel = newNestingLevel
        self.assertEqual(newNestingLevel, execution.sdExecution.nestingLevel)

    def testSDExecutionSetter(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        lifeLine.addExecution(execution=execution)

        newModelExecution: SDExecution = SDExecution(
            instance=lifeLine.sdInstance,
            startTime=EXECUTION_START_Y_2,
            endTime=EXECUTION_END_Y_2,
            nestingLevel=EXPECTED_NESTING_LEVEL_1
        )

        execution.sdExecution = newModelExecution
        self.assertIs(newModelExecution, execution.sdExecution)
        self.assertEqual(EXECUTION_START_Y_2, execution.startY)
        self.assertEqual(EXECUTION_END_Y_2, execution.endY)
        self.assertEqual(EXPECTED_NESTING_LEVEL_1, execution.nestingLevel)

    def testExecutionNestingLevels(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        exec1: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        lifeLine.addExecution(execution=exec1)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, exec1.nestingLevel)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, exec1.sdExecution.nestingLevel)

        execNonOverlap: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_NON_OVERLAP,
            endY=EXECUTION_END_Y_NON_OVERLAP
        )
        lifeLine.addExecution(execution=execNonOverlap)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, execNonOverlap.nestingLevel)
        self.assertEqual(EXPECTED_NESTING_LEVEL_0, execNonOverlap.sdExecution.nestingLevel)

        exec2: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_2,
            endY=EXECUTION_END_Y_2
        )
        lifeLine.addExecution(execution=exec2)
        self.assertEqual(EXPECTED_NESTING_LEVEL_1, exec2.nestingLevel)
        self.assertEqual(EXPECTED_NESTING_LEVEL_1, exec2.sdExecution.nestingLevel)
        self.assertGreater(exec2.GetX(), exec1.GetX())

        exec3: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_3,
            endY=EXECUTION_END_Y_3
        )
        lifeLine.addExecution(execution=exec3)
        self.assertEqual(EXPECTED_NESTING_LEVEL_2, exec3.nestingLevel)
        self.assertEqual(EXPECTED_NESTING_LEVEL_2, exec3.sdExecution.nestingLevel)
        self.assertGreater(exec3.GetX(), exec2.GetX())

        lifeLine.removeExecution(execution=exec2)
        self.assertEqual(EXPECTED_NESTING_LEVEL_1, exec3.nestingLevel)
        self.assertEqual(EXPECTED_NESTING_LEVEL_1, exec3.sdExecution.nestingLevel)

    def testDeepestExecutionAtY(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        exec1: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        exec2: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_2,
            endY=EXECUTION_END_Y_2
        )
        exec3: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_3,
            endY=EXECUTION_END_Y_3
        )

        lifeLine.addExecution(execution=exec1)
        lifeLine.addExecution(execution=exec2)
        lifeLine.addExecution(execution=exec3)

        foundLevel0: Optional[UmlSDExecution] = lifeLine.getExecutionAtY(y=PROBE_Y_LEVEL_0_ONLY)
        self.assertIsNotNone(foundLevel0)
        self.assertEqual(exec1.id, cast(UmlSDExecution, foundLevel0).id)

        foundLevel1: Optional[UmlSDExecution] = lifeLine.getExecutionAtY(y=PROBE_Y_LEVEL_1_OVERLAP)
        self.assertIsNotNone(foundLevel1)
        self.assertEqual(exec2.id, cast(UmlSDExecution, foundLevel1).id)

        foundLevel2: Optional[UmlSDExecution] = lifeLine.getExecutionAtY(y=PROBE_Y_LEVEL_2_OVERLAP)
        self.assertIsNotNone(foundLevel2)
        self.assertEqual(exec3.id, cast(UmlSDExecution, foundLevel2).id)

        foundNone: Optional[UmlSDExecution] = lifeLine.getExecutionAtY(y=OUTSIDE_Y)
        self.assertIsNone(foundNone)

    def testMessageAttachmentSnapping(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        exec1: UmlSDExecution = UmlSDExecution(
            lifeLine=inst1.umlSDLifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        inst1.umlSDLifeLine.addExecution(execution=exec1)

        exec2: UmlSDExecution = UmlSDExecution(
            lifeLine=inst2.umlSDLifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        inst2.umlSDLifeLine.addExecution(execution=exec2)

        fromY: int = EXECUTION_START_Y_1 + 20
        toY:   int = EXECUTION_START_Y_1 + 20

        sdMessageModel: SDMessage = SDMessage(
            message='doOperation()',
            src=inst1.umlSDLifeLine.umlInstanceName.sdInstance,
            sourceY=fromY,
            dst=inst2.umlSDLifeLine.umlInstanceName.sdInstance,
            destinationY=toY
        )

        message: UmlSDMessage = UmlSDMessage(
            sdMessage=sdMessageModel,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        message.umlFrame = self._diagramFrame
        inst1.umlSDLifeLine.addMessage(umlSDMessage=message, destinationLifeLine=inst2.umlSDLifeLine)
        message.fromY = fromY
        message.toY = toY

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        message.OnMoveLink(dc=dc)

        expectedStartX: int = round(exec1.GetX() + (exec1.GetWidth() / 2.0))
        expectedEndX:   int = round(exec2.GetX() - (exec2.GetWidth() / 2.0))

        actualStartX: int = round(message.lineControlPoints[0].x)
        actualEndX:   int = round(message.lineControlPoints[-1].x)

        self.assertEqual(expectedStartX, actualStartX)
        self.assertEqual(expectedEndX, actualEndX)

    def testReflexiveMessageAttachmentSnapping(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)

        exec1: UmlSDExecution = UmlSDExecution(
            lifeLine=inst1.umlSDLifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        inst1.umlSDLifeLine.addExecution(execution=exec1)

        fromY: int = EXECUTION_START_Y_1 + 20
        toY:   int = EXECUTION_START_Y_1 + 60

        sdMessageModel: SDMessage = SDMessage(
            message='selfCall()',
            src=inst1.umlSDLifeLine.umlInstanceName.sdInstance,
            sourceY=fromY,
            dst=inst1.umlSDLifeLine.umlInstanceName.sdInstance,
            destinationY=toY
        )

        message: UmlSDMessage = UmlSDMessage(
            sdMessage=sdMessageModel,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        message.umlFrame = self._diagramFrame
        inst1.umlSDLifeLine.addMessage(umlSDMessage=message, destinationLifeLine=inst1.umlSDLifeLine)
        message.fromY = fromY
        message.toY = toY

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        message.OnMoveLink(dc=dc)

        expectedStartX: int = round(exec1.GetX() + (exec1.GetWidth() / 2.0))
        actualStartX:   int = round(message.lineControlPoints[0].x)

        self.assertEqual(expectedStartX, actualStartX)

    def testInteractiveSizingDragSnapping(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = inst1.umlSDLifeLine

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        lifeLine.addExecution(execution=execution)

        execution.MakeControlPoints()
        controlPoints: list[ControlPoint] = execution.GetControlPoints()
        self.assertEqual(2, len(controlPoints))

        topHandle:    ControlPoint = controlPoints[EXECUTION_TOP_HANDLE_INDEX]
        bottomHandle: ControlPoint = controlPoints[EXECUTION_BOTTOM_HANDLE_INDEX]

        eventHandler: UmlSDExecutionEventHandler = UmlSDExecutionEventHandler(
            umlSDExecution=execution,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=execution.GetEventHandler()
        )

        eventHandler.OnSizingBeginDragLeft(pt=topHandle, x=round(topHandle.GetX()), y=round(topHandle.GetY()))
        eventHandler.OnSizingDragLeft(
            pt=topHandle,
            draw=False,
            x=round(topHandle.GetX()),
            y=RESIZE_DRAG_TOP_TARGET_Y
        )
        eventHandler.OnSizingEndDragLeft(pt=topHandle, x=round(topHandle.GetX()), y=RESIZE_DRAG_TOP_TARGET_Y)

        self.assertEqual(EXPECTED_TOP_SNAPPED_Y, execution.startY)
        self.assertEqual(EXPECTED_TOP_SNAPPED_Y, execution.sdExecution.startTime)

        eventHandler.OnSizingBeginDragLeft(pt=bottomHandle, x=round(bottomHandle.GetX()), y=round(bottomHandle.GetY()))
        eventHandler.OnSizingDragLeft(
            pt=bottomHandle,
            draw=False,
            x=round(bottomHandle.GetX()),
            y=RESIZE_DRAG_BOTTOM_TARGET_Y
        )
        eventHandler.OnSizingEndDragLeft(pt=bottomHandle, x=round(bottomHandle.GetX()), y=RESIZE_DRAG_BOTTOM_TARGET_Y)

        self.assertEqual(EXPECTED_BOTTOM_SNAPPED_Y, execution.endY)
        self.assertEqual(EXPECTED_BOTTOM_SNAPPED_Y, execution.sdExecution.endTime)

    def testDiagramRegistrationOnAddAndRemove(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = inst1.umlSDLifeLine
        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        self.assertNotIn(execution, self._diagramFrame.umlDiagram.GetShapeList())

        lifeLine.addExecution(execution=execution)
        self.assertIn(execution, self._diagramFrame.umlDiagram.GetShapeList())

        lifeLine.removeExecution(execution=execution)
        self.assertNotIn(execution, self._diagramFrame.umlDiagram.GetShapeList())

    def testAutoGenerateExecutionOnMessageCreation(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        handler: SDMessageCreationHandler = SDMessageCreationHandler(
            sequenceDiagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        handler.enableMessageCreation = True

        click1: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst1.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_1_X, y=EXECUTION_START_Y_1)
        )
        click2: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst2.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_2_X, y=EXECUTION_START_Y_1)
        )

        handler._lifeLineClicked(clickDetails=click1)
        handler._lifeLineClicked(clickDetails=click2)

        self.assertEqual(1, len(inst2.umlSDLifeLine.executions))
        createdExec: UmlSDExecution = inst2.umlSDLifeLine.executions[0]
        self.assertIn(createdExec, self._diagramFrame.umlDiagram.GetShapeList())
        self.assertEqual(inst2.umlSDLifeLine.sdInstance, createdExec.sdExecution.instance)
        self.assertEqual(createdExec.startY, createdExec.sdExecution.startTime)
        self.assertEqual(createdExec.endY, createdExec.sdExecution.endTime)

    def testMessageDraggableAndExecutionSynchronization(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        handler: SDMessageCreationHandler = SDMessageCreationHandler(
            sequenceDiagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        handler.enableMessageCreation = True

        click1: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst1.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_1_X, y=EXECUTION_START_Y_1)
        )
        click2: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst2.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_2_X, y=EXECUTION_START_Y_1)
        )

        handler._lifeLineClicked(clickDetails=click1)
        handler._lifeLineClicked(clickDetails=click2)
        handler.enableMessageCreation = False

        self.assertEqual(1, len(inst1.umlSDLifeLine.messages))
        msg: UmlSDMessage = inst1.umlSDLifeLine.messages[0]
        self.assertTrue(msg.Draggable())
        self.assertIsNotNone(msg.execution)

        execution: UmlSDExecution = msg.execution
        initialDuration: int = execution.endY - execution.startY

        targetDragY: int = EXECUTION_START_Y_1 + (self._preferences.timeStepHeight * 2)
        msgHandler = msg.GetEventHandler()
        msgHandler.OnBeginDragLeft(x=INSTANCE_1_X + 50, y=EXECUTION_START_Y_1)
        msgHandler.OnDragLeft(draw=False, x=INSTANCE_1_X + 50, y=targetDragY)
        msgHandler.OnEndDragLeft(x=INSTANCE_1_X + 50, y=targetDragY)

        expectedNewY: int = self._layoutEngine.computeTimeStepY(
            headerBottomY=inst1.umlSDLifeLine.rectangle.top,
            timeStepIndex=self._layoutEngine.computeNearestTimeStepIndex(
                headerBottomY=inst1.umlSDLifeLine.rectangle.top,
                targetY=targetDragY
            )
        )
        self.assertEqual(expectedNewY, msg.fromY)
        self.assertEqual(expectedNewY, msg.toY)
        self.assertEqual(expectedNewY, execution.startY)
        self.assertEqual(expectedNewY + initialDuration, execution.endY)
        self.assertEqual(expectedNewY, execution.sdExecution.startTime)
        self.assertEqual(expectedNewY + initialDuration, execution.sdExecution.endTime)

    def testMessageLinkageOnTriggerMessage(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=inst2.umlSDLifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        inst2.umlSDLifeLine.addExecution(execution=execution)

        sdMessageModel: SDMessage = SDMessage(
            message='computeTotal()',
            src=inst1.umlSDLifeLine.sdInstance,
            sourceY=EXECUTION_START_Y_1,
            dst=inst2.umlSDLifeLine.sdInstance,
            destinationY=EXECUTION_START_Y_1
        )
        message: UmlSDMessage = UmlSDMessage(
            sdMessage=sdMessageModel,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        message.execution = execution

        self.assertIs(sdMessageModel, execution.startMessage)
        self.assertIs(sdMessageModel, execution.sdExecution.startMessage)
        self.assertEqual('computeTotal()', execution.operation)
        self.assertEqual('computeTotal()', execution.sdExecution.operation)
        self.assertIsNone(execution.finishMessage)
        self.assertIsNone(execution.sdExecution.finishMessage)

    def testMessageLinkageOnReturnMessage(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=inst2.umlSDLifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        inst2.umlSDLifeLine.addExecution(execution=execution)

        callModelMessage: SDMessage = SDMessage(
            message='computeTotal()',
            src=inst1.umlSDLifeLine.sdInstance,
            sourceY=EXECUTION_START_Y_1,
            dst=inst2.umlSDLifeLine.sdInstance,
            destinationY=EXECUTION_START_Y_1
        )
        callMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=callModelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        callMessage.execution = execution

        returnModelMessage: SDMessage = SDMessage(
            message='totalAmount',
            src=inst2.umlSDLifeLine.sdInstance,
            sourceY=EXECUTION_END_Y_1,
            dst=inst1.umlSDLifeLine.sdInstance,
            destinationY=EXECUTION_END_Y_1
        )
        returnMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=returnModelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.RETURN
        )
        returnMessage.execution = execution

        self.assertIs(callModelMessage, execution.startMessage)
        self.assertIs(callModelMessage, execution.sdExecution.startMessage)
        self.assertIs(returnModelMessage, execution.finishMessage)
        self.assertIs(returnModelMessage, execution.sdExecution.finishMessage)
        self.assertEqual('computeTotal()', execution.operation)

    def testOperationPropertyExplicit(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        execution: UmlSDExecution = UmlSDExecution(
            lifeLine=inst1.umlSDLifeLine,
            startY=EXECUTION_START_Y_1,
            endY=EXECUTION_END_Y_1
        )
        self.assertIsNone(execution.operation)

        explicitOperation: str = 'executeOrder()'
        execution.operation = explicitOperation
        self.assertEqual(explicitOperation, execution.operation)
        self.assertEqual(explicitOperation, execution.sdExecution.operation)

    def testAutoGenerateExecutionLinksStartAndFinishMessages(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        handler: SDMessageCreationHandler = SDMessageCreationHandler(
            sequenceDiagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        handler.enableMessageCreation = True

        callClick1: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst1.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_1_X, y=EXECUTION_START_Y_1)
        )
        callClick2: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst2.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_2_X, y=EXECUTION_START_Y_1)
        )

        handler._lifeLineClicked(clickDetails=callClick1)
        handler._lifeLineClicked(clickDetails=callClick2)

        self.assertEqual(1, len(inst2.umlSDLifeLine.executions))
        createdExec: UmlSDExecution = inst2.umlSDLifeLine.executions[0]
        self.assertEqual(1, len(inst1.umlSDLifeLine.messages))
        callMsg: UmlSDMessage = inst1.umlSDLifeLine.messages[0]

        self.assertIs(callMsg.sdMessage, createdExec.startMessage)
        self.assertEqual(callMsg.sdMessage.message, createdExec.operation)
        self.assertIsNone(createdExec.finishMessage)

        handler.messageType = SDMessageType.RETURN
        returnClick1: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst2.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_2_X, y=EXECUTION_START_Y_1 + self._preferences.timeStepHeight)
        )
        returnClick2: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst1.umlSDLifeLine,
            clickPosition=UmlPosition(x=INSTANCE_1_X, y=EXECUTION_START_Y_1 + self._preferences.timeStepHeight)
        )

        handler._lifeLineClicked(clickDetails=returnClick1)
        handler._lifeLineClicked(clickDetails=returnClick2)
        handler.enableMessageCreation = False

        self.assertEqual(2, len(inst2.umlSDLifeLine.messages))
        returnMsg: UmlSDMessage = inst2.umlSDLifeLine.messages[1]
        self.assertIs(returnMsg.sdMessage, createdExec.finishMessage)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestSDExecution))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
