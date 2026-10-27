from typing import cast

from unittest.mock import MagicMock
from unittest.mock import patch

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import CANCEL
from wx import ID_OK

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW
from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.Defaults import MIN_INSTANCE_WIDTH
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.sd.eventhandlers.UmlSdInstanceEventHandler import UmlSdInstanceEventHandler
from umlshapes.sd.UmlSDInstance import HANDLE_NAME_MIDDLE_LEFT
from umlshapes.sd.UmlSDInstance import HANDLE_NAME_MIDDLE_RIGHT
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDInstance import UmlSDInstance

DEFAULT_NAME:               str = 'Short'
LONG_NAME:                  str = 'VeryLongParticipantNameExceedingDefaultWidth'
EXTREMELY_LONG_NAME:        str = 'AnExtremelyLongParticipantNameRequiringEvenMoreHorizontalSpace'
TARGET_EXPANDED_WIDTH:      int = 220
CUSTOM_MANUAL_WIDTH:        int = 260
TOO_SMALL_WIDTH:            int = 25
AUTOFIT_ON_CP_COUNT:        int = 1
AUTOFIT_OFF_CP_COUNT:       int = 3
INITIAL_FRAME_Y:            int = 150


class TestSDInstanceNameResizing(UnitTestBaseW):
    """
    Unit tests for Sequence Diagram Instance Name auto-fitting, manual resizing,
    and interactive control point sizing based on preferences.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._preferences:     UmlPreferences       = UmlPreferences()
        self._saveAutoFit:     bool                 = self._preferences.autoFitInstanceWidth
        self._saveReFit:       bool                 = self._preferences.reFitExistingInstances
        self._preferences.autoFitInstanceWidth      = True
        self._preferences.reFitExistingInstances    = False
        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        self._preferences.autoFitInstanceWidth   = self._saveAutoFit
        self._preferences.reFitExistingInstances = self._saveReFit
        self._diagramFrame.Destroy()
        super().tearDown()

    def testAutoFitPreferenceDefaults(self):
        self.assertTrue(self._preferences.autoFitInstanceWidth)
        self.assertFalse(self._preferences.reFitExistingInstances)

    def testAutoFitEnabledHidesHorizontalControlPoints(self):
        self._preferences.autoFitInstanceWidth = True

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        umlSDInstance.MakeControlPoints()
        self.assertEqual(AUTOFIT_ON_CP_COUNT, len(umlSDInstance.controlPoints))

    def testAutoFitDisabledShowsHorizontalControlPoints(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        umlSDInstance.MakeControlPoints()
        self.assertEqual(AUTOFIT_OFF_CP_COUNT, len(umlSDInstance.controlPoints))

    def testAutoFitInitialWidth(self):
        self._preferences.autoFitInstanceWidth = True

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = LONG_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        defaultWidth: int = self._preferences.instanceDimensions.width
        self.assertGreater(umlSDInstance.instanceWidth, defaultWidth)
        self.assertEqual(umlSDInstance.instanceWidth, umlSDInstance.instanceName.width)
        self.assertEqual(umlSDInstance.instanceWidth, round(umlSDInstance.constrainingShape.GetWidth()))

    def testAutoFitDisabledUsesDefaultWidth(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = LONG_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        defaultWidth: int = self._preferences.instanceDimensions.width
        self.assertEqual(defaultWidth, umlSDInstance.instanceWidth)

    def testManualInstanceWidthProperty(self):
        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        lifelineCenterXBefore: float = umlSDInstance.umlSDLifeLine.GetX()

        umlSDInstance.instanceWidth = TARGET_EXPANDED_WIDTH
        self.assertEqual(TARGET_EXPANDED_WIDTH, umlSDInstance.instanceWidth)
        self.assertEqual(TARGET_EXPANDED_WIDTH, umlSDInstance.instanceName.width)
        self.assertEqual(TARGET_EXPANDED_WIDTH, round(umlSDInstance.constrainingShape.GetWidth()))

        lifelineCenterXAfter: float = umlSDInstance.umlSDLifeLine.GetX()
        self.assertAlmostEqual(lifelineCenterXBefore, lifelineCenterXAfter, places=1)

    def testManualInstanceWidthClampMinimum(self):
        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        umlSDInstance.instanceWidth = TOO_SMALL_WIDTH
        self.assertEqual(MIN_INSTANCE_WIDTH, umlSDInstance.instanceWidth)

    def testInteractiveSizingMiddleRightHandleWhenAutoFitDisabled(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        eventHandler: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=umlSDInstance,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDInstance.GetEventHandler()
        )
        umlSDInstance.SetEventHandler(eventHandler)

        umlSDInstance.MakeControlPoints()
        controlPoints: list[ControlPoint] = umlSDInstance.controlPoints
        self.assertEqual(AUTOFIT_OFF_CP_COUNT, len(controlPoints))

        rightHandle: ControlPoint = controlPoints[HANDLE_NAME_MIDDLE_RIGHT]

        instanceCenterX: float = umlSDInstance.instanceName.GetX()
        lifelineCenterXBefore: float = umlSDInstance.umlSDLifeLine.GetX()

        startX: int = round(rightHandle.GetX())
        startY: int = round(rightHandle.GetY())
        dragTargetX: int = round(instanceCenterX + 100.0)

        eventHandler.OnSizingBeginDragLeft(pt=rightHandle, x=startX, y=startY)
        eventHandler.OnSizingDragLeft(pt=rightHandle, draw=False, x=dragTargetX, y=INITIAL_FRAME_Y)
        eventHandler.OnSizingEndDragLeft(pt=rightHandle, x=dragTargetX, y=INITIAL_FRAME_Y)

        expectedWidth: int = 200
        self.assertEqual(expectedWidth, umlSDInstance.instanceWidth)

        lifelineCenterXAfter: float = umlSDInstance.umlSDLifeLine.GetX()
        self.assertAlmostEqual(lifelineCenterXBefore, lifelineCenterXAfter, places=1)

    def testInteractiveSizingMiddleLeftHandleWhenAutoFitDisabled(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        eventHandler: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(
            umlSdInstance=umlSDInstance,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDInstance.GetEventHandler()
        )
        umlSDInstance.SetEventHandler(eventHandler)

        umlSDInstance.MakeControlPoints()
        controlPoints: list[ControlPoint] = umlSDInstance.controlPoints
        self.assertEqual(AUTOFIT_OFF_CP_COUNT, len(controlPoints))

        leftHandle: ControlPoint = controlPoints[HANDLE_NAME_MIDDLE_LEFT]

        instanceCenterX: float = umlSDInstance.instanceName.GetX()
        startX: int = round(leftHandle.GetX())
        startY: int = round(leftHandle.GetY())
        dragTargetX: int = round(instanceCenterX - 90.0)

        eventHandler.OnSizingBeginDragLeft(pt=leftHandle, x=startX, y=startY)
        eventHandler.OnSizingDragLeft(pt=leftHandle, draw=False, x=dragTargetX, y=INITIAL_FRAME_Y)
        eventHandler.OnSizingEndDragLeft(pt=leftHandle, x=dragTargetX, y=INITIAL_FRAME_Y)

        expectedWidth: int = 180
        self.assertEqual(expectedWidth, umlSDInstance.instanceWidth)

    def testRenameAutoFitWhenEnabled(self):
        self._preferences.autoFitInstanceWidth = True

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        initialWidth: int = umlSDInstance.instanceWidth

        sdModel.instanceName = EXTREMELY_LONG_NAME
        umlSDInstance.instanceName.sdInstance = sdModel

        self.assertGreater(umlSDInstance.instanceName.width, initialWidth)

    def testRenamePreservesManualWidthWhenAutoFitDisabled(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        umlSDInstance.instanceWidth = CUSTOM_MANUAL_WIDTH

        sdModel.instanceName = EXTREMELY_LONG_NAME
        umlSDInstance.instanceName.sdInstance = sdModel

        self.assertEqual(CUSTOM_MANUAL_WIDTH, umlSDInstance.instanceWidth)

    def testReFitAllInstancesWidthOnFrame(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = LONG_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        defaultWidth: int = self._preferences.instanceDimensions.width
        self.assertEqual(defaultWidth, umlSDInstance.instanceWidth)

        # Re-fitting updates the width to match the name
        self._diagramFrame.reFitAllInstancesWidth()
        self.assertGreater(umlSDInstance.instanceWidth, defaultWidth)

    def testDoubleClickInstanceNameRenamesAndAutoFitsWhenAutoFitOn(self):
        self._preferences.autoFitInstanceWidth = True

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        initialWidth: int = umlSDInstance.instanceWidth

        mockDlg: MagicMock = MagicMock()
        mockDlg.ShowModal.return_value = ID_OK
        mockDlg.instanceName = LONG_NAME
        mockDlg.__enter__.return_value = mockDlg

        with patch('umlshapes.dialogs.DlgEditInstanceName.DlgEditInstanceName', return_value=mockDlg):
            instanceNameShape: UmlInstanceName = umlSDInstance.instanceName
            instanceNameShape.GetEventHandler().OnLeftDoubleClick(100, 100)

        self.assertEqual(LONG_NAME, umlSDInstance.sdInstance.instanceName)
        self.assertEqual(LONG_NAME, instanceNameShape.instanceName)
        self.assertGreater(umlSDInstance.instanceWidth, initialWidth)
        self.assertTrue(self._diagramFrame.frameModified)

    def testDoubleClickInstanceNameRenamesAndPreservesWidthWhenAutoFitOff(self):
        self._preferences.autoFitInstanceWidth = False

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame
        umlSDInstance.instanceWidth = CUSTOM_MANUAL_WIDTH

        mockDlg: MagicMock = MagicMock()
        mockDlg.ShowModal.return_value = ID_OK
        mockDlg.instanceName = LONG_NAME
        mockDlg.__enter__.return_value = mockDlg

        with patch('umlshapes.dialogs.DlgEditInstanceName.DlgEditInstanceName', return_value=mockDlg):
            instanceNameShape: UmlInstanceName = umlSDInstance.instanceName
            instanceNameShape.GetEventHandler().OnLeftDoubleClick(100, 100)

        self.assertEqual(LONG_NAME, umlSDInstance.sdInstance.instanceName)
        self.assertEqual(LONG_NAME, instanceNameShape.instanceName)
        self.assertEqual(CUSTOM_MANUAL_WIDTH, umlSDInstance.instanceWidth)

    def testDoubleClickInstanceNameCanceledPreservesNameAndWidth(self):
        self._preferences.autoFitInstanceWidth = True

        sdModel: SDInstance = SDInstance()
        sdModel.instanceName = DEFAULT_NAME

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.umlFrame = self._diagramFrame

        initialWidth: int = umlSDInstance.instanceWidth

        mockDlg: MagicMock = MagicMock()
        mockDlg.ShowModal.return_value = CANCEL
        mockDlg.instanceName = LONG_NAME
        mockDlg.__enter__.return_value = mockDlg

        with patch('umlshapes.dialogs.DlgEditInstanceName.DlgEditInstanceName', return_value=mockDlg):
            instanceNameShape: UmlInstanceName = umlSDInstance.instanceName
            instanceNameShape.GetEventHandler().OnLeftDoubleClick(100, 100)

        self.assertEqual(DEFAULT_NAME, umlSDInstance.sdInstance.instanceName)
        self.assertEqual(initialWidth, umlSDInstance.instanceWidth)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDInstanceNameResizing))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
