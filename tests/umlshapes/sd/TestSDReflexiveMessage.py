from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import ClientDC
from wx import Point

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW
from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage

from umlshapes.commands.DeleteSDMessageCommand import DeleteSDMessageCommand
from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.UmlSDMessage import LineControlPoints
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.sd.eventhandlers.UmlSDMessageEventHandler import UmlSDMessageEventHandler

INITIAL_FROM_Y: int = 100
INITIAL_TO_Y:   int = 140
MOVED_X:        int = 250


class TestSDReflexiveMessage(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Reflexive (Self-call) Messages.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._preferences:     UmlPreferences       = UmlPreferences()
        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        self._diagramFrame.Destroy()
        super().tearDown()

    def _createTestInstance(self, name: str, x: int = 100, y: int = 50) -> UmlSDInstance:
        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = name

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        umlSDInstance.SetX(x)
        umlSDInstance.SetY(y)
        umlSDInstance.umlSDLifeLine.SetX(x)
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)
        return umlSDInstance

    def testReflexiveMessageCreationAndGeometry(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=INITIAL_FROM_Y,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=INITIAL_TO_Y
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = INITIAL_FROM_Y
        umlSDMessage.toY   = INITIAL_TO_Y

        umlSDMessage.setReflexiveMessagePoints(lifeLineX=lifeLineX, fromY=INITIAL_FROM_Y, toY=INITIAL_TO_Y)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)

        self.assertTrue(umlSDMessage.isReflexiveMessage)
        lineControlPoints: LineControlPoints = umlSDMessage.lineControlPoints
        assert lineControlPoints is not None
        self.assertEqual(len(lineControlPoints), 4)

        loopWidth: int = self._preferences.reflexiveMessageWidth
        point0: Point = lineControlPoints[0]
        point1: Point = lineControlPoints[1]
        point2: Point = lineControlPoints[2]
        point3: Point = lineControlPoints[3]

        self.assertEqual(point0.x, lifeLineX)
        self.assertEqual(point0.y, INITIAL_FROM_Y)
        self.assertEqual(point1.x, lifeLineX + loopWidth)
        self.assertEqual(point1.y, INITIAL_FROM_Y)
        self.assertEqual(point2.x, lifeLineX + loopWidth)
        self.assertEqual(point2.y, INITIAL_TO_Y)
        self.assertEqual(point3.x, lifeLineX)
        self.assertEqual(point3.y, INITIAL_TO_Y)

    def testReflexiveMessageHorizontalParticipantMovement(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=INITIAL_FROM_Y,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=INITIAL_TO_Y
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = INITIAL_FROM_Y
        umlSDMessage.toY   = INITIAL_TO_Y

        dc: ClientDC = ClientDC(self._diagramFrame)
        self._diagramFrame.PrepareDC(dc)
        umlSDMessage.OnMoveLink(dc=dc)

        umlSDInstance.SetX(MOVED_X)
        lifeLine.SetX(MOVED_X)
        umlSDMessage.OnMoveLink(dc=dc)

        loopWidth: int = self._preferences.reflexiveMessageWidth
        lineControlPoints: LineControlPoints = umlSDMessage.lineControlPoints
        assert lineControlPoints is not None
        point0: Point = lineControlPoints[0]
        point1: Point = lineControlPoints[1]
        point2: Point = lineControlPoints[2]
        point3: Point = lineControlPoints[3]

        self.assertEqual(point0.x, MOVED_X)
        self.assertEqual(point1.x, MOVED_X + loopWidth)
        self.assertEqual(point2.x, MOVED_X + loopWidth)
        self.assertEqual(point3.x, MOVED_X)

    def testReflexiveMessageVerticalDragSnapping(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=INITIAL_FROM_Y,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=INITIAL_TO_Y
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = INITIAL_FROM_Y
        umlSDMessage.toY   = INITIAL_TO_Y

        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(eventHandler)

        expectedTimeStepHeight: int = 40
        initialSpan: int = INITIAL_TO_Y - INITIAL_FROM_Y

        eventHandler.OnBeginDragLeft(x=100, y=INITIAL_FROM_Y)
        targetY: int = INITIAL_FROM_Y + (expectedTimeStepHeight * 2)
        eventHandler.OnDragLeft(draw=False, x=100, y=targetY)
        eventHandler.OnEndDragLeft(x=100, y=targetY)

        self.assertEqual(umlSDMessage.toY - umlSDMessage.fromY, initialSpan)
        self.assertTrue(umlSDMessage.fromY > INITIAL_FROM_Y)

    def testReturnControlPointDragResizesMessage(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=INITIAL_FROM_Y,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=INITIAL_TO_Y
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = INITIAL_FROM_Y
        umlSDMessage.toY   = INITIAL_TO_Y
        umlSDMessage.setReflexiveMessagePoints(lifeLineX=100, fromY=INITIAL_FROM_Y, toY=INITIAL_TO_Y)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)
        umlSDMessage.Select(True)

        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(eventHandler)

        controlPoints = umlSDMessage.GetControlPoints()
        self.assertEqual(len(controlPoints), 4)
        returnPoint = controlPoints[3]
        self.assertIsInstance(returnPoint, UmlLineControlPoint)

        expectedTimeStepHeight: int = 40
        newTargetY: int = INITIAL_FROM_Y + (expectedTimeStepHeight * 3)

        eventHandler.OnSizingBeginDragLeft(pt=returnPoint, x=100, y=INITIAL_TO_Y)
        eventHandler.OnSizingDragLeft(pt=returnPoint, draw=False, x=100, y=newTargetY)
        eventHandler.OnSizingEndDragLeft(pt=returnPoint, x=100, y=newTargetY)

        self.assertEqual(umlSDMessage.fromY, INITIAL_FROM_Y)
        self.assertEqual(umlSDMessage.toY, newTargetY)
        self.assertEqual(umlSDMessage.toY - umlSDMessage.fromY, expectedTimeStepHeight * 3)

    def testReturnControlPointDragUpRepositionsMessage(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        expectedTimeStepHeight: int = 40
        startFromY: int = INITIAL_FROM_Y + (expectedTimeStepHeight * 2)
        startToY:   int = startFromY + expectedTimeStepHeight

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=startFromY,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=startToY
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = startFromY
        umlSDMessage.toY   = startToY
        umlSDMessage.setReflexiveMessagePoints(lifeLineX=100, fromY=startFromY, toY=startToY)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)
        umlSDMessage.Select(True)

        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(eventHandler)

        controlPoints = umlSDMessage.GetControlPoints()
        returnPoint = controlPoints[3]

        dragUpTargetY: int = INITIAL_FROM_Y + expectedTimeStepHeight

        eventHandler.OnSizingBeginDragLeft(pt=returnPoint, x=100, y=startToY)
        eventHandler.OnSizingDragLeft(pt=returnPoint, draw=False, x=100, y=dragUpTargetY)
        eventHandler.OnSizingEndDragLeft(pt=returnPoint, x=100, y=dragUpTargetY)

        self.assertEqual(umlSDMessage.toY, dragUpTargetY)
        self.assertEqual(umlSDMessage.fromY, INITIAL_FROM_Y)
        self.assertEqual(umlSDMessage.toY - umlSDMessage.fromY, expectedTimeStepHeight)

    def testCornerControlPointHorizontalResize(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=INITIAL_FROM_Y,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=INITIAL_TO_Y
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = INITIAL_FROM_Y
        umlSDMessage.toY   = INITIAL_TO_Y
        umlSDMessage.setReflexiveMessagePoints(lifeLineX=100, fromY=INITIAL_FROM_Y, toY=INITIAL_TO_Y)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)
        umlSDMessage.Select(True)

        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(eventHandler)

        controlPoints = umlSDMessage.GetControlPoints()
        cornerPoint = controlPoints[2]

        eventHandler.OnSizingBeginDragLeft(pt=cornerPoint, x=150, y=INITIAL_TO_Y)
        eventHandler.OnSizingDragLeft(pt=cornerPoint, draw=False, x=220, y=INITIAL_TO_Y)
        eventHandler.OnSizingEndDragLeft(pt=cornerPoint, x=220, y=INITIAL_TO_Y)

        self.assertEqual(umlSDMessage.loopWidth, 120)

        lineControlPoints: LineControlPoints = umlSDMessage.lineControlPoints
        assert lineControlPoints is not None
        self.assertEqual(lineControlPoints[1].x, 220)
        self.assertEqual(lineControlPoints[2].x, 220)

    def testReflexiveMessageDeleteAndUndo(self):
        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=100)
        lifeLine: UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=INITIAL_FROM_Y,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=INITIAL_TO_Y
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = INITIAL_FROM_Y
        umlSDMessage.toY   = INITIAL_TO_Y
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)

        deleteCommand: DeleteSDMessageCommand = DeleteSDMessageCommand(
            partialName='deleteReflexiveMessage',
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self.assertTrue(deleteCommand.Do())
        self.assertNotIn(umlSDMessage, self._diagramFrame.umlDiagram.GetShapeList())
        self.assertNotIn(umlSDMessage, lifeLine.GetLines())

        self.assertTrue(deleteCommand.Undo())
        self.assertIn(umlSDMessage, self._diagramFrame.umlDiagram.GetShapeList())
        self.assertIn(umlSDMessage, lifeLine.GetLines())


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDReflexiveMessage))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
