
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import ClientDC
from wx import Point

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage

from umlshapes.commands.DeleteSDMessageCommand import DeleteSDMessageCommand

from umlshapes.lib.ogl import ControlPoint
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

INITIAL_FROM_Y:             int = 100
INITIAL_TO_Y:               int = 140
MOVED_X:                    int = 250
EXPECTED_TIME_STEP_HEIGHT:  int = 40
RESIZED_LOOP_WIDTH:         int = 120
INSTANCE_DEFAULT_X:         int = 100
INSTANCE_DEFAULT_Y:         int = 50
CORNER_CONTROL_POINT_INDEX: int = 2
RETURN_CONTROL_POINT_INDEX: int = 3


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

    def testReflexiveMessageCreationAndGeometry(self):

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine
        lifeLineX:     int           = round(lifeLine.GetX())

        umlSDMessage: UmlSDMessage = self._createReflexiveMessage(lifeLine=lifeLine)

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

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        umlSDMessage: UmlSDMessage = self._createReflexiveMessage(lifeLine=lifeLine, initializePoints=False)

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

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        umlSDMessage: UmlSDMessage = self._createReflexiveMessage(lifeLine=lifeLine, initializePoints=False)
        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        initialSpan: int = INITIAL_TO_Y - INITIAL_FROM_Y

        eventHandler.OnBeginDragLeft(x=INSTANCE_DEFAULT_X, y=INITIAL_FROM_Y)
        targetY: int = INITIAL_FROM_Y + (EXPECTED_TIME_STEP_HEIGHT * 2)
        eventHandler.OnDragLeft(draw=False, x=INSTANCE_DEFAULT_X, y=targetY)
        eventHandler.OnEndDragLeft(x=INSTANCE_DEFAULT_X, y=targetY)

        self.assertEqual(umlSDMessage.toY - umlSDMessage.fromY, initialSpan)
        self.assertTrue(umlSDMessage.fromY > INITIAL_FROM_Y)

    def testReturnControlPointDragResizesMessage(self):

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine
        umlSDMessage:  UmlSDMessage  = self._createReflexiveMessage(lifeLine=lifeLine)
        umlSDMessage.Select(True)

        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        controlPoints: list[ControlPoint] = umlSDMessage.GetControlPoints()
        self.assertEqual(len(controlPoints), 4)
        returnPoint: ControlPoint = controlPoints[RETURN_CONTROL_POINT_INDEX]
        self.assertIsInstance(returnPoint, UmlLineControlPoint)

        newTargetY: int = INITIAL_FROM_Y + (EXPECTED_TIME_STEP_HEIGHT * 3)
        self._simulateSizingDrag(
            eventHandler=eventHandler,
            point=returnPoint,
            startX=INSTANCE_DEFAULT_X,
            startY=INITIAL_TO_Y,
            targetX=INSTANCE_DEFAULT_X,
            targetY=newTargetY
        )

        self.assertEqual(umlSDMessage.fromY, INITIAL_FROM_Y)
        self.assertEqual(umlSDMessage.toY, newTargetY)
        self.assertEqual(umlSDMessage.toY - umlSDMessage.fromY, EXPECTED_TIME_STEP_HEIGHT * 3)

    def testReturnControlPointDragUpRepositionsMessage(self):

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        startFromY: int = INITIAL_FROM_Y + (EXPECTED_TIME_STEP_HEIGHT * 2)
        startToY:   int = startFromY + EXPECTED_TIME_STEP_HEIGHT

        umlSDMessage: UmlSDMessage = self._createReflexiveMessage(lifeLine=lifeLine, fromY=startFromY, toY=startToY)
        umlSDMessage.Select(True)

        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        controlPoints: list[ControlPoint] = umlSDMessage.GetControlPoints()
        returnPoint: ControlPoint = controlPoints[RETURN_CONTROL_POINT_INDEX]

        dragUpTargetY: int = INITIAL_FROM_Y + EXPECTED_TIME_STEP_HEIGHT
        self._simulateSizingDrag(
            eventHandler=eventHandler,
            point=returnPoint,
            startX=INSTANCE_DEFAULT_X,
            startY=startToY,
            targetX=INSTANCE_DEFAULT_X,
            targetY=dragUpTargetY
        )

        self.assertEqual(umlSDMessage.toY, dragUpTargetY)
        self.assertEqual(umlSDMessage.fromY, INITIAL_FROM_Y)
        self.assertEqual(umlSDMessage.toY - umlSDMessage.fromY, EXPECTED_TIME_STEP_HEIGHT)

    def testCornerControlPointHorizontalResize(self):

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        umlSDMessage: UmlSDMessage = self._createReflexiveMessage(lifeLine=lifeLine)
        umlSDMessage.Select(True)

        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        controlPoints: list[ControlPoint] = umlSDMessage.GetControlPoints()
        cornerPoint:   ControlPoint       = controlPoints[CORNER_CONTROL_POINT_INDEX]

        self._simulateSizingDrag(
            eventHandler=eventHandler,
            point=cornerPoint,
            startX=150,
            startY=INITIAL_TO_Y,
            targetX=220,
            targetY=INITIAL_TO_Y
        )

        self.assertEqual(umlSDMessage.loopWidth, RESIZED_LOOP_WIDTH)

        lineControlPoints: LineControlPoints = umlSDMessage.lineControlPoints
        assert lineControlPoints is not None

        self.assertEqual(lineControlPoints[1].x, 220)
        self.assertEqual(lineControlPoints[2].x, 220)

    def testReflexiveMessageDeleteAndUndo(self):

        umlSDInstance: UmlSDInstance = self._createTestInstance(name='instance1', x=INSTANCE_DEFAULT_X)
        lifeLine:      UmlSDLifeLine = umlSDInstance.umlSDLifeLine

        umlSDMessage: UmlSDMessage = self._createReflexiveMessage(lifeLine=lifeLine, initializePoints=False)
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

    def _createTestInstance(self, name: str, x: int = INSTANCE_DEFAULT_X, y: int = INSTANCE_DEFAULT_Y) -> UmlSDInstance:
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

    def _createReflexiveMessage(
        self,
        lifeLine: UmlSDLifeLine,
        fromY: int = INITIAL_FROM_Y,
        toY: int = INITIAL_TO_Y,
        initializePoints: bool = True
    ) -> UmlSDMessage:
        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=fromY,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=toY
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=SDMessageType.SYNCHRONOUS
        )
        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = fromY
        umlSDMessage.toY   = toY

        if initializePoints:
            lifeLineX: int = round(lifeLine.GetX())
            umlSDMessage.setReflexiveMessagePoints(lifeLineX=lifeLineX, fromY=fromY, toY=toY)
            self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
            umlSDMessage.Show(True)

        return umlSDMessage

    def _attachEventHandler(self, umlSDMessage: UmlSDMessage) -> UmlSDMessageEventHandler:
        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(eventHandler)
        return eventHandler

    def _simulateSizingDrag(
        self,
        eventHandler: UmlSDMessageEventHandler,
        point: ControlPoint,
        startX: int,
        startY: int,
        targetX: int,
        targetY: int
    ):
        eventHandler.OnSizingBeginDragLeft(pt=point, x=startX, y=startY)
        eventHandler.OnSizingDragLeft(pt=point, draw=False, x=targetX, y=targetY)
        eventHandler.OnSizingEndDragLeft(pt=point, x=targetX, y=targetY)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDReflexiveMessage))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
