from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW
from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import OGLInitialize

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from umlshapes.sd.UmlSDInstance import UmlSDInstance

INITIAL_LIFELINE_LENGTH: int = 360
NEW_LIFELINE_LENGTH:     int = 500
TOO_SHORT_LENGTH:        int = 20
EXPECTED_MIN_LENGTH:     int = 80


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
        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        self._diagramFrame.Destroy()
        super().tearDown()

    def testLifeLinePreferencesDefaults(self):
        preferences: UmlPreferences = self._preferences

        self.assertTrue(preferences.autoGrowLifeLines)
        self.assertTrue(preferences.uniformLifeLineLength)

    def testLifeLineLengthModification(self):
        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = 'testInstance'

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

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
        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = 'testInstanceMin'

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        umlSDInstance.setLifeLineLength(newLength=TOO_SHORT_LENGTH)
        self.assertEqual(EXPECTED_MIN_LENGTH, umlSDInstance.getLifeLineLength())

    def testMakeControlPoints(self):
        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = 'testInstanceCP'

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        umlSDInstance.MakeControlPoints()
        self.assertEqual(1, len(umlSDInstance.controlPoints))

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
        sdModel1: SDInstance = SDInstance()
        sdModel1.instanceName = 'instance1'
        umlSDInstance1: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel1,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        sdModel2: SDInstance = SDInstance()
        sdModel2.instanceName = 'instance2'
        umlSDInstance2: UmlSDInstance = UmlSDInstance(
            sdInstance=sdModel2,
            diagramFrame=self._diagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )

        self._diagramFrame.umlDiagram.AddShape(umlSDInstance1)
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance2)

        instances: list[UmlSDInstance] = self._diagramFrame.getSDInstances()
        self.assertEqual(2, len(instances))

        self._diagramFrame.setAllLifeLinesLength(length=NEW_LIFELINE_LENGTH)

        self.assertEqual(NEW_LIFELINE_LENGTH, umlSDInstance1.getLifeLineLength())
        self.assertEqual(NEW_LIFELINE_LENGTH, umlSDInstance2.getLifeLineLength())


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDLifeLineResizing))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
