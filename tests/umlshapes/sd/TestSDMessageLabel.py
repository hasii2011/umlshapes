
from typing import cast

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.lib.ogl import OGLInitialize
from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.UmlSDMessageLabel import UmlSDMessageLabel
from umlshapes.sd.eventhandlers.UmlSDMessageLabelEventHandler import UmlSDMessageLabelEventHandler

TEST_INSTANCE_NAME: str = 'instance1'
INITIAL_FROM_Y:     int = 100
INITIAL_TO_Y:       int = 140
INSTANCE_DEFAULT_X: int = 100
INSTANCE_DEFAULT_Y: int = 50
DOUBLE_CLICK_X:     int = 125
DOUBLE_CLICK_Y:     int = 115


class SpyParentMessageHandler(ShapeEvtHandler):
    """
    Spy event handler to verify double click delegation from UmlSDMessageLabel.
    """

    def __init__(self, previousEventHandler: ShapeEvtHandler):
        super().__init__(prev=previousEventHandler)
        self.doubleClicked: bool = False
        self.lastX:         int = 0
        self.lastY:         int = 0

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        self.doubleClicked = True
        self.lastX = x
        self.lastY = y


class TestSDMessageLabel(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Message Label pub-sub engine wiring and event delegation.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._umlSDInstance: UmlSDInstance = self._createTestInstance()
        self._lifeLine:      UmlSDLifeLine = self._umlSDInstance.umlSDLifeLine

    def tearDown(self):
        self._diagramFrame.Destroy()
        super().tearDown()

    def testMessageLabelPubSubEngineWiredOnFrameAssignment(self):
        """
        Verify that setting umlFrame on UmlSDMessage wires umlPubSubEngine to the message label event handler.
        """
        umlSDMessage: UmlSDMessage       = self._createReflexiveMessage(lifeLine=self._lifeLine)
        messageLabel: UmlSDMessageLabel = umlSDMessage.messageLabel

        labelHandler: UmlSDMessageLabelEventHandler = messageLabel.GetEventHandler()
        self.assertIsInstance(labelHandler, UmlSDMessageLabelEventHandler)

        self.assertIsNotNone(labelHandler.umlPubSubEngine)
        self.assertIs(labelHandler.umlPubSubEngine, self._diagramFrame.umlPubSubEngine)

    def testMessageLabelRaisesIfPubSubEngineNotSet(self):
        """
        Verify that UmlSDMessageLabelEventHandler raises AssertionError if umlPubSubEngine is accessed before being set.
        """
        umlSDMessage: UmlSDMessage      = self._createReflexiveMessage(lifeLine=self._lifeLine)
        messageLabel: UmlSDMessageLabel = umlSDMessage.messageLabel

        labelHandler: UmlSDMessageLabelEventHandler = messageLabel.GetEventHandler()

        labelHandler._umlPubSubEngine = None
        with self.assertRaises(AssertionError):
            # Access the @property getter (assigning to _ so linters/IDEs do not warn
            # about a statement with no effect) to trigger the fail-fast assert in
            # UmlBaseEventHandler.umlPubSubEngine.
            _ = labelHandler.umlPubSubEngine

    def testMessageLabelLeftClickPublishesSelectionEvent(self):
        """
        Verify that OnLeftClick on UmlSDMessageLabel sends UML_SHAPE_SELECTED through umlPubSubEngine.
        """
        umlSDMessage: UmlSDMessage      = self._createReflexiveMessage(lifeLine=self._lifeLine)
        messageLabel: UmlSDMessageLabel = umlSDMessage.messageLabel

        selectedShapes: list[Shape] = []

        def onShapeSelected(umlShape: object):
            selectedShapes.append(cast(Shape, umlShape))

        self._umlPubSubEngine.subscribe(
            messageType=UmlMessageType.UML_SHAPE_SELECTED,
            frameId=self._diagramFrame.id,
            listener=onShapeSelected
        )

        labelHandler: ShapeEvtHandler = messageLabel.GetEventHandler()
        labelHandler.OnLeftClick(x=DOUBLE_CLICK_X, y=DOUBLE_CLICK_Y, keys=0, attachment=0)

        self.assertEqual(len(selectedShapes), 1)
        self.assertIs(selectedShapes[0], messageLabel)

    def testMessageLabelDoubleClickDelegatesToParentMessage(self):
        """
        Verify that OnLeftDoubleClick on UmlSDMessageLabel delegates to the parent UmlSDMessage event handler.
        """
        umlSDMessage: UmlSDMessage      = self._createReflexiveMessage(lifeLine=self._lifeLine)
        messageLabel: UmlSDMessageLabel = umlSDMessage.messageLabel

        spyHandler: SpyParentMessageHandler = SpyParentMessageHandler(
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(spyHandler)

        labelHandler: ShapeEvtHandler = messageLabel.GetEventHandler()
        labelHandler.OnLeftDoubleClick(x=DOUBLE_CLICK_X, y=DOUBLE_CLICK_Y, keys=0, attachment=0)

        self.assertTrue(spyHandler.doubleClicked)
        self.assertEqual(spyHandler.lastX, DOUBLE_CLICK_X)
        self.assertEqual(spyHandler.lastY, DOUBLE_CLICK_Y)

    def _createTestInstance(
        self,
        name: str = TEST_INSTANCE_NAME,
        x:    int = INSTANCE_DEFAULT_X,
        y:    int = INSTANCE_DEFAULT_Y
    ) -> UmlSDInstance:

        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = name

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel
        )
        umlSDInstance.umlFrame = self._diagramFrame
        umlSDInstance.SetX(x)
        umlSDInstance.SetY(y)
        umlSDInstance.umlSDLifeLine.SetX(x)
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)

        return umlSDInstance

    def _createReflexiveMessage(
        self,
        lifeLine: UmlSDLifeLine,
        fromY:    int = INITIAL_FROM_Y,
        toY:      int = INITIAL_TO_Y
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
            messageType=SDMessageType.SYNCHRONOUS
        )

        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = fromY
        umlSDMessage.toY   = toY

        lifeLineX: int = round(lifeLine.GetX())
        umlSDMessage.setReflexiveMessagePoints(lifeLineX=lifeLineX, fromY=fromY, toY=toY)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)

        return umlSDMessage


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDMessageLabel))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
