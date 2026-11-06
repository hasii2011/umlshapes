from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import ClientDC
from wx import MOD_CMD
from wx import MouseEvent
from wx import Point
from wx import wxEVT_MOTION

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW
from umlmodel.Note import Note
from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage

from wx.lib.ogl import ControlPoint
from wx.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.sd.SDFragmentOperator import SDFragmentOperator
from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDCombinedFragment import UmlSDCombinedFragment
from umlshapes.sd.UmlSDExecution import UmlSDExecution
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.eventhandlers.UmlSDMessageEventHandler import UmlSDMessageEventHandler
from umlshapes.sd.eventhandlers.UmlSdInstanceEventHandler import UmlSdInstanceEventHandler
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.types.UmlPosition import UmlPosition

INITIAL_LIFELINE_LENGTH: int = 360
NEW_LIFELINE_LENGTH:     int = 500
TOO_SHORT_LENGTH:        int = 20
EXPECTED_MIN_LENGTH:           int = 80
EXPECTED_CONTROL_POINT_COUNT:  int = 1
DRAG_HORIZONTAL_DELTA:         int = 50
DRAG_VERTICAL_DELTA:           int = 80
RESIZE_VERTICAL_DELTA:   int = 80


class TestSDLifeLineResizing(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Lifeline resizing and preferences.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._preferences:     UmlPreferences       = UmlPreferences()
        self._saveAutoFit:     bool                 = self._preferences.autoFitInstanceWidth
        self._preferences.autoFitInstanceWidth      = True
        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        self._preferences.autoFitInstanceWidth = self._saveAutoFit
        self._diagramFrame.Destroy()
        super().tearDown()

    def testLifeLinePreferencesDefaults(self):
        preferences: UmlPreferences = self._preferences

        self.assertTrue(preferences.autoGrowLifeLines)
        self.assertTrue(preferences.uniformLifeLineLength)

    def testLifeLineLengthModification(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='testInstance')

        initialLength: int = umlSDInstance.getLifeLineLength()
        self.assertEqual(INITIAL_LIFELINE_LENGTH, initialLength)

        instanceNameTopBefore: float = (
            umlSDInstance.instanceName.GetY() - (umlSDInstance.instanceName.GetHeight() / 2.0)
        )

        umlSDInstance.setLifeLineLength(newLength=NEW_LIFELINE_LENGTH)
        updatedLength: int = umlSDInstance.getLifeLineLength()
        self.assertEqual(NEW_LIFELINE_LENGTH, updatedLength)

        instanceNameTopAfter: float = (
            umlSDInstance.instanceName.GetY() - (umlSDInstance.instanceName.GetHeight() / 2.0)
        )
        self.assertAlmostEqual(instanceNameTopBefore, instanceNameTopAfter, places=1)

        lifeLineTopAfter: float = (
            umlSDInstance.umlSDLifeLine.GetY() - (umlSDInstance.umlSDLifeLine.GetHeight() / 2.0)
        )
        instanceNameBottomAfter: float = (
            umlSDInstance.instanceName.GetY() + (umlSDInstance.instanceName.GetHeight() / 2.0)
        )
        self.assertAlmostEqual(instanceNameBottomAfter, lifeLineTopAfter, places=1)

    def testMinimumLifelineLengthClamping(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='testInstanceMin')

        umlSDInstance.setLifeLineLength(newLength=TOO_SHORT_LENGTH)
        self.assertEqual(EXPECTED_MIN_LENGTH, umlSDInstance.getLifeLineLength())

    def testMakeControlPoints(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='testInstanceCP')

        umlSDInstance.MakeControlPoints()
        self.assertEqual(EXPECTED_CONTROL_POINT_COUNT, len(umlSDInstance.controlPoints))

        expectedYOffset: float = (
            umlSDInstance.umlSDLifeLine.GetY()
            + (umlSDInstance.umlSDLifeLine.GetHeight() / 2.0)
            - umlSDInstance.GetY()
        )
        actualYOffset: float = umlSDInstance.controlPoints[0]._yoffset
        self.assertAlmostEqual(expectedYOffset, actualYOffset, places=1)

        umlSDInstance.DeleteControlPoints()
        self.assertEqual(0, len(umlSDInstance.controlPoints))

    def testSetAllLifeLinesLengthOnFrame(self):
        umlSDInstance1: UmlSDInstance = self._createSDInstance(name='instance1')
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance1)

        umlSDInstance2: UmlSDInstance = self._createSDInstance(name='instance2')
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance2)

        self._diagramFrame.umlDiagram.AddShape(umlSDInstance1)
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance2)

        instances: list[UmlSDInstance] = self._diagramFrame.getSDInstances()
        self.assertEqual(2, len(instances))

        self._diagramFrame.setAllLifeLinesLength(length=NEW_LIFELINE_LENGTH)

        self.assertEqual(NEW_LIFELINE_LENGTH, umlSDInstance1.getLifeLineLength())
        self.assertEqual(NEW_LIFELINE_LENGTH, umlSDInstance2.getLifeLineLength())

    def testInstanceNameSelectionAndDrag(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='testSelectionInstance')
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)

        eventHandler: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=umlSDInstance,
            previousEventHandler=umlSDInstance.GetEventHandler()
        )
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlSDInstance.SetEventHandler(eventHandler)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        umlSDInstance.Move(dc, 150, 250)

        self.assertFalse(umlSDInstance.Selected())
        self.assertEqual(0, len(umlSDInstance.controlPoints))

        # Clicking the instance name header selects the composite shape
        headerX: int = round(umlSDInstance.instanceName.GetX())
        headerY: int = round(umlSDInstance.instanceName.GetY())
        umlSDInstance.instanceName.GetEventHandler().OnLeftClick(headerX, headerY)

        self.assertTrue(umlSDInstance.Selected())
        self.assertEqual(EXPECTED_CONTROL_POINT_COUNT, len(umlSDInstance.controlPoints))

        controlPoint: ControlPoint = umlSDInstance.controlPoints[0]
        expectedY: float = (
            umlSDInstance.umlSDLifeLine.GetY()
            + (umlSDInstance.umlSDLifeLine.GetHeight() / 2.0)
        )
        self.assertAlmostEqual(expectedY, controlPoint.GetY(), places=1)

        # Dragging on the instance name moves the composite horizontally
        startX: int = round(umlSDInstance.GetX())
        umlSDInstance.instanceName.GetEventHandler().OnBeginDragLeft(startX, headerY)
        umlSDInstance.instanceName.GetEventHandler().OnDragLeft(True, startX + DRAG_HORIZONTAL_DELTA, headerY)
        umlSDInstance.instanceName.GetEventHandler().OnEndDragLeft(startX + DRAG_HORIZONTAL_DELTA, headerY)

        self.assertNotEqual(startX, round(umlSDInstance.GetX()))

    def testLifeLineSelectionAndDrag(self):
        umlSDInstance: UmlSDInstance = self._createSDInstance(name='testLifeLineDragInstance')
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)

        eventHandler: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=umlSDInstance,
            previousEventHandler=umlSDInstance.GetEventHandler()
        )
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlSDInstance.SetEventHandler(eventHandler)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        umlSDInstance.Move(dc, 150, 250)

        # Clicking the lifeline selects the composite shape
        lifeLineX: int = round(umlSDInstance.umlSDLifeLine.GetX())
        lifeLineY: int = round(umlSDInstance.umlSDLifeLine.GetY())
        umlSDInstance.umlSDLifeLine.GetEventHandler().OnLeftClick(lifeLineX, lifeLineY)

        self.assertTrue(umlSDInstance.Selected())
        self.assertEqual(EXPECTED_CONTROL_POINT_COUNT, len(umlSDInstance.controlPoints))

        # Dragging on the lifeline moves the composite horizontally
        startX: int = round(umlSDInstance.GetX())
        umlSDInstance.umlSDLifeLine.GetEventHandler().OnBeginDragLeft(startX, lifeLineY)
        umlSDInstance.umlSDLifeLine.GetEventHandler().OnDragLeft(True, startX + DRAG_HORIZONTAL_DELTA, lifeLineY)
        umlSDInstance.umlSDLifeLine.GetEventHandler().OnEndDragLeft(startX + DRAG_HORIZONTAL_DELTA, lifeLineY)

        self.assertNotEqual(startX, round(umlSDInstance.GetX()))

    def testInteractiveLifelineSizingDrag(self):
        umlSDInstance1: UmlSDInstance = self._createSDInstance(name='instance1')
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance1)
        umlSDInstance1.Show(True)

        umlSDInstance2: UmlSDInstance = self._createSDInstance(name='instance2')
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance2)
        umlSDInstance2.Show(True)

        self._diagramFrame.umlDiagram.AddShape(umlSDInstance1)
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance2)
        umlSDInstance1.Show(True)
        umlSDInstance2.Show(True)

        handler1: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=umlSDInstance1,
            previousEventHandler=umlSDInstance1.GetEventHandler()
        )
        handler1.umlPubSubEngine = self._umlPubSubEngine
        umlSDInstance1.SetEventHandler(handler1)

        handler2: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=umlSDInstance2,
            previousEventHandler=umlSDInstance2.GetEventHandler()
        )
        handler2.umlPubSubEngine = self._umlPubSubEngine
        umlSDInstance2.SetEventHandler(handler2)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        umlSDInstance1.Move(dc, 150, 250)
        umlSDInstance2.Move(dc, 350, 250)

        initialLength: int = umlSDInstance1.getLifeLineLength()

        # Select instance 1
        umlSDInstance1.instanceName.GetEventHandler().OnLeftClick(150, 70)
        self.assertEqual(EXPECTED_CONTROL_POINT_COUNT, len(umlSDInstance1.controlPoints))

        controlPoint: ControlPoint = umlSDInstance1.controlPoints[0]
        dragTargetY: int = round(controlPoint.GetY() + RESIZE_VERTICAL_DELTA)

        controlPoint.GetEventHandler().OnBeginDragLeft(round(controlPoint.GetX()), round(controlPoint.GetY()))
        controlPoint.GetEventHandler().OnDragLeft(True, round(controlPoint.GetX()), dragTargetY)
        controlPoint.GetEventHandler().OnEndDragLeft(round(controlPoint.GetX()), dragTargetY)

        expectedLength: int = initialLength + RESIZE_VERTICAL_DELTA
        self.assertEqual(expectedLength, umlSDInstance1.getLifeLineLength())
        self.assertEqual(expectedLength, umlSDInstance2.getLifeLineLength())

    def testMultiSelectHorizontalDragMovesInstancesFragmentAndNote(self):
        instance1: UmlSDInstance = self._createSDInstance(name='Customer')
        self._diagramFrame.umlDiagram.AddShape(instance1)
        instance1.Show(True)

        handler1: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=instance1,
            previousEventHandler=instance1.GetEventHandler()
        )
        handler1.umlPubSubEngine = self._umlPubSubEngine
        instance1.SetEventHandler(handler1)

        instance2: UmlSDInstance = self._createSDInstance(name='OrderService')
        self._diagramFrame.umlDiagram.AddShape(instance2)
        instance2.Show(True)

        handler2: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=instance2,
            previousEventHandler=instance2.GetEventHandler()
        )
        handler2.umlPubSubEngine = self._umlPubSubEngine
        instance2.SetEventHandler(handler2)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        instance1.position = UmlPosition(x=100, y=50)
        instance2.position = UmlPosition(x=320, y=50)

        lifeLine1: UmlSDLifeLine = instance1.umlSDLifeLine
        lifeLine2: UmlSDLifeLine = instance2.umlSDLifeLine

        execution2: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine2,
            startY=140,
            endY=220
        )
        lifeLine2.addExecution(execution=execution2)

        modelMessage: SDMessage = SDMessage(
            message='placeOrder()',
            src=instance1.sdInstance,
            sourceY=140,
            dst=instance2.sdInstance,
            destinationY=140
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine1.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine2)
        umlSDMessage.fromY = 140
        umlSDMessage.toY = 140
        umlSDMessage.execution = execution2
        umlSDMessage.OnMoveLink(dc=dc)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.ALT,
            x=210.0,
            y=180.0,
            width=260,
            height=120
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        noteModel: Note = Note(content='Order note')
        umlNote: UmlNote = UmlNote(note=noteModel)
        umlNote.umlFrame = self._diagramFrame
        umlNote.position = UmlPosition(x=450, y=100)
        self._diagramFrame.umlDiagram.AddShape(umlNote)
        umlNote.Show(True)

        # Multi-select instance1, instance2, fragment, note, and message
        instance1.Select(True, dc)
        instance2.Select(True, dc)
        fragment.Select(True, dc)
        umlNote.Select(True, dc)
        umlSDMessage.Select(True, dc)

        initialInst1Pos: UmlPosition = instance1.position
        initialInst2Pos: UmlPosition = instance2.position
        initialLifeLine2X: int = round(lifeLine2.GetX())
        initialExec2X: int = round(execution2.GetX())
        initialFragmentPos: UmlPosition = fragment.position
        initialNotePos: UmlPosition = umlNote.position

        startX: int = round(instance1.GetX())
        headerY: int = round(instance1.instanceName.GetY())

        instance1.instanceName.GetEventHandler().OnBeginDragLeft(startX, headerY, keys=MOD_CMD)
        instance1.instanceName.GetEventHandler().OnDragLeft(True, startX + DRAG_HORIZONTAL_DELTA, headerY + 30, keys=MOD_CMD)
        instance1.instanceName.GetEventHandler().OnEndDragLeft(startX + DRAG_HORIZONTAL_DELTA, headerY + 30, keys=MOD_CMD)

        self.assertEqual(initialInst1Pos.x + DRAG_HORIZONTAL_DELTA, instance1.position.x)
        self.assertEqual(initialInst1Pos.y, instance1.position.y)

        self.assertEqual(initialInst2Pos.x + DRAG_HORIZONTAL_DELTA, instance2.position.x)
        self.assertEqual(initialInst2Pos.y, instance2.position.y)
        self.assertEqual(initialLifeLine2X + DRAG_HORIZONTAL_DELTA, round(lifeLine2.GetX()))
        self.assertEqual(initialExec2X + DRAG_HORIZONTAL_DELTA, round(execution2.GetX()))

        self.assertEqual(initialFragmentPos.x + DRAG_HORIZONTAL_DELTA, fragment.position.x)
        self.assertEqual(initialFragmentPos.y, fragment.position.y)

        self.assertEqual(initialNotePos.x + DRAG_HORIZONTAL_DELTA, umlNote.position.x)
        self.assertEqual(initialNotePos.y, umlNote.position.y)

    def testRubberBandSelectionOnSequenceDiagram(self):
        """
        Verify that dragging the selection rectangle (rubber-banding) selects enclosed
        participant instances, combined fragments, and messages.
        """
        instance1: UmlSDInstance = self._createSDInstance(name='Inst1')
        self._diagramFrame.umlDiagram.AddShape(instance1)
        instance1.position = UmlPosition(x=100, y=50)
        instance1.Show(True)

        instance2: UmlSDInstance = self._createSDInstance(name='Inst2')
        self._diagramFrame.umlDiagram.AddShape(instance2)
        instance2.position = UmlPosition(x=450, y=50)
        instance2.Show(True)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.ALT,
            x=200.0,
            y=180.0,
            width=200,
            height=100
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        # Clear any selection
        for s in list(self._diagramFrame.umlDiagram.shapes):
            if hasattr(s, 'Select'):
                s.Select(False)

        # Rubber band covering instance1 and fragment only (not instance2)
        self._diagramFrame.OnDragLeft(True, 20, 20)
        moveEvent: MouseEvent = MouseEvent(wxEVT_MOTION)
        moveEvent.SetPosition(Point(x=320, y=300))
        self._diagramFrame._onSelectorMove(moveEvent)
        self._diagramFrame.OnEndDragLeft(320, 300)

        selectedShapes = self._diagramFrame.selectedShapes
        self.assertIn(instance1, selectedShapes)
        self.assertIn(fragment, selectedShapes)
        self.assertNotIn(instance2, selectedShapes)

    def testMultiSelectVerticalDragMovesMessagesExecutionsFragmentAndNote(self):
        instance1: UmlSDInstance = self._createSDInstance(name='Customer')
        self._diagramFrame.umlDiagram.AddShape(instance1)
        instance1.Show(True)

        instance2: UmlSDInstance = self._createSDInstance(name='OrderService')
        self._diagramFrame.umlDiagram.AddShape(instance2)
        instance2.Show(True)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        instance1.position = UmlPosition(x=100, y=50)
        instance2.position = UmlPosition(x=320, y=50)

        layoutEngine: SDLayoutEngine = SDLayoutEngine()
        lifeLine1: UmlSDLifeLine = instance1.umlSDLifeLine
        lifeLine2: UmlSDLifeLine = instance2.umlSDLifeLine
        headerBottomY: int = lifeLine1.rectangle.top
        msg1InitialY: int = layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=0)
        msg2InitialY: int = layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=1)

        execution1: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine2,
            startY=msg1InitialY,
            endY=msg1InitialY + 40
        )
        lifeLine2.addExecution(execution=execution1)

        execution2: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine2,
            startY=msg2InitialY,
            endY=msg2InitialY + 40
        )
        lifeLine2.addExecution(execution=execution2)

        modelMsg1: SDMessage = SDMessage(
            message='validate()',
            src=instance1.sdInstance,
            sourceY=msg1InitialY,
            dst=instance2.sdInstance,
            destinationY=msg1InitialY
        )
        msg1: UmlSDMessage = UmlSDMessage(sdMessage=modelMsg1, messageType=SDMessageType.SYNCHRONOUS)
        msg1.umlFrame = self._diagramFrame
        lifeLine1.addMessage(umlSDMessage=msg1, destinationLifeLine=lifeLine2)
        msg1.fromY = msg1InitialY
        msg1.toY   = msg1InitialY
        msg1.execution = execution1
        msg1.OnMoveLink(dc=dc)
        self._diagramFrame.umlDiagram.AddShape(msg1)
        msg1.Show(True)

        msgHandler1: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=msg1,
            previousEventHandler=msg1.GetEventHandler()
        )
        msgHandler1.umlPubSubEngine = self._umlPubSubEngine
        msg1.SetEventHandler(msgHandler1)

        modelMsg2: SDMessage = SDMessage(
            message='submitOrder()',
            src=instance1.sdInstance,
            sourceY=msg2InitialY,
            dst=instance2.sdInstance,
            destinationY=msg2InitialY
        )
        msg2: UmlSDMessage = UmlSDMessage(sdMessage=modelMsg2, messageType=SDMessageType.SYNCHRONOUS)
        msg2.umlFrame = self._diagramFrame
        lifeLine1.addMessage(umlSDMessage=msg2, destinationLifeLine=lifeLine2)
        msg2.fromY = msg2InitialY
        msg2.toY   = msg2InitialY
        msg2.execution = execution2
        msg2.OnMoveLink(dc=dc)
        self._diagramFrame.umlDiagram.AddShape(msg2)
        msg2.Show(True)

        msgHandler2: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=msg2,
            previousEventHandler=msg2.GetEventHandler()
        )
        msgHandler2.umlPubSubEngine = self._umlPubSubEngine
        msg2.SetEventHandler(msgHandler2)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.ALT,
            x=210.0,
            y=180.0,
            width=260,
            height=120
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        noteModel: Note = Note(content='Vertical drag note')
        umlNote: UmlNote = UmlNote(note=noteModel)
        umlNote.umlFrame = self._diagramFrame
        umlNote.position = UmlPosition(x=450, y=100)
        self._diagramFrame.umlDiagram.AddShape(umlNote)
        umlNote.Show(True)

        # Multi-select msg1, msg2, fragment, umlNote, and instance1
        msg1.Select(True, dc)
        msg2.Select(True, dc)
        fragment.Select(True, dc)
        umlNote.Select(True, dc)
        instance1.Select(True, dc)

        initialInst1Pos: UmlPosition = instance1.position
        initialFragmentPos: UmlPosition = fragment.position
        initialNotePos:     UmlPosition = umlNote.position

        msg1Handler: UmlSDMessageEventHandler = msgHandler1
        msg1Handler.OnBeginDragLeft(200, msg1InitialY, keys=MOD_CMD)
        msg1Handler.OnDragLeft(True, 200, msg1InitialY + DRAG_VERTICAL_DELTA, keys=MOD_CMD)
        msg1Handler.OnEndDragLeft(200, msg1InitialY + DRAG_VERTICAL_DELTA, keys=MOD_CMD)

        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, msg1.fromY)
        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, msg1.toY)
        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, execution1.startY)
        self.assertEqual(msg1InitialY + 40 + DRAG_VERTICAL_DELTA, execution1.endY)

        self.assertEqual(msg2InitialY + DRAG_VERTICAL_DELTA, msg2.fromY)
        self.assertEqual(msg2InitialY + DRAG_VERTICAL_DELTA, msg2.toY)
        self.assertEqual(msg2InitialY + DRAG_VERTICAL_DELTA, execution2.startY)
        self.assertEqual(msg2InitialY + 40 + DRAG_VERTICAL_DELTA, execution2.endY)

        self.assertEqual(initialFragmentPos.x, fragment.position.x)
        self.assertEqual(initialFragmentPos.y + DRAG_VERTICAL_DELTA, fragment.position.y)

        self.assertEqual(initialNotePos.x, umlNote.position.x)
        self.assertEqual(initialNotePos.y + DRAG_VERTICAL_DELTA, umlNote.position.y)

        self.assertEqual(initialInst1Pos, instance1.position)

    def testUndoRedoMultiSelectHorizontalDrag(self):
        """
        Verify Undo and Redo restore positions after multi-shape horizontal dragging.
        """
        instance1: UmlSDInstance = self._createSDInstance(name='User')
        self._diagramFrame.umlDiagram.AddShape(instance1)
        instance1.Show(True)

        handler1: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=instance1,
            previousEventHandler=instance1.GetEventHandler()
        )
        handler1.umlPubSubEngine = self._umlPubSubEngine
        instance1.SetEventHandler(handler1)

        instance2: UmlSDInstance = self._createSDInstance(name='Gateway')
        self._diagramFrame.umlDiagram.AddShape(instance2)
        instance2.Show(True)

        handler2: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=instance2,
            previousEventHandler=instance2.GetEventHandler()
        )
        handler2.umlPubSubEngine = self._umlPubSubEngine
        instance2.SetEventHandler(handler2)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        instance1.position = UmlPosition(x=100, y=50)
        instance2.position = UmlPosition(x=320, y=50)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.ALT,
            x=200.0,
            y=180.0,
            width=220,
            height=100
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        noteModel: Note = Note(content='Test Note')
        umlNote: UmlNote = UmlNote(note=noteModel)
        umlNote.umlFrame = self._diagramFrame
        umlNote.position = UmlPosition(x=400, y=100)
        self._diagramFrame.umlDiagram.AddShape(umlNote)
        umlNote.Show(True)

        instance1.Select(True, dc)
        instance2.Select(True, dc)
        fragment.Select(True, dc)
        umlNote.Select(True, dc)

        initialInst1Pos: UmlPosition = instance1.position
        initialInst2Pos: UmlPosition = instance2.position
        initialFragmentPos: UmlPosition = fragment.position
        initialNotePos:     UmlPosition = umlNote.position

        startX: int = round(instance1.GetX())
        headerY: int = round(instance1.instanceName.GetY())

        instance1.instanceName.GetEventHandler().OnBeginDragLeft(startX, headerY, keys=MOD_CMD)
        instance1.instanceName.GetEventHandler().OnDragLeft(True, startX + DRAG_HORIZONTAL_DELTA, headerY + 30, keys=MOD_CMD)
        instance1.instanceName.GetEventHandler().OnEndDragLeft(startX + DRAG_HORIZONTAL_DELTA, headerY + 30, keys=MOD_CMD)

        self.assertEqual(initialInst1Pos.x + DRAG_HORIZONTAL_DELTA, instance1.position.x)
        self.assertEqual(initialInst2Pos.x + DRAG_HORIZONTAL_DELTA, instance2.position.x)
        self.assertEqual(initialFragmentPos.x + DRAG_HORIZONTAL_DELTA, fragment.position.x)
        self.assertEqual(initialNotePos.x + DRAG_HORIZONTAL_DELTA, umlNote.position.x)

        # Test Undo
        self._diagramFrame.commandProcessor.Undo()
        self.assertEqual(initialInst1Pos.x, instance1.position.x)
        self.assertEqual(initialInst2Pos.x, instance2.position.x)
        self.assertEqual(initialFragmentPos.x, fragment.position.x)
        self.assertEqual(initialNotePos.x, umlNote.position.x)

        # Test Redo
        self._diagramFrame.commandProcessor.Redo()
        self.assertEqual(initialInst1Pos.x + DRAG_HORIZONTAL_DELTA, instance1.position.x)
        self.assertEqual(initialInst2Pos.x + DRAG_HORIZONTAL_DELTA, instance2.position.x)
        self.assertEqual(initialFragmentPos.x + DRAG_HORIZONTAL_DELTA, fragment.position.x)
        self.assertEqual(initialNotePos.x + DRAG_HORIZONTAL_DELTA, umlNote.position.x)

    def testUndoRedoMultiSelectVerticalDrag(self):
        """
        Verify Undo and Redo restore positions after multi-shape vertical dragging.
        """
        instance1: UmlSDInstance = self._createSDInstance(name='Customer')
        self._diagramFrame.umlDiagram.AddShape(instance1)
        instance1.Show(True)

        handler1: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=instance1,
            previousEventHandler=instance1.GetEventHandler()
        )
        handler1.umlPubSubEngine = self._umlPubSubEngine
        instance1.SetEventHandler(handler1)

        instance2: UmlSDInstance = self._createSDInstance(name='OrderService')
        self._diagramFrame.umlDiagram.AddShape(instance2)
        instance2.Show(True)

        handler2: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=instance2,
            previousEventHandler=instance2.GetEventHandler()
        )
        handler2.umlPubSubEngine = self._umlPubSubEngine
        instance2.SetEventHandler(handler2)

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        instance1.position = UmlPosition(x=100, y=50)
        instance2.position = UmlPosition(x=320, y=50)

        layoutEngine: SDLayoutEngine = SDLayoutEngine()
        lifeLine1: UmlSDLifeLine = instance1.umlSDLifeLine
        lifeLine2: UmlSDLifeLine = instance2.umlSDLifeLine

        headerBottomY: int = lifeLine1.rectangle.top
        msg1InitialY:  int = layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=0)
        msg2InitialY:  int = layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=1)

        execution1: UmlSDExecution = UmlSDExecution(
            lifeLine=lifeLine2,
            startY=msg1InitialY,
            endY=msg1InitialY + 40
        )
        lifeLine2.addExecution(execution=execution1)

        modelMsg1: SDMessage = SDMessage(
            message='validate()',
            src=instance1.sdInstance,
            sourceY=msg1InitialY,
            dst=instance2.sdInstance,
            destinationY=msg1InitialY
        )
        msg1: UmlSDMessage = UmlSDMessage(sdMessage=modelMsg1, messageType=SDMessageType.SYNCHRONOUS)
        msg1.umlFrame = self._diagramFrame
        lifeLine1.addMessage(umlSDMessage=msg1, destinationLifeLine=lifeLine2)
        msg1.fromY = msg1InitialY
        msg1.toY   = msg1InitialY
        msg1.execution = execution1
        msg1.OnMoveLink(dc=dc)
        self._diagramFrame.umlDiagram.AddShape(msg1)
        msg1.Show(True)

        msgHandler1: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=msg1,
            previousEventHandler=msg1.GetEventHandler()
        )
        msgHandler1.umlPubSubEngine = self._umlPubSubEngine
        msg1.SetEventHandler(msgHandler1)

        modelMsg2: SDMessage = SDMessage(
            message='submitOrder()',
            src=instance1.sdInstance,
            sourceY=msg2InitialY,
            dst=instance2.sdInstance,
            destinationY=msg2InitialY
        )
        msg2: UmlSDMessage = UmlSDMessage(sdMessage=modelMsg2, messageType=SDMessageType.SYNCHRONOUS)
        msg2.umlFrame = self._diagramFrame
        lifeLine1.addMessage(umlSDMessage=msg2, destinationLifeLine=lifeLine2)

        msg2.fromY = msg2InitialY
        msg2.toY   = msg2InitialY
        msg2.OnMoveLink(dc=dc)
        self._diagramFrame.umlDiagram.AddShape(msg2)
        msg2.Show(True)

        msgHandler2: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=msg2,
            previousEventHandler=msg2.GetEventHandler()
        )
        msgHandler2.umlPubSubEngine = self._umlPubSubEngine
        msg2.SetEventHandler(msgHandler2)

        fragment: UmlSDCombinedFragment = UmlSDCombinedFragment(
            operator=SDFragmentOperator.ALT,
            x=210.0,
            y=180.0,
            width=260,
            height=120
        )
        self._diagramFrame.umlDiagram.AddShape(fragment)
        fragment.umlFrame = self._diagramFrame

        noteModel: Note = Note(content='Vertical drag note')
        umlNote: UmlNote = UmlNote(note=noteModel)
        umlNote.umlFrame = self._diagramFrame
        umlNote.position = UmlPosition(x=450, y=100)
        self._diagramFrame.umlDiagram.AddShape(umlNote)
        umlNote.Show(True)

        msg1.Select(True, dc)
        msg2.Select(True, dc)
        fragment.Select(True, dc)
        umlNote.Select(True, dc)
        instance1.Select(True, dc)

        initialFragmentPos: UmlPosition = fragment.position
        initialNotePos: UmlPosition = umlNote.position

        msg1Handler: UmlSDMessageEventHandler = msgHandler1
        msg1Handler.OnBeginDragLeft(200, msg1InitialY, keys=MOD_CMD)
        msg1Handler.OnDragLeft(True, 200, msg1InitialY + DRAG_VERTICAL_DELTA, keys=MOD_CMD)
        msg1Handler.OnEndDragLeft(200, msg1InitialY + DRAG_VERTICAL_DELTA, keys=MOD_CMD)

        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, msg1.fromY)
        self.assertEqual(msg2InitialY + DRAG_VERTICAL_DELTA, msg2.fromY)
        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, execution1.startY)
        self.assertEqual(initialFragmentPos.y + DRAG_VERTICAL_DELTA, fragment.position.y)
        self.assertEqual(initialNotePos.y + DRAG_VERTICAL_DELTA, umlNote.position.y)

        # Test Undo
        self._diagramFrame.commandProcessor.Undo()
        self.assertEqual(msg1InitialY, msg1.fromY)
        self.assertEqual(msg2InitialY, msg2.fromY)
        self.assertEqual(msg1InitialY, execution1.startY)
        self.assertEqual(initialFragmentPos.y, fragment.position.y)
        self.assertEqual(initialNotePos.y, umlNote.position.y)

        # Test Redo
        self._diagramFrame.commandProcessor.Redo()
        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, msg1.fromY)
        self.assertEqual(msg2InitialY + DRAG_VERTICAL_DELTA, msg2.fromY)
        self.assertEqual(msg1InitialY + DRAG_VERTICAL_DELTA, execution1.startY)
        self.assertEqual(initialFragmentPos.y + DRAG_VERTICAL_DELTA, fragment.position.y)
        self.assertEqual(initialNotePos.y + DRAG_VERTICAL_DELTA, umlNote.position.y)

    def _createSDInstance(self, name: str) -> UmlSDInstance:
        """
        Create and initialize a UmlSDInstance attached to this test's diagram frame.

        Args:
            name: The participant instance name

        Returns:
            The created UmlSDInstance
        """
        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = name

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel
        )
        umlSDInstance.umlFrame = self._diagramFrame

        return umlSDInstance



def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDLifeLineResizing))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
