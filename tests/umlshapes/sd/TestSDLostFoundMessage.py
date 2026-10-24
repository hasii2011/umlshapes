
from typing import cast
from typing import Optional

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import ClientDC
from wx import MemoryDC
from wx import Bitmap
from wx import NullBitmap
from wx import Image
from wx import Point
from wx import Colour
from wx import BLACK_BRUSH
from wx import RED_BRUSH
from wx import WHITE_BRUSH

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import OGLInitialize
from umlshapes.lib.ogl import Shape

from umlshapes.preferences.Defaults import DEFAULT_LOST_FOUND_MESSAGE_LENGTH
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.utils.ResourceUtils import ResourceUtils
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.SDMessageCreationHandler import SDMessageCreationHandler
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDExecution import UmlSDExecution
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage

from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import LifeLineClickDetails
from umlshapes.sd.eventhandlers.UmlSDMessageEventHandler import UmlSDMessageEventHandler

INSTANCE_1_X:        int = 100
INSTANCE_2_X:        int = 320
INSTANCE_DEFAULT_Y:  int = 50
MESSAGE_START_Y_1:   int = 140
MESSAGE_DRAG_DELTA:  int = 40
CANVAS_BITMAP_WIDTH:  int = 400
CANVAS_BITMAP_HEIGHT: int = 400


class TestSDLostFoundMessage(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Lost & Found Messages conforming to OMG UML 2.5.1 Section 17.4.
    Tests creation, geometry, selection, drawing, time step snapping, and control-point resizing.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._preferences:     UmlPreferences          = UmlPreferences()
        self._layoutEngine:    SDLayoutEngine          = SDLayoutEngine()
        self._umlPubSubEngine: IUmlPubSubEngine        = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame    = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._creationHandler: SDMessageCreationHandler = SDMessageCreationHandler(
            sequenceDiagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        self._diagramFrame.Destroy()
        super().tearDown()

    def testLostMessageCreationAndEndpoints(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = inst1.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        lostMessage: UmlSDMessage = self._creationHandler.createLostMessage(
            startLifeLine=lifeLine,
            fromY=MESSAGE_START_Y_1,
            destX=lifeLineX + DEFAULT_LOST_FOUND_MESSAGE_LENGTH,
            messageName='testLostMsg'
        )

        self.assertTrue(lostMessage.isLostMessage)
        self.assertFalse(lostMessage.isFoundMessage)
        self.assertFalse(lostMessage.isReflexiveMessage)
        self.assertEqual(SDMessageType.LOST, lostMessage.messageType)
        self.assertEqual(lifeLine, lostMessage.GetFrom())
        self.assertIsNone(lostMessage.GetTo())
        self.assertEqual(lostMessage.fromY, lostMessage.toY)

        firstPoint: Point = lostMessage.lineControlPoints[0]
        lastPoint:  Point = lostMessage.lineControlPoints[-1]
        self.assertEqual(lifeLineX, firstPoint.x)
        self.assertEqual(lifeLineX + DEFAULT_LOST_FOUND_MESSAGE_LENGTH, lastPoint.x)
        self.assertEqual(lostMessage.fromY, firstPoint.y)
        self.assertEqual(lostMessage.toY, lastPoint.y)

    def testFoundMessageCreationAndEndpoints(self):
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)
        lifeLine: UmlSDLifeLine = inst2.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        foundMessage: UmlSDMessage = self._creationHandler.createFoundMessage(
            destLifeLine=lifeLine,
            toY=MESSAGE_START_Y_1,
            sourceX=lifeLineX - DEFAULT_LOST_FOUND_MESSAGE_LENGTH,
            messageName='testFoundMsg'
        )

        self.assertTrue(foundMessage.isFoundMessage)
        self.assertFalse(foundMessage.isLostMessage)
        self.assertFalse(foundMessage.isReflexiveMessage)
        self.assertEqual(SDMessageType.FOUND, foundMessage.messageType)
        self.assertIsNone(foundMessage.GetFrom())
        self.assertEqual(lifeLine, foundMessage.GetTo())
        self.assertEqual(foundMessage.fromY, foundMessage.toY)

        firstPoint: Point = foundMessage.lineControlPoints[0]
        lastPoint:  Point = foundMessage.lineControlPoints[-1]
        self.assertEqual(lifeLineX - DEFAULT_LOST_FOUND_MESSAGE_LENGTH, firstPoint.x)
        self.assertEqual(foundMessage.fromY, firstPoint.y)
        self.assertEqual(foundMessage.toY, lastPoint.y)

        self.assertIsNotNone(foundMessage.execution)
        self.assertEqual(1, len(lifeLine.executions))

    def testLostAndFoundMessageRendering(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        lostMessage: UmlSDMessage = self._creationHandler.createLostMessage(
            startLifeLine=inst1.umlSDLifeLine,
            fromY=MESSAGE_START_Y_1
        )
        foundMessage: UmlSDMessage = self._creationHandler.createFoundMessage(
            destLifeLine=inst2.umlSDLifeLine,
            toY=MESSAGE_START_Y_1 + 40
        )

        bitmap: Bitmap = Bitmap(CANVAS_BITMAP_WIDTH, CANVAS_BITMAP_HEIGHT)
        dc: MemoryDC = MemoryDC()
        dc.SelectObject(bitmap)
        dc.SetBackground(WHITE_BRUSH)
        dc.Clear()
        dc.SelectObject(NullBitmap)

        lostCirclePoint:  Point = lostMessage.lineControlPoints[-1]
        foundCirclePoint: Point = foundMessage.lineControlPoints[0]

        # 1. Lost Message: unselected then selected
        self._assertMessageRenderingAndPixel(message=lostMessage, circlePoint=lostCirclePoint, selected=False, dc=dc, bitmap=bitmap)
        self._assertMessageRenderingAndPixel(message=lostMessage, circlePoint=lostCirclePoint, selected=True, dc=dc, bitmap=bitmap)

        # 2. Found Message: unselected then selected
        self._assertMessageRenderingAndPixel(message=foundMessage, circlePoint=foundCirclePoint, selected=False, dc=dc, bitmap=bitmap)
        self._assertMessageRenderingAndPixel(message=foundMessage, circlePoint=foundCirclePoint, selected=True, dc=dc, bitmap=bitmap)

    def testLostMessageVerticalDragSnapping(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)

        lostMessage: UmlSDMessage = self._creationHandler.createLostMessage(
            startLifeLine=inst1.umlSDLifeLine,
            fromY=MESSAGE_START_Y_1
        )
        initialFromY: int = lostMessage.fromY
        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, lostMessage.GetEventHandler())

        self._simulateVerticalDrag(eventHandler=eventHandler, startX=INSTANCE_1_X, startY=initialFromY, deltaY=MESSAGE_DRAG_DELTA)

        expectedY: int = initialFromY + self._preferences.timeStepHeight
        self.assertEqual(expectedY, lostMessage.fromY)
        self.assertEqual(expectedY, lostMessage.toY)

    def testFoundMessageVerticalDragSnappingWithExecution(self):
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)

        foundMessage: UmlSDMessage = self._creationHandler.createFoundMessage(
            destLifeLine=inst2.umlSDLifeLine,
            toY=MESSAGE_START_Y_1
        )
        initialToY: int = foundMessage.toY
        associatedExecution: Optional[UmlSDExecution] = foundMessage.execution
        self.assertIsNotNone(associatedExecution)
        if associatedExecution is not None:
            self.assertEqual(initialToY, associatedExecution.startY)

        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, foundMessage.GetEventHandler())
        self._simulateVerticalDrag(eventHandler=eventHandler, startX=INSTANCE_2_X, startY=initialToY, deltaY=MESSAGE_DRAG_DELTA)

        expectedY: int = initialToY + self._preferences.timeStepHeight
        self.assertEqual(expectedY, foundMessage.toY)
        self.assertEqual(expectedY, foundMessage.fromY)
        if associatedExecution is not None:
            self.assertEqual(expectedY, associatedExecution.startY)

    def testLostMessageFreeEndpointHorizontalResize(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLineX: int = round(inst1.umlSDLifeLine.GetX())

        lostMessage: UmlSDMessage = self._creationHandler.createLostMessage(
            startLifeLine=inst1.umlSDLifeLine,
            fromY=MESSAGE_START_Y_1,
            destX=lifeLineX + DEFAULT_LOST_FOUND_MESSAGE_LENGTH
        )
        lostMessage.MakeControlPoints()
        controlPoints: list[ControlPoint] = lostMessage.GetControlPoints()
        self.assertEqual(2, len(controlPoints))
        toControlPoint: ControlPoint = controlPoints[1]

        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, lostMessage.GetEventHandler())
        targetNewX: int = lifeLineX + 150

        eventHandler.OnSizingBeginDragLeft(pt=toControlPoint, x=toControlPoint.GetX(), y=toControlPoint.GetY())
        eventHandler.OnSizingDragLeft(pt=toControlPoint, draw=True, x=targetNewX, y=toControlPoint.GetY())
        eventHandler.OnSizingEndDragLeft(pt=toControlPoint, x=targetNewX, y=toControlPoint.GetY())

        self.assertEqual(targetNewX, lostMessage.lineControlPoints[-1].x)

    def testInteractiveLostMessageWorkflow(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLineX: int = round(inst1.umlSDLifeLine.GetX())

        self._creationHandler.messageType = SDMessageType.LOST
        self._creationHandler.enableMessageCreation = True

        click1: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst1.umlSDLifeLine,
            clickPosition=UmlPosition(x=lifeLineX, y=MESSAGE_START_Y_1)
        )
        self._creationHandler._lifeLineClicked(clickDetails=click1)

        canvasClick: UmlPosition = UmlPosition(x=lifeLineX + 120, y=MESSAGE_START_Y_1)
        self._creationHandler._frameLeftClicked(self._diagramFrame, umlPosition=canvasClick)

        createdMsg: UmlSDMessage = self._getSingleCreatedMessage()
        self.assertTrue(createdMsg.isLostMessage)
        self.assertEqual(lifeLineX + 120, createdMsg.lineControlPoints[-1].x)

    def testInteractiveFoundMessageWorkflow(self):
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)
        lifeLineX: int = round(inst2.umlSDLifeLine.GetX())

        self._creationHandler.messageType = SDMessageType.FOUND
        self._creationHandler.enableMessageCreation = True

        canvasClick: UmlPosition = UmlPosition(x=lifeLineX - 110, y=MESSAGE_START_Y_1)
        self._creationHandler._frameLeftClicked(self._diagramFrame, umlPosition=canvasClick)

        click2: LifeLineClickDetails = LifeLineClickDetails(
            lifeLine=inst2.umlSDLifeLine,
            clickPosition=UmlPosition(x=lifeLineX, y=MESSAGE_START_Y_1)
        )
        self._creationHandler._lifeLineClicked(clickDetails=click2)

        createdMsg: UmlSDMessage = self._getSingleCreatedMessage()
        self.assertTrue(createdMsg.isFoundMessage)
        self.assertEqual(lifeLineX - 110, createdMsg.lineControlPoints[0].x)

    def testLostMessageDirectEndpointStretch(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = inst1.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        lostMessage: UmlSDMessage = self._creationHandler.createLostMessage(
            startLifeLine=lifeLine,
            fromY=MESSAGE_START_Y_1,
            destX=lifeLineX + DEFAULT_LOST_FOUND_MESSAGE_LENGTH
        )
        self.assertFalse(lostMessage.Selected())
        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, lostMessage.GetEventHandler())

        initialFreeX: int = lostMessage.lineControlPoints[-1].x
        targetFreeX:  int = initialFreeX + 60
        eventHandler.OnBeginDragLeft(x=initialFreeX, y=MESSAGE_START_Y_1)
        eventHandler.OnDragLeft(draw=True, x=targetFreeX, y=MESSAGE_START_Y_1)
        eventHandler.OnEndDragLeft(x=targetFreeX, y=MESSAGE_START_Y_1)

        self.assertEqual(targetFreeX, lostMessage.lineControlPoints[-1].x)

    def testFoundMessageDirectEndpointStretch(self):
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)
        lifeLine: UmlSDLifeLine = inst2.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        foundMessage: UmlSDMessage = self._creationHandler.createFoundMessage(
            destLifeLine=lifeLine,
            toY=MESSAGE_START_Y_1,
            sourceX=lifeLineX - DEFAULT_LOST_FOUND_MESSAGE_LENGTH
        )
        self.assertFalse(foundMessage.Selected())
        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, foundMessage.GetEventHandler())

        initialFreeX: int = foundMessage.lineControlPoints[0].x
        targetFreeX:  int = initialFreeX - 50
        eventHandler.OnBeginDragLeft(x=initialFreeX, y=MESSAGE_START_Y_1)
        eventHandler.OnDragLeft(draw=True, x=targetFreeX, y=MESSAGE_START_Y_1)
        eventHandler.OnEndDragLeft(x=targetFreeX, y=MESSAGE_START_Y_1)

        self.assertEqual(targetFreeX, foundMessage.lineControlPoints[0].x)

    def testLostMessageVerticalMovePreservesStretchedLength(self):
        inst1: UmlSDInstance = self._createSDInstance(name='inst1', x=INSTANCE_1_X)
        lifeLine: UmlSDLifeLine = inst1.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        lostMessage: UmlSDMessage = self._creationHandler.createLostMessage(
            startLifeLine=lifeLine,
            fromY=MESSAGE_START_Y_1,
            destX=lifeLineX + DEFAULT_LOST_FOUND_MESSAGE_LENGTH
        )
        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, lostMessage.GetEventHandler())

        initialFreeX: int = lostMessage.lineControlPoints[-1].x
        stretchedFreeX: int = initialFreeX + 70
        initialFromY: int = lostMessage.fromY
        eventHandler.OnBeginDragLeft(x=initialFreeX, y=initialFromY)
        eventHandler.OnDragLeft(draw=True, x=stretchedFreeX, y=initialFromY)
        eventHandler.OnEndDragLeft(x=stretchedFreeX, y=initialFromY)
        self.assertEqual(stretchedFreeX, lostMessage.lineControlPoints[-1].x)

        # Move vertically via message body drag
        bodyMidX: int = (lifeLineX + stretchedFreeX) // 2
        self._simulateVerticalDrag(
            eventHandler=eventHandler,
            startX=bodyMidX,
            startY=initialFromY,
            deltaY=MESSAGE_DRAG_DELTA
        )

        expectedY: int = initialFromY + self._preferences.timeStepHeight
        self.assertEqual(expectedY, lostMessage.fromY)
        self.assertEqual(expectedY, lostMessage.toY)
        self.assertEqual(lifeLineX, lostMessage.lineControlPoints[0].x)
        self.assertEqual(stretchedFreeX, lostMessage.lineControlPoints[-1].x)

    def testFoundMessageVerticalMovePreservesStretchedLength(self):
        inst2: UmlSDInstance = self._createSDInstance(name='inst2', x=INSTANCE_2_X)
        lifeLine: UmlSDLifeLine = inst2.umlSDLifeLine
        lifeLineX: int = round(lifeLine.GetX())

        foundMessage: UmlSDMessage = self._creationHandler.createFoundMessage(
            destLifeLine=lifeLine,
            toY=MESSAGE_START_Y_1,
            sourceX=lifeLineX - DEFAULT_LOST_FOUND_MESSAGE_LENGTH
        )
        eventHandler: UmlSDMessageEventHandler = cast(UmlSDMessageEventHandler, foundMessage.GetEventHandler())

        initialFreeX: int = foundMessage.lineControlPoints[0].x
        stretchedFreeX: int = initialFreeX - 60
        initialToY: int = foundMessage.toY
        eventHandler.OnBeginDragLeft(x=initialFreeX, y=initialToY)
        eventHandler.OnDragLeft(draw=True, x=stretchedFreeX, y=initialToY)
        eventHandler.OnEndDragLeft(x=stretchedFreeX, y=initialToY)
        self.assertEqual(stretchedFreeX, foundMessage.lineControlPoints[0].x)

        # Move vertically via message body drag
        bodyMidX: int = (stretchedFreeX + lifeLineX) // 2
        self._simulateVerticalDrag(
            eventHandler=eventHandler,
            startX=bodyMidX,
            startY=initialToY,
            deltaY=MESSAGE_DRAG_DELTA
        )

        expectedY: int = initialToY + self._preferences.timeStepHeight
        self.assertEqual(expectedY, foundMessage.toY)
        self.assertEqual(expectedY, foundMessage.fromY)
        self.assertEqual(stretchedFreeX, foundMessage.lineControlPoints[0].x)

        expectedDestX: int = lifeLineX

        execution: UmlSDExecution = foundMessage.execution  # type: ignore
        expectedDestX = round(execution.GetX() - (execution.GetWidth() / 2.0))

        self.assertEqual(expectedDestX, foundMessage.lineControlPoints[-1].x)

    def _simulateVerticalDrag(self, eventHandler: UmlSDMessageEventHandler, startX: int, startY: int, deltaY: int):
        eventHandler.OnBeginDragLeft(x=startX, y=startY)
        eventHandler.OnDragLeft(draw=True, x=startX, y=startY + deltaY)
        eventHandler.OnEndDragLeft(x=startX, y=startY + deltaY)

    def _getSingleCreatedMessage(self) -> UmlSDMessage:
        shapes: list[Shape] = self._diagramFrame.umlDiagram.GetShapeList()
        createdMessages: list[UmlSDMessage] = [s for s in shapes if isinstance(s, UmlSDMessage)]
        self.assertEqual(1, len(createdMessages))
        return createdMessages[0]

    def _assertMessageRenderingAndPixel(self, message: UmlSDMessage, circlePoint: Point, selected: bool, dc: MemoryDC, bitmap: Bitmap):
        dc.SelectObject(bitmap)
        message.Select(selected)
        message.OnDraw(dc)

        expectedPenColour:   Colour
        expectedBrushColour: Colour
        expectedRgbValue:    int
        if selected:
            expectedPenColour = ResourceUtils.redSolidPen().GetColour()
            expectedBrushColour = RED_BRUSH.GetColour()
            expectedRgbValue = 255
        else:
            expectedPenColour = ResourceUtils.blackSolidPen().GetColour()
            expectedBrushColour = BLACK_BRUSH.GetColour()
            expectedRgbValue = 0

        self.assertIsNotNone(message.messageLabel)
        self.assertEqual(expectedPenColour, message.GetPen().GetColour())
        self.assertEqual(expectedBrushColour, message.GetBrush().GetColour())

        dc.SelectObject(NullBitmap)
        renderedImage: Image = bitmap.ConvertToImage()
        self.assertEqual(expectedRgbValue, renderedImage.GetRed(circlePoint.x, circlePoint.y))
        self.assertEqual(0, renderedImage.GetGreen(circlePoint.x, circlePoint.y))
        self.assertEqual(0, renderedImage.GetBlue(circlePoint.x, circlePoint.y))

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
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDLostFoundMessage))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
